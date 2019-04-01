import unittest
from unittest.mock import MagicMock

import googlesearch
import requests
import requests_mock

from DataScraper import SimpleWebScraper, CosineSummariser, SentenceSummariser, TextInsight
from OverlappingLines import Line, two_lines_overlap, lines_overlap
from Searchers import GoogleSearcher, Searcher
from VersionString import compare_version_strings


class TestingLineCreation(unittest.TestCase):
    def test_line_creation(self):
        line1 = Line(1, 5)
        self.assertEqual(line1.x1, 1)
        self.assertEqual(line1.x2, 5)

        # inverted creation
        line1 = Line(7, 5)
        self.assertEqual(line1.x1, 5)
        self.assertEqual(line1.x2, 7)

        # Floating point
        line1 = Line(2.9, 2.901)
        self.assertEqual(line1.x1, 2.9)
        self.assertEqual(line1.x2, 2.901)

    def test_invalid_line_creation(self):
        self.assertRaises(RuntimeError, Line, "a", "b")
        self.assertRaises(RuntimeError, Line, 3, "4")
        self.assertRaises(RuntimeError, Line, "3", 2)


class TestOverlappingLines(unittest.TestCase):
    def test_overlapping_two_lines(self):
        # base example
        line1 = Line(1, 5)
        line2 = Line(0, 3)
        self.assertTrue(two_lines_overlap(line1, line2))

        # negative and inverted line creation
        line1 = Line(-5, -7)
        line2 = Line(-5, -2)
        self.assertTrue(two_lines_overlap(line1, line2))

        # using float instead of ints
        line1 = Line(5.1, 6.99)
        line2 = Line(6.99, 7.0)
        self.assertTrue(two_lines_overlap(line1, line2))

    def test_non_overlapping_two_lines(self):
        # base example
        line1 = Line(1, 3)
        line2 = Line(4, 5)
        self.assertFalse(two_lines_overlap(line1, line2))

        # Inverted line creation
        line1 = Line(99, 5)
        line2 = Line(4, 1)
        self.assertFalse(two_lines_overlap(line1, line2))

        # Using float
        line1 = Line(1.25, 3.99)
        line2 = Line(3.9901, 5)
        self.assertFalse(two_lines_overlap(line1, line2))

    def test_overlapping_lines(self):
        line1 = Line(1, 2)
        line2 = Line(3, 4)
        line3 = Line(5, 6)
        line4 = Line(6, 7)
        self.assertTrue(lines_overlap(line1, line2, line3, line4))

        line1 = Line(1.5, 2.5)
        line2 = Line(3.5, 4.5)
        line3 = Line(5.5, 6.5)
        line4 = Line(6.5, 7.5)
        self.assertTrue(lines_overlap(line1, line2, line3, line4))

    def test_non_overlapping_lines(self):
        line1 = Line(1, 2)
        line2 = Line(3, 4)
        line3 = Line(5, 6)
        line4 = Line(7, 8)
        self.assertFalse(lines_overlap(line1, line2, line3, line4))

        line1 = Line(1.5, 2.5)
        line2 = Line(3.5, 4.5)
        line3 = Line(5.5, 6.5)
        line4 = Line(7.5, 8.5)
        self.assertFalse(lines_overlap(line1, line2, line3, line4))


class TestVersionString(unittest.TestCase):
    def test_valid_strings(self):
        string1 = "2.0.1"
        string2 = "3.9.1"
        # smaller
        self.assertEqual(compare_version_strings(string1, string2), -1)

        string1 = "5.00.21"
        string2 = "05.00.021"
        # equals
        self.assertEqual(compare_version_strings(string1, string2), 0)

        string1 = "0.0.100"
        string2 = "0.0.021"
        # higher
        self.assertEqual(compare_version_strings(string1, string2), 1)

        string1 = "0.10"
        string2 = "0.0.0.5"
        self.assertEqual(compare_version_strings(string1, string2), 1)

        string1 = "00.25.32.9"
        string2 = "0.25"
        self.assertEqual(compare_version_strings(string1, string2), 1)

        string1 = "00.025.32.9"
        string2 = "0.25.32.09.1"
        self.assertEqual(compare_version_strings(string1, string2), -1)

        # should also work with any separator
        string1 = "5,5"
        string2 = "5,2"
        self.assertEqual(compare_version_strings(string1, string2, sep=','), 1)

        # Even different separators
        string1 = "5,5"
        string2 = "9.2"
        self.assertEqual(compare_version_strings(string1, string2, sep=',', sep2='.'), -1)

    def test_invalid_strings(self):
        self.assertRaises(AttributeError, compare_version_strings, 3.9, 4.2)
        self.assertRaises(AttributeError, compare_version_strings, 3, 4)
        self.assertRaises(ValueError, compare_version_strings, "-2.0", "5.1.0")
        self.assertRaises(ValueError, compare_version_strings, "2.0.55", "5.1.0.-9")


