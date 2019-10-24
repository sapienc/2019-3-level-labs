# ===== [IMPORT: Importing external libraries] =====
import requests
import requests.exceptions
from requests.models import PreparedRequest

from bs4 import BeautifulSoup
from flask import Flask, render_template, redirect, url_for, request

# ===== [IMPORT: Importing standard libraries] =====
import json
from datetime import datetime, date
import os.path
import random


app = Flask(__name__)

sites = {
    "lifehacker": [
        "Лайфхакер",
        "https://lifehacker.ru/topics/news"
    ],
    "mailru": [
        "Новости Mail.RU",
        "https://news.mail.ru/economics/"
    ],
    "nnru": [
        "Новости NN.RU",
        "https://www.nn.ru/news/"
    ]
}
#######################################################################################################
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
        raise ValueError("[!] Your URL is empty!")

    # Check for the correct of the received URL
    if not check_url(url):
        raise ValueError("[!] Invalid URL!\n*[TIP]: Correct URL consists of: http(s)://domain.name/[path/]")

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
def find_articles(page, page_label):
    if type(page) is not BeautifulSoup:
        raise TypeError(f"[!] Something went wrong! Incoming argument `page` is not what we are expected for.\n*[INPUT]: Incoming argument is not a BS4 type | `page` = {page}")

    params = {
        'lifehacker': {
            'container': '.flow .flow__posts',
            'posts': ['div', 'class', 'flow-post'],

            'heading': '.flow-post__title',
            'descr': '.flow-post__excerpt',
            'tags': '.meta-mark span[class^="meta-info"]'
        },
        'mailru': {
            'container': '.paging__content',
            'posts': ['div', 'class', 'newsitem'],

            'heading': '.cell .newsitem__title',
            'descr': '.cell .newsitem__text'
        },
        'nnru': {
            'container': '.rn-section_lenta-on-main .rn-info__list',
            'posts': ['li', 'class', 'rn-info__item'],

            'heading': '.rn-info__announce .rn-info__announce-text'
        },
    }

    try:
        # get a specific container from which we will search for the contents
        news_container = page.select_one( params[page_label]['container'] )
        posts = news_container.find_all(
            params[page_label]['posts'][0],
            { params[page_label]['posts'][1]: params[page_label]['posts'][2]}
        )
        
        if page_label == 'nnru':
            del posts[-1]

    except KeyError:
        raise KeyError(f"[!] There is no instructions for parsing by label: {page_label}!")
    except:
        raise Exception("[!] HTML page doesn't available!\n*[TIP]: Perhaps the page you need is not that you are looking for")

    articles = []
    post_heading = post_description = post_link = None

    try:
        for post in posts:
            # HEADING
            post_heading = post.select_one( params[page_label]['heading'] )

            # DESCRIPTION
            if page_label == 'lifehacker' or page_label == 'mailru':
                post_description = post.select_one( params[page_label]['descr'] ).text
            elif page_label == 'nnru':
                post_description = "Описание внутри статьи."

            # LINK
            if page_label == 'lifehacker' or page_label == 'nnru':
                post_link = post_heading.parent.get('href')
            elif page_label == 'mailru':
                post_link = "https://news.mail.ru/" + post_heading.get('href')

            # TAGS
            post_tags = []
            if page_label == 'lifehacker':
                for tag in post.select( params[page_label]['tags'] ):
                    post_tags.append( (tag.text).strip() )
            elif page_label == 'mailru':
                for tag in post.select_one('.newsitem__params').find_all('span', {'class': 'newsitem__param'}):
                    post_tags.append( (tag.text).strip() )
                post_tags = [
                    "Актуальность: " + post_tags[0],
                    "Источник: " + post_tags[1]
                ]
            elif page_label == 'nnru':
                post_tags.append("НОВОСТИ НИЖНЕГО НОВГОРОДА")

            articles += [{
                'title': post_heading.text,
                'descr': post_description,
                'link': post_link,
                'tags': post_tags
            }]
            
    except KeyError:
        raise KeyError(f"[!] There is no instructions for parsing by label: {page_label}!")
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
def parse(url="https://lifehacker.ru/topics/news", page_label = ""):
    page = get_html_page(url) # getting HTML content of the page
    articles = find_articles(page, page_label) # grabbing articles from the pages
    generate_json(page_label + "_"  + "articles.json", url, articles) # generating json with grabbed data

#######################################################################################################

# ===== [ROUTE: Root page] =====
@app.route('/', methods=["GET"])
def main():
    return render_template('index.html') # render our main html page

# ===== [ROUTE: Category handler] =====
@app.route('/lifehacker', methods=["GET"])
@app.route('/mailru', methods=["GET"])
@app.route('/nnru', methods=["GET"])
def page_handler():
    current_page = request.path.split('/')[1]

    # if lifehacker_articles.json doesn't exists
    if not os.path.isfile(current_page + "_articles.json"):
        try:
            parse( sites[current_page][1], current_page) # trying to parse site by url, which is in: sites array, by current_page
        except KeyError:
            raise KeyError(f"[!] Can't get URL in sites array, searching by key `{current_page}`")
    
    with open(current_page + "_" + "articles.json", "r", encoding="utf-8") as file:
        articles_info = json.load(file) # loading articles from json file

    page_info = {
        'label': current_page,
        'title': sites[current_page][0]
    }

    return render_template('articles.html', articles = articles_info, page = page_info) # render our html page with articles data

# ===== [ROUTE: Refresh handler] =====
@app.route('/update', methods=["POST"])
def refresh():
    src = request.form['src'] #parse()

    try:
        parse( sites[src][1], src) # trying to parse site by url, which is in: sites array, by key: src
    except KeyError:
        raise KeyError(f"[!] There's no site in sites array, searching by key `{src}`")

    return redirect(request.url_root + src) #url_for('page_handler'))

# ===== [ROUTE: 404 handler] =====
@app.errorhandler(404)
def page_not_found(e):
    style = ['lifehacker', 'mailru', 'nnru']
    style_id = random.randint(0,2)
    return render_template('404.html', style = style[style_id]), 404
# --------------- [ENTRY POINT] ---------------
if __name__ == '__main__': # if the program is launched directly from console
    print("===== [PROGRAM STARTED] =====\n")

    #URL = "https://lifehacker.ru/topics/news"
    #parse(URL)
    #print("Parse done!")
    
    print("Running server...")
    app.run(port=8000, debug=True) # running a server on port 8000 with debug mode
    
    print("\n===== [PROGRAM FINISHED] =====")