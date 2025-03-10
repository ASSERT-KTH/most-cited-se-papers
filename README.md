# Most Cited Papers in Software Engineering

A systematic analysis of the most cited papers in software engineering from 2013-2023, based on data from CrossRef and Semantic Scholar APIs.

If you use this data, please cite the paper [Most Cited Papers in Software Engineering 2013-2023](https://zenodo.org/records/14885766/files/main.pdf):

```bibtex
@techreport{mostcitedse20132023,
  title= {Most Cited Papers in Software Engineering 2013-2023},
  author= {Martin Monperrus},
  year = {2025},
  number = {14885766},
  institution = {Zenodo},
  url = {https://zenodo.org/records/14885766/files/main.pdf},
  doi = {https://doi.org/10.5281/zenodo.14885765}
}
```

Martin Monperrus, KTH Royal Institute of Technology
Jan 2025

## Overview

This repository contains:
- Scripts for collecting and analyzing citation data
- Citation rankings for major software engineering venues

## Repository Structure

```
.
├── collect_most_cited_papers.py  # Main data collection 
├── cache/ (.gitignore)
│   ├── citations/     # Semantic Scholar API responses
│   ├── crossref/     # CrossRef API responses
│   └── ranks/        # Generated ranking files
```

## Usage

Dependencies:

- Python 3.x
- requests


1. Set up API keys:
```python
# config.py
semanticscholar_key = "your_key_here"
```

2. Collect citation data:
```bash
python3 collect_most_cited_papers.py
```

## Covered Venues in the Jan 2025 extraction

- International Conference on Software Engineering (ICSE)
- IEEE Transactions on Software Engineering (TSE)
- Journal of Systems and Software (JSS)
- Information and Software Technology (IST)
- Empirical Software Engineering (EMSE)
- Foundations of Software Engineering (FSE/ESEC)
- Automated Software Engineering (ASE)
- ACM Transactions on Software Engineering and Methodology (TOSEM)

## License

This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png

