import json
import unittest

from lab_1 import get_html_page, find_articles, generate_json, BeautifulSoup, requests


class CrawlerTests(unittest.TestCase):

    # ===== [TEST: Test json structure] =====
    def test_json_structure(self):
        with open("samples/lifehacker.json", "r", encoding="utf-8") as file:
            json_info = json.load(file)

        # URL property in json object
        self.assertIn("url", json_info) # does the url property even exist in the json object?
        self.assertIs(type(json_info["url"]), str) # does the url property have a type value of str?
        self.assertIsNot(len(json_info["url"]), 0) # is the length of the url property nonzero?

        # creationDate property in json object
        self.assertIn("creationDate", json_info) # does the creationDate property even exist in the json object?
        self.assertIs(type(json_info["creationDate"]), str) # does the creationDate property have a type value of str?
        self.assertIsNot(len(json_info["creationDate"]), 0) # is the length of the creationDate property nonzero?

        # articles property in json object
        self.assertIn("articles", json_info) # does the articles property even exist in the json object?
        self.assertIs(type(json_info["articles"]), list) # does the articles property have a type value of str?
        self.assertIsNot(len(json_info["articles"]), 0) # is the length of the articles property nonzero?

        # title property in articles array of json object
        self.assertIn("title", json_info["articles"][0]) # does the article title property even exist in the articles array?
        self.assertIs(type(json_info["articles"][0]["title"]), str) # does the article title property have a type value of str?
        self.assertIsNot(len(json_info["articles"][0]["title"]), 0) # is the length of the article title property nonzero?

    # ===== [TEST: Test html parsing] =====
    def test_html_parsing(self):
        with open("samples/lifehacker.htm", "r", encoding="utf-8") as file:
            html_file = file.read()

        souped_page = BeautifulSoup(html_file, "html.parser")

        articles = find_articles(souped_page)

        # Tests for types to be equal
        self.assertIs(type( articles ), list) # checking that articles has a type of array
        self.assertIsNot(len(articles), 0) # checking that length of articles array is not zero
        self.assertIn("title", articles[0]) # checking that articles[0] has a property of title
        self.assertIs(type( articles[0]["title"] ), str) # checking that value of articles[0]["title"] has a type of string

        # Tests for rising TypeError exception
        with self.assertRaises(TypeError):
            find_articles(None)
            find_articles("")
            find_articles(10)
            find_articles([])
            find_articles({})
    
    # ===== [TEST: Test get_html_page] =====
    def test_get_html(self):
        self.assertRaises(TypeError, get_html_page, None) # not an expected type
        self.assertRaises(ValueError, get_html_page, "") # empty string
        self.assertRaises(ValueError, get_html_page, "Just a string | Not the URL") # not the URL
        self.assertRaises(Exception, get_html_page, "https://lifehacker.ru/qdwqwdq") # 

        self.assertIs(type( get_html_page("https://lifehacker.ru/topics/news") ), type(BeautifulSoup("",  "html.parser")) )
        
# --------------- [ENTRY POINT] ---------------
if __name__ == '__main__':
    unittest.main()