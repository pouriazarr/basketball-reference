from bs4 import BeautifulSoup
import requests
import pandas as pd
import cloudscraper
import time
import unicodedata

def get_award_link(url,award_name):
  scraper = cloudscraper.create_scraper()
  page = scraper.get(url)
  page.raise_for_status()
  home_page = "https://www.basketball-reference.com"
  soup = BeautifulSoup(page.text, 'html.parser')

  div_element = soup.find('div', id="content")
  div_inner_element = div_element.find('div', class_='flexindex wrapable')
  div_inner_element = div_inner_element.find_all('div', class_='forcefull')[1]
  p_elements = div_inner_element.find_all('p')

  for p_element in p_elements:
    a_tag = p_element.find('a')
    strong_tag = a_tag.find('strong')
    if award_name == strong_tag.text:
        href = a_tag['href']
        award_link = home_page + href

        return award_link

def build_awards(award_names,award_types,recipient_types):
  awards = []
  award_dict = {}
  id = 1
  for award_name,award_type,recipient_type in zip(award_names,award_types,recipient_types):
    award_dict["id"] = id
    award_dict["award_name"] = award_name
    award_dict["award_type"] = award_type
    award_dict["recipient_type"] = recipient_type
    awards.append(award_dict)
    id += 1
  pd.DataFrame(awards).to_csv("./awards.csv",index=False)
  return awards

def get_Award_Data(url,award_name):
    award_info = []
    season_id = 0
    
    award_link = get_award_link(url,award_name)

    try:
        time.sleep(4)
        scraper = cloudscraper.create_scraper()
        page = scraper.get(award_link)
        page.raise_for_status()

        page.encoding = 'utf-8'

        soup = BeautifulSoup(page.text, 'html.parser')

        div_element = soup.find('div', id='content')
        div_inner_element = div_element.find('div', id='all_mvp_NBA')
        div_inner_element = div_inner_element.find('div', id="div_mvp_NBA")
        table_element = div_inner_element.find('table',id="mvp_NBA")
        tbody_element = table_element.find('tbody')
        tr_elements = tbody_element.find_all('tr')

        for tr_element in tr_elements:
            season_id += 1
            award_dict = {}
            award_dict["season_id"] = season_id
            award_dict["award_id"] = 1
            td_element = tr_element.find('td' , attrs={'data-stat' : 'player'})
            a_tag = td_element.find('a')
            name_text = a_tag.text.strip()
            normalized_text = unicodedata.normalize('NFKD', name_text).encode('ascii', 'ignore').decode('utf-8')
            award_dict["name"] = normalized_text
            td_element = tr_element.find('td' , attrs={'data-stat' : 'team_id'})
            a_tag = td_element.find('a')
            award_dict["team"] = a_tag.text.strip()

            award_info.append(award_dict)
    except requests.RequestException as e:
            print(f"Request failed: {e}")

    pd.DataFrame(award_info).to_csv("./awards_season.csv",index=False)
    
    return award_info


if __name__ == "__main__":
   
   url = "https://www.basketball-reference.com/awards"
   award_url = get_award_link(url,"Most Valuable Player (Michael Jordan Trophy)")
   awards = build_awards(["Most Valuable Player (Michael Jordan Trophy)"],["season"],["player"])
   award_info = get_Award_Data(award_url,"Most Valuable Player (Michael Jordan Trophy)")
   
   