from bs4 import BeautifulSoup
import requests
import pandas as pd
import cloudscraper
import time
import unicodedata

def get_tab_from_home(tab):

  home_page = "https://www.basketball-reference.com"

  scraper = cloudscraper.create_scraper()

  try:
      page = scraper.get(home_page)
      page.raise_for_status()

      soup = BeautifulSoup(page.text, 'html.parser')

      #TAB NAME
      li_element = soup.find('li', id='header_'+tab)

      if li_element:
          #Extract the href from the <a> tag
          a_tag = li_element.find('a')
          if a_tag and 'href' in a_tag.attrs:
              href = a_tag['href']

  except requests.RequestException as e:
      print(f"Request failed: {e}")
  return home_page + href

def get_season_link(url,season):
  scraper = cloudscraper.create_scraper()
  page = scraper.get(url)
  page.raise_for_status()
  home_page = "https://www.basketball-reference.com"
  soup = BeautifulSoup(page.text, 'html.parser')

  table_element = soup.find('table', id="stats")
  tr_element = table_element.find_all('tr')[season]
  th_element = tr_element.find('th', class_='left', attrs={'data-stat': 'season'})
  a_tag = th_element.find('a')
  if a_tag and 'href' in a_tag.attrs:
    href = a_tag['href']
    season_link = home_page + href

    return season_link , a_tag.text

def get_Season_Data(url):

    scraper = cloudscraper.create_scraper()

    seasons_info = []
    id = 0

    for season in range(3,10):
        id +=1
        season_dict = {}
        season_dict["id"] = id
        season_link , season_label = get_season_link(url,season)
        season_dict["season_label"] = season_label
        season_dict["year_start"] = season_label[0:4]
        season_dict["year_end"] = '20' + season_label[5:7]
        try:
            time.sleep(4)

            page = scraper.get(season_link)
            page.raise_for_status()

            page.encoding = 'utf-8'
            soup = BeautifulSoup(page.text, 'html.parser')

            div_element = soup.find('div', id='meta')
            p_elements = div_element.find_all('p')

            for p_element in p_elements:
                strong_element = p_element.find('strong')
                if strong_element:
                  strong_text = strong_element.text.strip()
                  a_tag = p_element.find('a')
                  text = a_tag.text.strip()
                  normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
                  season_dict[strong_text] = normalized_text

            seasons_info.append(season_dict)

        except requests.RequestException as e:
            print(f"Request failed: {e}")

    pd.DataFrame(seasons_info).to_csv("./seasons.csv",index=False)
    
    return seasons_info


if __name__ == "__main__":
    url = get_tab_from_home("leagues")
    season_info = get_Season_Data(url)