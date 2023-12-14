import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import json
from pprint import pprint

url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page='


def get_randon_headers():
    return Headers(os="win", browser="firefox").generate()


response = requests.get(url + "0", headers=get_randon_headers())
main_html = response.text
main_soup = BeautifulSoup(main_html, "lxml")
last_page = main_soup.find_all('a', class_='bloko-button')  # Узнаем номер последней страницы
num_last_page = int(last_page[-2].text)
articles_data = []
for i in range(num_last_page):  # идем по каждой странице
    print(f"Страница {i + 1}/{num_last_page}")
    response = requests.get(url + str({i}), headers=get_randon_headers())
    main_html_data = response.text
    main_soup = BeautifulSoup(main_html_data, "lxml")

    article_list = main_soup.find("div", {'data-qa': "vacancy-serp__results", 'id': "a11y-main-content"})
    if article_list is None:
        continue

    articles = article_list.find_all(class_="serp-item")

    for article_tag in articles:
        link = article_tag.find('a', class_='serp-item__title')['href']
        response = requests.get(link, headers=get_randon_headers())
        link_data = response.text
        soup = BeautifulSoup(link_data, "lxml")
        discr = soup.find('div', class_='g-user-content')
        if discr is None or discr.text.lower().find('django') == -1 or discr.text.lower().find('flask') == -1:
            continue
        else:
            name_job = article_tag.find('a', class_='serp-item__title').text

            salary = article_tag.find("span", class_="bloko-header-section-2")
            if salary is not None:
                salary = salary.text
            else:
                salary = 'Зарплата не указана'

            city = article_tag.find("div", {'data-qa': "vacancy-serp__vacancy-address"}).text

            company = article_tag.find("div", class_="vacancy-serp-item__meta-info-company").text
            articles_data.append(
                {
                    "name_job": name_job,
                    "link": link,
                    "salary": salary,
                    "city": city,
                    "company": company
                }
            )

with open('vacancy.json', 'w', encoding='utf-8') as f:
    json.dump(articles_data, f, indent=2, ensure_ascii=False)