class TestSearcher(unittest.TestCase):
    def test_search(self):
        urls = [
            "http://www.google.com/",
            "http://www.facebook.com/",
            "http://www.twitter.com/",
            "http://www.amazon.com/",
            "http://www.oracle.com/"
        ]
        thing = googlesearch
        thing.search = MagicMock(return_value=urls)
        searcher = GoogleSearcher()
        searcher.search("query", searcher=thing.search)
        self.assertEqual(searcher.urls, urls)


class TestWebScraper(unittest.TestCase):
    def test_web_scraper(self):
        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount('mock', adapter)
        adapter.register_uri(method="GET", url="mock://anyurl.com", text="<html>"
                                                                         "<p>This webpage is used for testing</p>"
                                                                         "<p>probably, it wouldn't do much if you "
                                                                         "render it on a browser, though you can still "
                                                                         "see the webpage</p>"
                                                                         "</html>")
        scraper = SimpleWebScraper()
        soup = scraper.get_soup("mock://anyurl.com", session.get)

        p_list = [p for p in soup.find_all('p')]
        self.assertTrue(len(p_list) is 2)
        self.assertEqual(p_list[0].text, "This webpage is used for testing")


class TestTextSummariser(unittest.TestCase):
    def test_cosine_summariser(self):
        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount('mock', adapter)
        adapter.register_uri(method="GET", url="mock://anyurl.com", text="<html>"
                                                                         "<p>This webpage is used for testing</p>"
                                                                         "<p>probably, it wouldn't do much if you "
                                                                         "render it on a browser, though you can still "
                                                                         "see the webpage</p>"
                                                                         "</html>")
        scraper = SimpleWebScraper()
        soup = scraper.get_soup("mock://anyurl.com", session.get)

        cosine_summariser = CosineSummariser()
        summary = cosine_summariser.summarise(soup, "render it on a browser")
        self.assertEqual(summary.text, "probably, it wouldn't do much if you render it on a browser, though you can "
                                       "still see the webpage")

    def test_sentence_summariser(self):
        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount('mock', adapter)
        adapter.register_uri(method="GET", url="mock://anyurl.com", text="<html>"
                                                                         "<p>This webpage is used for testing</p>"
                                                                         "<p>probably, it wouldn't do much if you "
                                                                         "render it on a browser, though you can still "
                                                                         "see the webpage</p>"
                                                                         "</html>")
        scraper = SimpleWebScraper()
        soup = scraper.get_soup("mock://anyurl.com", session.get)

        sentence_summariser = SentenceSummariser()
        summary = sentence_summariser.summarise(soup, "much")
        self.assertEqual(summary, "\n[...], it would n't do much if you render it on")


class TestTextInsight(unittest.TestCase):
    def test_text_insighter(self):
        searcher = Searcher()
        searcher.search = MagicMock()
        searcher.urls = [
            "mock://aurl.com",
            "mock://myurl.com",
            "mock://theurl.com",
            "mock://anyurl.com",
            "mock://anurl.com"
        ]

        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount('mock', adapter)
        adapter.register_uri(method="GET", url="mock://aurl.com", text="<html>"
                                                                       "<p>This webpage is used for testing</p>"
                                                                       "<p>probably, it wouldn't do much if you "
                                                                       "render it on a browser, though you can still "
                                                                       "see the webpage</p>"
                                                                       "</html>")
        adapter.register_uri(method="GET", url="mock://myurl.com")
        adapter.register_uri(method="GET", url="mock://theurl.com")
        adapter.register_uri(method="GET", url="mock://anyurl.com")
        adapter.register_uri(method="GET", url="mock://anurl.com")

        text_insighter = TextInsight(searcher, SimpleWebScraper(), CosineSummariser())
        insights = text_insighter.get("render it on a browser", session.get)
        self.assertTrue(len(insights) is 5)
        self.assertEqual(insights[0].summary.text, "probably, it wouldn't do much if you render it on a browser, "
                                                   "though you can still see the webpage")


if __name__ == '__main__':
    unittest.main()
