import re
from typing import List

import nltk
import numpy as np
import requests
from bs4 import BeautifulSoup, Tag
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from Searchers import Searcher

# This package is needed to use the tokenize functions from nltk
nltk.download("punkt")


class Scraper:
    """
    A simple web-scraper interface
    """

    def get_soup(self, url: str, getter=requests.get) -> BeautifulSoup:
        raise NotImplementedError


class SimpleWebScraper(Scraper):
    """
    A simple web-scraper that requests into a URL and returns a BS soup from the page
    """

    def __init__(self, parser: str = "html.parser"):
        self.parser = parser

    def get_soup(self, url: str, getter=requests.get) -> BeautifulSoup:
        """
        Returns a BeautifulSoup object to be used on the next steps
        :param url: URL to extract the info from
        :param getter: Which function to use for requesting
        :return: Soup containing web info
        """
        response = getter(url)
        response.raise_for_status()

        return BeautifulSoup(response.text, self.parser)


class TextSummariser:
    """
    Base interface for a text summariser. They receive a soup, from the webscraper and then return a summary of the text
    inside the website, that is the most relevant to the user, given his query.
    """

    def __init__(self):
        self.soup = None
        self.query = None

    def summarise(self, soup: BeautifulSoup, query: str) -> str:
        raise NotImplementedError


class CosineTag:
    """
    Object to return a pair of the original text of the webpage, and the preprocessed version of this text
    """

    def __init__(self, original, preprocessed):
        self.original = original
        self.preprocessed = preprocessed


class CosineSummariser(TextSummariser):
    """
    CosineSummariser, computes similarity of the documents (in this case, tags in the web page), representing them as
    tfidf vectors.
    """

    def __init__(self):
        super().__init__()
        self.tags = []

    def summarise(self, soup: BeautifulSoup, query: str) -> Tag:
        """
        Consider the text inside each tag as the document. Preprocess the text, removing whitespace and non-letters
        chars. Create a corpus of every tag, and calculate the tfidf vector. Use the created vector to calculate the
        distance between the text inside the tag, and the original user query. The tag with the highest similarity is
        returned as the text insight for the user query.
        :param soup: BeautifulSoup object received from the scraper
        :param query: Original user query
        :return: Summary for the given soup
        """
        self.soup = soup
        self.query = query
        tag: Tag
        for tag in self.soup():
            self.tags.append(CosineTag(tag, self.preprocess(tag.get_text().lower())))

        training_data = [tag.preprocessed for tag in self.tags]
        vectorizer = TfidfVectorizer(use_idf=False)
        tfidf = vectorizer.fit_transform(training_data)
        tfidf_query = vectorizer.transform([self.preprocess(self.query)])

        # this is faster than using cosine_similarity
        # Reference : https://scikit-learn.org/stable/modules/metrics.html#cosine-similarity
        cosine_similarity = linear_kernel(tfidf_query, tfidf).flatten()
        return self.tags[np.argmax(cosine_similarity)].original

    def preprocess(self, text) -> str:
        """
        Removes non letters chars
        :param text: Text to process
        :return: processed text
        """
        formatted_text = re.sub('[^a-zA-Z]', ' ', text)
        return re.sub(r'\s+', ' ', formatted_text)


class SentenceSummariser(TextSummariser):
    """
    * NOTE: This is a naive implementation of a sentence summariser, it should not be used, it is here only to the sole
    purpose of demonstrating how it is possible to extend the current API to use another summariser and give other
    results to the text insight.
    """

    def __init__(self, pre: int = 5, pos: int = 5):
        super().__init__()
        self.text = ""
        self.summary = ""
        self.pre = pre
        self.pos = pos

    def summarise(self, soup: BeautifulSoup, query: str) -> str:
        """
        The sentence summarizer works as follows: Tokenize each sequence in the text of the webpage, using sent_tokenize
        from nltk. For each sentence, iterate through each word, and once we find a word that belonged to the user original
        query, we append to the summary `pre` words, which defaults to 5, that came before the first word we found, and
        append `pos` words after, which also defaults to five. If during the appending of the `pos` words we get to
        encounter another word belonging to the original user query, we add + `pos` words, and double the value of words in
        the `pos`. That is because, the more words we find belonging to the query, the more relevant the sentence is. So
        this is a basic heuristic to return some summary.
        :param soup: BeautifulSoup object received from the scraper
        :param query: Original user query
        :return: Summary for the given soup
        """
        self.text = soup.text.lower()
        self.text = re.sub("[\t\n\r\f\v]+", '\n', self.text)
        self.text = re.sub("[ ]{2,}", '\n', self.text)
        self.text = re.sub("[.]{2,}", "", self.text)
        self.query = query
        self.soup = soup
        query_tokens = self.get_as_tokens(self.query)
        sentences = nltk.sent_tokenize(self.text)
        for sentence in sentences:
            words = nltk.word_tokenize(sentence)
            pos = 0
            for i, word in enumerate(words):
                if word in query_tokens:
                    if pos == 0:
                        self.add_retroactively(self.pre, words, i)
                        pos = self.pos
                    else:
                        pos += self.pos
                        pos *= 2
                    self.summary += " " + word
                elif pos > 0:
                    pos -= 1
                    self.summary += " " + word

        return self.summary

    def add_retroactively(self, count, tokens, i):
        """
        Add to the summary the last `count` words from the tokens
        :param count: how many words to add retroactively
        :param tokens: the list of tokens
        :param i: pointer to the actual token
        """
        self.summary += "\n[...]" + " ".join([tokens[i] for i in range(max(i - count, 0), i)])

    def get_as_tokens(self, text: str) -> List[str]:
        """
        Preprocess the text, and return it as a list of tokens
        :param text: text to process
        :return: List containing each token
        """
        alphanum_text = re.sub("[^0-9a-zA-Z]+", " ", text)
        return alphanum_text.split(" ")


class Summary:
    """
    Base object to hold the result of a summary, which includes the summary of the webpage, and its url
    """

    def __init__(self, summary: str, url: str):
        self.summary = summary
        self.url = url


class TextInsight:
    """
    Class that unites every part of the text insight API, it calls every needed method that are available on the
    searcher, scraper and summariser and returns a list with the Summary object for each page
    """

    def __init__(self, searcher: Searcher, scraper: Scraper, summariser: TextSummariser):
        self.searcher = searcher
        self.scraper = scraper
        self.summariser = summariser

    def get(self, query: str, getter=requests.get) -> List[Summary]:
        """
        Performs the text insight collection, given the set of searcher, scraper and summariser given. This is done so
        any of those are swappable to a new/different version of each.
        :param getter: Getter function to request to webpage on scraper
        :param query: Original user query
        :return: List containing summarisation of the first n responses of a search in a web engine
        """
        query = query.lower()
        summary_list = []
        self.searcher.search(query)
        for url in self.searcher.urls:
            soup = self.scraper.get_soup(url, getter)
            summary = self.summariser.summarise(soup, query)
            summary_list.append(Summary(summary, url))
        return summary_list
