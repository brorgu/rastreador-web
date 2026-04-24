import urllib.robotparser
import requests
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv
import csv
import time

#brand_dict = {}
load_dotenv()
base_url = os.getenv("BASE_URL")

rp = urllib.robotparser.RobotFileParser()
rp.set_url(base_url+"/robots.txt")
rp.read()

sitemaps = rp.site_maps()
sitemap = sitemaps[0]
#print(sitemap)
maps_clean_text = []
products_clean_text = []
products_clean_text = []


sitemap_response = requests.get(sitemap)
soup = BeautifulSoup(sitemap_response.content, "xml")
#print(soup)
product_maps = soup.find_all('loc', string=re.compile("product"))
for index, product in enumerate(product_maps):
    maps_clean_text.append(product_maps[index].get_text())


#print(maps_clean_text[0])
#print(maps_clean_text[1])
#print(maps_clean_text[6])

list_len_maps = len(maps_clean_text)
#print(list_len_maps)

for product_map_index in range(list_len_maps):
    print(product_map_index)
    print(maps_clean_text[product_map_index])
    url = maps_clean_text[product_map_index]

    product_details_response = requests.get(url)
    product_details_soup = BeautifulSoup(product_details_response.content, "xml")
    product_xml_list = product_details_soup.find_all('loc', string=re.compile("products"))
    for index, product in enumerate(product_xml_list):
        products_clean_text.append(product_xml_list[index].get_text())
        #print(products_clean_text[index])
        #print(index)

# small debug print
#print(len(products_clean_text))
#print("produkt url nr 6900 " + products_clean_text[6900])
#print("produkt url nr 500 " + products_clean_text[500])
#print(products_clean_text)


def productcrawler(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    product_response = requests.get(url, headers=headers)
    product_soup = BeautifulSoup(product_response.text, "html.parser")

    price_tag = product_soup.find(
        lambda tag: tag.name in ["div", "span", "p"] and
        tag.get("class") and
        any(re.search(r"price", c, re.I)
        for c in tag.get("class")) and
        re.search(r"\d+,\d+", tag.get_text())
        )
    #print(price_tag.text)
    match = re.search(r"(\d+,\d{2})", price_tag.text)
    #print(match)

    if match:
        price = match.group(1)
    #    print(price)

    product_name = product_soup.find("h1")
    if product_name:
        product_name = product_name.get_text()
        #print(product_name)
    else:
        print("No product found")

    product_comp = [product_name, price]
    #print(product_comp)
    return product_comp

def csvwriter(product):
    with open('products.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(product)

number_of_products = len(products_clean_text)
print("number of products " + str(number_of_products))

for index in range(number_of_products):
    product_crawler = productcrawler(products_clean_text[index])
    csvwriter(product_crawler)
    print(product_crawler)
    # DoS protection
    print("wait started..")
    time.sleep(1)
    print("sleep ended")

# small test run
#cprice = productcrawler(products_clean_text[6900])
#csvwriter(cprice)
#cprice = productcrawler(products_clean_text[500])
#csvwriter(cprice)