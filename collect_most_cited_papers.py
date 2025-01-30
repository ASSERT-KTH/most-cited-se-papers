#!/usr/bin/python3
"""
Scholar Paper Citation Collector and Analyzer

This program collects and analyzes academic paper citations from major software engineering venues.
It uses the Semantic Scholar and Crossref APIs to gather citation data and ranks papers by their
impact.

Features:
- Fetches paper metadata from Crossref API
- Retrieves citation counts from Semantic Scholar API
- Caches results to avoid redundant API calls
- Ranks papers by citation count
- Supports multiple major SE venues (ICSE, TSE, FSE, etc.)
- Handles conference name variations over time

Dependencies:
    - requests: For API calls
    - json: For data serialization
    - config.py: Contains API keys (not included)

Usage:
    Direct execution:
        python collect-most-cited-papers.py
    
    Import as module:
        from collect-most-cited-papers import get_papers, get_ranked_papers

Cache Structure:
    cache/
        citations/     # Semantic Scholar API responses
        crossref/     # Crossref API responses
        ranks/        # Generated ranking files


Author: Martin Monperrus
Date: January 2025
"""

import requests
import json
import config
import os

def get_semanticscholar_citations(paper_id):
    """Retrieve citation count for a paper from Semantic Scholar API.
    
    Args:
        paper_id (str): DOI or Semantic Scholar paper ID
        
    Returns:
        dict: Paper data including citation count and embeddings
        Cached results are returned if available
    """
    fname = "cache/citations/"+paper_id.replace("/","_")

    # Check if we have the data cached
    try:
        with open(fname, "r") as f:
            return json.load(f)        
    except FileNotFoundError:
        pass 

    # Get paper details including citation count
    #paper_id = resp["data"][0]["paperId"] 
    paper_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    params = "?fields=citationCount,embedding,embedding.specter_v2"
    
    semanticscholar_full = requests.get(
        paper_url + params,
        headers = {"x-api-key": config.semanticscholar_key}
    ).json()
    
    if "error" in semanticscholar_full:
        print(f"Error semanticscholar_full: {paper_id}")
        semanticscholar_full = {"citationCount": 0} 
    # print(json.dumps(semanticscholar_full, indent=2))
    # Combine response data

    if 'citationCount' not in semanticscholar_full:
        print(f"Error semanticscholar_full2: {paper_id} {json.dumps(semanticscholar_full, indent=2)}")
        semanticscholar_full['citationCount'] = 0

    data = semanticscholar_full
    # save in file
    with open(fname, "w") as f:
         json.dump(data, f, indent=2)

    return data

def get_icse_2022_papers():
    """Convenience function to get ICSE 2022 papers.
    
    Returns:
        list: Papers from ICSE 2022
    """
    return get_papers("International Conference on Software Engineering", 2022)

def date_mess(item):
    """Debug function to print various date fields from a Crossref item.
    
    Args:
        item (dict): Crossref API response item
    """
    print("issued", item["created"]["date-parts"][0])
    print("created", item["created"]["date-parts"][0])
    print("published", item["published"]["date-parts"][0])
    if "published-print" in item:
        print("published-print", item["published-print"]["date-parts"][0])

def get_papers(name, year):
    """Retrieve papers from a specific venue and year using Crossref API.
    
    Args:
        name (str): Publication venue name
        year (int): Publication year
        
    Returns:
        list: Papers with metadata and citation counts
        Results are cached in JSON files
    """
    fname = f"cache/crossref/{name}_{year}.json"
    try:
        with open(fname, "r") as f:
            data = json.load(f)
        if len(data) > 0:
            return data
    except FileNotFoundError:
        pass
    # print(fname)
    # Base URL for Crossref API
    url = "https://api.crossref.org/works"
    
    # Query parameters
    # query_filer = "pub" # sequencer returns 2021 for this
    query_filer = "issued"
    # from-created-date
    params = {
        "query.container-title": name,
        "filter": "from-"+query_filer+"-date:"+str(year)+",until-"+query_filer+"-date:"+str(year),
        "rows": 1000
        # "select": "title,author,DOI,container-title,created,,publication-date"
    }
    
    # Make request
    response = requests.get(url, params=params)
    data = response.json()
    assert response.status_code  == 200

    # print(data)
    # Process results
    papers = []
    
    prev = ""
    for item in data["message"]["items"]:
        if "title" not in item or "DOI" not in item:
            # print(item)
            # sometimes we have only {'DOI': '10.1145/3186333', 'container-title': ['ACM Computing Surveys']}
            continue
        container_title = item.get("container-title", [""])[0]
        # remove parentheses at the end of the title
        container_title = container_title.split("(")[0].strip() 
        # print(item["container-title"])
        # print(container_title)
        if not container_title.lower().endswith(name.lower()):
            continue
        if "breaker page".lower() in container_title.lower():
            continue
        # hack to filte ESEM
        if "measurement".lower() in container_title.lower():
            continue
        if "software engineering".lower() == container_title.lower():
            continue
        # hack to filter workshops
        if "companion".lower() in container_title.lower():
            continue

        # print(item)
        if item["type"] == "proceedings-article":
            # print(year)
            
            # print(item["published"]["date-parts"][0][0], year)
            assert item["published"]["date-parts"][0][0] == year, date_mess(item)
        if item["type"] == "journal-article":
            # mess
            # print(year)
            # date_mess(item)
            # print(item["created"]["date-parts"][0])
            assert item[query_filer]["date-parts"][0][0] == year, date_mess(item)

        # print(container_title)
        if container_title != prev:
            if prev != "":
                # we change publication
                continue
            print(container_title)
        # print(json.dumps(item, indent=2))
        prev = container_title
        citations = get_semanticscholar_citations("doi:"+item["DOI"])
        # print(citations.keys())
        if "embedding" in citations: del citations["embedding"]
        citations["source"] = "semanticscholar"
        paper = {
            "title": item["title"][0],
            "authors": [author.get("given", "") + " " + author.get("family", "") 
                        for author in item.get("author", [])],
            "doi": item.get("DOI", ""),
            "venue": container_title,
            "citations": citations,
            "year": year
        }

        papers.append(paper)
    
    # # Print results
    for paper in papers:
       if "citationCount" not in paper['citations']:
           print(f"Title: {paper}")
    #    print(f"Title: {paper['title']} {paper['citations']['citationCount']} citations")
       pass
    
    # save
    with open(fname, "w") as f:
        json.dump(papers, f, indent=2)

    print(name, prev, year)

    return papers

