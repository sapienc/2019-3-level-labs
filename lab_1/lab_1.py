import requests
from bs4 import BeautifulSoup

from requests.models import PreparedRequest
import requests.exceptions

import json
from datetime import datetime, date


# ===== [ФУНКЦИЯ: Проверить URL на валидность] =====
def check_url(url):
    prepared_request = PreparedRequest() # создадим экземпляр класса PreparedRequest библиотеки requests
    try:
        prepared_request.prepare_url(url, None)
        return True
    except:
        return False


# ===== [ФУНКЦИЯ: Получить HTML контент] =====
def get_html_page(url):

    print("Incoming URL is:", url, "\n")

    # Проверим на тип входящего аргумента
    if type(url) is not str:
        raise TypeError(f"[!] Incorrect type of argument `url`! Should be a 'string', but came: {type(url)}")

    # Проверим на заполненность аргумента url
    if len(url) <= 0:
        raise ValueError(f"[!] Your URL is empty!")

    # Проверим на корректность пришедшего URL
    if not check_url(url):
        raise ValueError(f"[!] Invalid URL!\n*[TIP]: Correct URL consists of: http(s)://domain.name/[path/]")

    # Произведем попытку подключения и получения контента
    try:
        url_req = requests.get(url)
    except requests.exceptions.ConnectionError:
        raise Exception(f"[!] Can't connect to this URL: {url}\n*[TIP]: Try to check your URL for validity or even check your internet connection status!")
    except:
        raise ValueError(f"[!] Can't get HTML content by this URL: {url}\n*[TIP]: Try to check your URL for validity!")

    # Проверим что со status_code'ом
    if not url_req.status_code == 200:
        raise Exception(f"[!] status_code is not OK of incoming url: {url}\n*[TIP]: Perhaps you stumbled upon page 404...")

    return BeautifulSoup(url_req.text, "lxml") # вернем результат

# ===== [ФУНКЦИЯ: Получить все статьи и их представленные данные] =====
def find_articles(page):
    if type(page) is not BeautifulSoup:
        raise TypeError(f"[!] Something went wrong! Incoming argument `page` is not what we are expected for.\n*[INPUT]: Incoming argument is not a BS4 type | `page` = {page}")

    try:
        # получим конкретный контейнер, у которого будем искать содержимое
        news_container = page.select_one('.flow .flow__posts')
        posts = news_container.find_all('div', {'class': 'flow-post'})
    except:
        raise Exception("[!] HTML page doesn't available!\n*[TIP]: Perhaps the page you need is not that you are looking for")

    articles = []

    try:
        for post in posts:
            post_heading = post.select_one('.flow-post__title')
            post_description = post.select_one('.flow-post__excerpt')
            post_link = post_heading.parent.get('href')
            
            post_tags = []

            for tag in post.select('.meta-mark span[class^="meta-info"]'):
                post_tags.append( (tag.text).strip() )

            articles += [{
                'title': post_heading.text,
                'descr': post_description.text,
                'link': post_link,
                'tags': post_tags
            }]
    except:
        raise Exception("[!] Can't parse content!\n*[TIP]: Perhaps DOM structure was changed...")

    return articles

# ===== [ФУНКЦИЯ: Сформировать JSON документ о полученных данных] =====
def generate_json(path, url = "", articles = []):

    json_obj = {
        'url': url,
        'creationDate': datetime.now().strftime("%d-%m-%Y [%H:%M:%S]"),
        'articles': articles
    }

    # Сохранием объект в файл
    with open(path, "w", encoding="utf-8") as file:
        json.dump(json_obj, file, indent = 4, ensure_ascii = False)

    return json_obj
# --------------- [ТОЧКА ВХОДА] ---------------
if __name__ == '__main__': # если программа запущена напрямую
    print("===== [PROGRAM STARTED] =====\n")

    URL = "https://lifehacker.ru/topics/news"

    page = get_html_page(URL)
    articles = find_articles(page)
    generate_json("articles.json")
    
    print("Done!")
    
    print("\n===== [PROGRAM FINISHED] =====")