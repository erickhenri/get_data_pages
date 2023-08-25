import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
from flask import Flask, jsonify, request
import os

all_pages = []
headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

def getLinks(soup, root_path, domain):
    global all_pages
    
    all_links_elements = soup.find_all('a', href = True)

    for element in all_links_elements:
        route = element.get('href')

        if not route.startswith(root_path):
            continue
        if '#' in route:
            continue
        
        link = domain + route
        new_page = {'link': link, 'content': ''}

        if all(existing_page["link"] != new_page["link"] for existing_page in all_pages):
            all_pages.append({'link':link,'content': ''})

def getContent(page):
    global all_pages
    global headers

    site = requests.get(page['link'], headers)
    soup = BeautifulSoup(site.content, 'html.parser')
    
    content = soup.text
    index = all_pages.index(page)
    new_page = {'link': page['link'], 'content': content}
    all_pages[index] = new_page

def browseTheLinks(soup, root_path, domain):
    global all_pages
    
    list_index = 0
    
    next_page = ""
    for index, page in enumerate(all_pages):
        list_index = index
        
        if page['content'] != "":
            continue
            
        next_page = page
        break
    
    if next_page == "":
        return
        

    getContent(next_page)
    getLinks(soup, root_path, domain)
    print(all_pages[index])
    browseTheLinks(soup, root_path, domain)

app = Flask(__name__)

@app.route('/pages', methods=['GET'])
def get_pages():
    ##Variáveis de entrada
    url = request.args.get('url')
    scope_url = request.args.get('scope_url')

    # url = 'https://tanstack.com/query/latest/docs/react/overview'
    # scope_url = 'https://tanstack.com/query/latest/docs/react'

    parsed_url = urlsplit(scope_url)

    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    root_path = parsed_url.path

    site = requests.get(url, headers)
    soup = BeautifulSoup(site.content, 'html.parser')

    # url = request.args.get('url')
    # scope_url = request.args.get('scope_url')

    getLinks(soup, root_path, domain)
    browseTheLinks(soup, root_path, domain)
    return jsonify(all_pages)

if __name__ == "__main__":
    # Obtém a porta do ambiente, definida pelo Railway
    port = int(os.environ.get("PORT", 5000))
    
    # Define o host como '0.0.0.0' para que o aplicativo seja acessível externamente
    app.run(host='0.0.0.0', port=port)