def get_ranked_papers(name, year, n):
    """Get papers sorted by citation count and save ranking.
    
    Args:
        name (str): Publication venue name
        year (int): Publication year
        n (int): Index number for output file
        
    Returns:
        tuple: (sorted_papers, filename)
        Papers are sorted by citations in descending order
    """
    papers = get_papers(name, year)
    # print(f"Found {len(papers)} papers for {name} {year}")
    sorted_papers = [x for x in enumerate(sorted(papers, 
                         key=lambda p: p['citations']['citationCount'], reverse=True) , 1)]
    # n on three digits
    nwdigits = str(n).zfill(3)
    fname = f"cache/ranks/{nwdigits} {name} {year}.json".replace(" ", "-")
    # assert len(sorted_papers) > 0, f"no data for {name} {year}"
    with open(fname, "w") as f:
        json.dump(sorted_papers, f, indent=2)
    return sorted_papers, fname


def firsttry():
    """Initial implementation for collecting top SE venue papers.
    
    Processes papers from 2015-2024 for:
    - ICSE
    - TSE 
    - JSS
    - EMSE
    - FSE
    """
    n=0
    for i in range(2015,2024):
        n+=1
        # print(i)
        get_ranked_papers("International Conference on Software Engineering", i, n )
        n+=1
        get_ranked_papers("IEEE Transactions on Software Engineering", i, n)
        n+=1

def get_fse_name(year):
    """Get the correct FSE conference name for a given year.
    
    The conference name changed over time and alternates between 
    FSE and ESEC/FSE formats.
    
    Args:
        year (int): Conference year
        
    Returns:
        str: Full conference name for that year
    """
    # if odd year, it's FSE
    if year % 2 == 0:
        if year < 2018:
            return "Symposium on Foundations of Software Engineering"
        else:
            return "Symposium on the Foundations of Software Engineering"
    else:
        if year < 2018:
            return "Meeting on Foundations of Software Engineering"
        else:
            return "European Software Engineering Conference and Symposium on the Foundations of Software Engineering"
            return "Meeting on European Software Engineering Conference"
            
def top8_2013_2023():
    """Collect and rank papers from top 8 SE venues 2013-2023.
    
    Processes papers from:
    - ICSE
    - TSE
    - JSS
    - IST
    - EMSE
    - FSE/ESEC
    - ASE
    
    Creates ranked lists in cache/ranks/
    """
    # save all TSE
    n=0
    for i in range(2013,2023+1):
        n+=1
        print(n)
        get_ranked_papers("International Conference on Software Engineering", i, n)
        n+=1
        get_ranked_papers("IEEE Transactions on Software Engineering", i, n)
        n+=1
        get_ranked_papers("Journal of Systems and Software", i, n)
        n+=1
        # missing 4: Proceedings of the ACM on Programming Languages
        get_ranked_papers("Information and Software Technology", i, n)
        n+=1
        get_ranked_papers("Empirical Software Engineering", i, n)
        n+=1
        fse, fname = get_ranked_papers(get_fse_name(i), i, n)
        if len(fse) == 0:
            raise Exception(f"No data for FSE {i}")
            fse, fname = get_ranked_papers("Foundations of Software Engineering", i, n)
            # print(fse[0][1]['title'])
        n+=1
        get_ranked_papers("International Conference on Automated Software Engineering",i, n)
        
        n+=1
        get_ranked_papers("ACM Transactions on Software Engineering and Methodology", i, n)
        
    # papers = get_papers("Computing Surveys", 2018)
    # get_monperrus_paper_rank(papers)


    # print(f"\nFound {len(papers)}")

if __name__ == "__main__":

    top8_2013_2023()
