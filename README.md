#### How this code is organized

There are 4 files that implement functions and classes, they are:

* DataScraper.py: Implements most of the classes and the solution for the third task, that scrapes the web, and returns
a summary of the top 5 pages from google, that is relevant to the query of the user. 
 
* OverlappingLines.py: Implements the solution for the first task, checking whether two lines overlap or not. 
There is also another function that checks if any set of lines do have a overlap, so the user can input N lines
and expect True if they overlap, False otherwise.
 
* Searchers.py: Class implementation for the GoogleSearcher, can be easily extended to include other search engines.

* VersionString.py: Implementation for the second task, to check that given two version strings, check if the first is
equal, higher or lower than the second.

Also, there is a fifth file, called `sergio_marques_test.py`, which has all the tests for all the classes
and functions for the four files above. It uses unittesting and can by run by issuing `python sergio_marques_test.py`.

#### Requirements

Code was tested on Python 3.7, the libraries used are:
```
google:2.0.2 -> https://pypi.org/project/google/
requests-mock:1.5.2 -> https://pypi.org/project/requests-mock/
beautifulsoup4:4.6.3 -> https://pypi.org/project/beautifulsoup4/
nltk:3.4 -> https://pypi.org/project/nltk/
numpy:1.15.4 -> https://pypi.org/project/numpy/
scikit-learn:0.20.1 -> https://pypi.org/project/scikit-learn/
```