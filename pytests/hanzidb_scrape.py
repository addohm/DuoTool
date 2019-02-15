import requests
import json
from bs4 import BeautifulSoup

base_url = 'http://hanzidb.org'


def soup_the_page(page_number):
    url = base_url + '/character-list/by-frequency?page=' + str(page_number)
    # url = 'http://addohm.net/test_folder/resources/Most common Chinese characters - ordered by frequency - page ' + str(page_number) + '.html'
    response = requests.get(url, timeout=5)
    soup = BeautifulSoup(response.content, 'lxml')
    return soup


def get_max_page(soup):
    paging = soup.find_all("p", {'class': 'rigi'})
    # Isolate the first paging link
    paging_link = paging[0].find_all('a')
    # Extract the last page number of the series
    max_page_num = int([item.get('href').split('=')[-1] for item in paging_link][-1])
    return max_page_num


def cleaned_data(val):
    if not val:
        return ''
    else:
        return val


def crawl_hanzidb():
    result, fields = {}

    # Get the page scrape data
    page_content = soup_the_page(1)
    # Get the page number of the last page
    last_page = get_max_page(page_content)
    # Get the table data
    for p in range(1, last_page + 1):
        page_content = soup_the_page(p)
        for trow in page_content.find_all('tr')[1:]:
            char_dict = {}
            i = 0
            n = 0
            n += 1
            character = trow.contents[0].text
            result['mode'] = 'main.CharacterModel'
            result['pk'] = n
            result[character] = []
            for tcell in trow.children:
                # Return list of strings from trow.children to parse urls
                char_position = 0
                radical_position = 3
                if i == char_position or i == radical_position:
                    for content in tcell.children:
                        if type(content).__name__ == 'Tag':
                            if 'href' in content.attrs:
                                url = base_url + content.attrs.get('href')
                                if i == char_position:
                                    char_dict['char_url'] = url
                                if i == radical_position:
                                    char_dict['radical_url'] = url
                i += 1
            char_dict['radical'] = trow.contents[3].text[:1]
            char_dict['pinyin'] = trow.contents[1].text
            char_dict['definition'] = trow.contents[2].text
            char_dict['hsk_level'] = trow.contents[5].text[:1] if trow.contents[5].text[:1].isdigit() else ''
            char_dict['frequency_rank'] = trow.contents[7].text if trow.contents[7].text.isdigit() else ''
            result[character].append(char_dict)
        print('Progress: ' + str(p) + '%.')
    return(result)


crawl_data = crawl_hanzidb()
with open('../resources/hanzidb.json', 'w') as f:
    json.dump(crawl_data, f, indent=2, ensure_ascii=False)
