from googlesearch import search


class Searcher:
    """
    Searcher is a base class for all searchers, it has a method search, which will populate a list of urls, that can be
    then queried for its results.

    If needed, one can extend this to perform searches on other engines too.
    """

    def __init__(self, n_results: int = 5):
        """
        Initialises the Searcher class, storing the amount of results needed and the URLS in a list.
        :param n_results: Number of results to get the URL
        """
        self.urls = []
        self.n_results = n_results
        self.query = ""

    def search(self, query: str):
        """
        Perform a search on the given platform given the query, and populate the list of URLs.
        """
        raise NotImplementedError


class GoogleSearcher(Searcher):
    """
    Implementation of the searcher on the Google web search engine. The search is made with the python binding of Google
    web search, more info here : https://pypi.org/project/google/
    """
    def __init__(self):
        super().__init__()

    def search(self, query: str, searcher=search):
        """
        Calls to the python binding to google search and performs a search using the given parameters
        :param query: Original user query
        :param searcher: which function to use to search the web
        """
        self.query = query

        assert self.query is not None and self.query != "", "Query should not be empty"
        assert isinstance(self.query, str), "Query should be a string"
        self.urls = [url for url in searcher(self.query, stop=self.n_results)]
