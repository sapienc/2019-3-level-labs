import requests
import requests.exceptions
from requests.models import PreparedRequest

from bs4 import BeautifulSoup

from flask import Flask, render_template, redirect, url_for

# Standard libraries
import json
from datetime import datetime, date


app = Flask(__name__)

# ===== [FUNCTION: Check URL for validity] =====
def check_url(url):
    prepared_request = PreparedRequest() # create an instance of the PreparedRequest class of the requests library
    try:
        prepared_request.prepare_url(url, None) # checking for the correct of url
        return True
    except:
        return False

# ===== [FUNCTION: Get HTML content] =====
def get_html_page(url):

    print("Incoming URL is:", url, "\n")

    # Check for the type of input argument
    if type(url) is not str:
        raise TypeError(f"[!] Incorrect type of argument `url`! Should be a 'string', but came: {type(url)}")

    # Check if the url argument is empty
    if len(url) <= 0:
        raise ValueError(f"[!] Your URL is empty!")

    # Check for the correct of the received URL
    if not check_url(url):
        raise ValueError(f"[!] Invalid URL!\n*[TIP]: Correct URL consists of: http(s)://domain.name/[path/]")

    # Try to connect and receive content
    try:
        url_req = requests.get(url)
    except requests.exceptions.ConnectionError:
        raise Exception(f"[!] Can't connect to this URL: {url}\n*[TIP]: Try to check your URL for validity or even check your internet connection status!")
    except:
        raise ValueError(f"[!] Can't get HTML content by this URL: {url}\n*[TIP]: Try to check your URL for validity!")

    # Checking status_code
    if not url_req.status_code == 200:
        raise Exception(f"[!] status_code is not OK of incoming url: {url}\n*[TIP]: Perhaps you stumbled upon page 404...")

    return BeautifulSoup(url_req.text, "html.parser") # return for future handling

# ===== [FUNCTION: Get all articles and their submitted data] =====
def find_articles(page):
    if type(page) is not BeautifulSoup:
        raise TypeError(f"[!] Something went wrong! Incoming argument `page` is not what we are expected for.\n*[INPUT]: Incoming argument is not a BS4 type | `page` = {page}")

    try:
        # get a specific container from which we will search for the contents
        news_container = page.select_one('.flow .flow__posts')
        posts = news_container.find_all('div', {'class': 'flow-post'})
    except:
        raise Exception("[!] HTML page doesn't available!\n*[TIP]: Perhaps the page you need is not that you are looking for")

    articles = []

    try:
        for post in posts:
            # getting the DOM elements to grab info from them
            post_heading = post.select_one('.flow-post__title')
            post_description = post.select_one('.flow-post__excerpt')
            post_link = post_heading.parent.get('href')
            
            post_tags = []

            for tag in post.select('.meta-mark span[class^="meta-info"]'):
                post_tags.append( (tag.text).strip() )

            # forming an array with objects of each post
            articles += [{
                'title': post_heading.text,
                'descr': post_description.text,
                'link': post_link,
                'tags': post_tags
            }]
    except:
        raise Exception("[!] Can't parse content!\n*[TIP]: Perhaps DOM structure was changed...")

    return articles # return for future handling

# ===== [FUNCTION: Generate a JSON document about the received data] =====
def generate_json(path, url = "", articles = []):

    # Forming a json object
    json_obj = {
        'url': url,
        'creationDate': datetime.now().strftime("%d-%m-%Y [%H:%M:%S]"),
        'articles': articles
    }

    # Saving data to a json file
    with open(path, "w", encoding="utf-8") as file:
        json.dump(json_obj, file, indent = 4, ensure_ascii = False)

    return json_obj # return for future handling

# ===== [FUNCTION: Parse page] =====
def parse(url="https://lifehacker.ru/topics/news"):
    page = get_html_page(url) # getting HTML content of the page
    articles = find_articles(page) # grabbing articles from the pages
    generate_json("articles.json", url, articles) # generating json with grabbed data

# ===== [ROUTE: Root page] =====
@app.route('/', methods=["GET"])
def main():
    with open("articles.json", "r", encoding="utf-8") as file:
        articles_info = json.load(file) # loading articles from json file

    return render_template('main.html', articles = articles_info) # render our html page with articles data

@app.route('/update', methods=["POST"])
def refresh():
    parse()
    return redirect(url_for('main'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
# --------------- [ENTRY POINT] ---------------
if __name__ == '__main__': # if the program is launched directly from console
    print("===== [PROGRAM STARTED] =====\n")

    URL = "https://lifehacker.ru/topics/news"

    parse(URL)
    
    print("Parse done!")
    print("Running server...")
    
    app.run(port=8000, debug=True) # running a server on port 8000 with debug mode
    
    print("\n===== [PROGRAM FINISHED] =====")