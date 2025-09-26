from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import cloudscraper
import time

def get_team_season_link(url,season):

  home_page = "https://www.basketball-reference.com"
  scraper = cloudscraper.create_scraper()
  page = scraper.get(url)
  page.raise_for_status()

  soup = BeautifulSoup(page.text, 'html.parser')

  pattern = r"/teams/([A-Z]{3})/"
  match = re.search(pattern, url)
  team_code = match.group(1)

  table_element = soup.find('table', id=team_code)
  tbody_elements = table_element.find('tbody')
  tr_element = tbody_elements.find_all('tr')[season]
  th_element = tr_element.find('th', class_='left', attrs={'data-stat': 'season'})
  a_tag = th_element.find('a')
  if a_tag and 'href' in a_tag.attrs:
    href = a_tag['href']
    team_season_link = home_page + href
    return team_season_link


def get_win_loss_team_seasons(team_url):
  win_loss_team_seasons = {}
  scraper = cloudscraper.create_scraper()
  try:
    time.sleep(4)

    page = scraper.get(team_url)
    page.raise_for_status()

    soup = BeautifulSoup(page.text, 'html.parser')

    pattern = r"/teams/([A-Z]{3})/"
    match = re.search(pattern,team_url)
    team_code = match.group(1)
    table_element = soup.find('table', id=team_code)
    tbody_elements = table_element.find('tbody')
    for season in range(1,8):
      tr_elements = tbody_elements.find_all('tr')[season]
      td_elements_wins = tr_elements.find('td',attrs={'data-stat' : 'wins'})
      td_elements_losses = tr_elements.find('td',attrs={'data-stat' : 'losses'})
      win_loss_team_seasons[str(season)] = {"wins": int(td_elements_wins.text),"losses": int(td_elements_losses.text)}
    return win_loss_team_seasons , team_code
  except requests.RequestException as e:
    print(f"Request failed: {e}")


def get_team_seasons(team_url):

  team_seasons_dict = {}
  win_loss_team_seasons , team_code = get_win_loss_team_seasons(team_url)
  team_seasons_dict["team_code"] = team_code
  scraper = cloudscraper.create_scraper()

  for season in range(1,8):
    team_seasons = {}
    team_season_link = get_team_season_link(team_url,season)
    url = team_season_link
    try:
      time.sleep(4)
      #url = "https://www.basketball-reference.com/teams/DEN/2025.html"
      page = scraper.get(url)
      page.raise_for_status()

      soup = BeautifulSoup(page.text, 'html.parser')

      div_element = soup.find('div', attrs={'data-template' :"Partials/Teams/Summary"})
      p_elements = div_element.find_all('p')

      for p in p_elements:
        record = p.text.strip("\n").strip().strip(' ').split('\n')
        #print(p.text.strip("\n").strip().strip(' ').split('\n'))
        if "Record:" in record:
          team_seasons["conference"] = record[3].strip()
          match = re.search(r'(\d+)(?:th|rd|nd|st)', record[2])
          rank = match.group(1)
          team_seasons["rank"] = rank
        if "Coach" in record[0]:
          coach=record[0].split(':')
          full_name_regex = r'\b([A-Za-z]+\s+[A-Za-z]+)\b(?=\s*\()'
          dotted_name_regex = r'\b[A-Z]\.\s*[A-Z]\.\s*([A-Za-z]+)\b(?=\s*\()'
          dotted_match = re.findall(dotted_name_regex, coach[1])
          full_name_match = re.findall(full_name_regex, coach[1]) if not dotted_match else []
          team_seasons["coach"] = dotted_match[0] if dotted_match else full_name_match[0] if full_name_match else ""
        if "PTS/G:" in record[0].strip():
          numeric_regex = r'\b\d+\.?\d*\b'
          numeric_match = re.search(numeric_regex, record[1])
          team_seasons["PTS/G"] = numeric_match.group(0)
        if len(record) > 2:
          if "Opp PTS/G:" in record[2]:
            numeric_regex = r'\b\d+\.?\d*\b'
            numeric_match = re.search(numeric_regex, record[3])
            team_seasons["OppPTS/G"] = numeric_match.group(0)
        if len(record) > 2:
          if "SRS:" in record[0]:
            srs = record[0].split(':')
            numeric_regex = r'\b\d+\.?\d*\b'
            numeric_match = re.search(numeric_regex, srs[1])
            team_seasons["SRS"] = numeric_match.group(0)

        if len(record) > 2:
          if re.search(r'\bPace\b', record[2]):
            pace = record[2].split(':')
            numeric_regex = r'\b\d+\.?\d*\b'
            numeric_match = re.search(numeric_regex, pace[1])
            team_seasons["Pace"] = numeric_match.group(0)
        if "Off Rtg" in record[0]:
          ortg = record[0].split(':')
          numeric_regex = r'\b\d+\.?\d*\b'
          numeric_match = re.search(numeric_regex, ortg[1])
          team_seasons["ORtg"] = numeric_match.group(0)
        if len(record) > 2:
          if "Def Rtg" in record[1]:
            drtg = record[1].split(':')
            numeric_regex = r'\b\d+\.?\d*\b'
            numeric_match = re.search(numeric_regex, drtg[1])
            team_seasons["DRtg"] = numeric_match.group(0)
          if "Net Rtg" in record[2]:
            nrtg = record[2].split(':')
            numeric_regex = r'\b\d+\.?\d*\b'
            numeric_match = re.search(numeric_regex, nrtg[1])
            team_seasons["NetRtg"] = numeric_match.group(0)
          if "Preseason Odds:" in record[0]:
            numeric_regex = r'[+-]?\d+'
            numeric_match = re.search(numeric_regex, record[1])
            team_seasons["championship_odds"] = numeric_match.group(0)
          if "Arena:" in record[0]:
            numeric_regex = r'[+-]?\d{1,3}(,\d{3})*'
            numeric_match = re.search(numeric_regex, record[6])
            team_seasons["attendace_total"] = numeric_match.group(0).replace(',','')

    except requests.RequestException as e:
      print(f"Request failed: {e}")
    team_seasons_dict[str(season)] = team_seasons
    team_seasons_dict[str(season)].update(win_loss_team_seasons[str(season)])
  return team_seasons_dict

def get_tab_from_home(tab):

  home_page = "https://www.basketball-reference.com"
  scraper = cloudscraper.create_scraper()

  try:
      page = scraper.get(home_page)
      page.raise_for_status()

      soup = BeautifulSoup(page.text, 'html.parser')

      #TAB NAME
      tab = "teams"
      li_element = soup.find('li', id='header_'+tab)

      if li_element:
          #Extract the href from the <a> tag
          a_tag = li_element.find('a')
          if a_tag and 'href' in a_tag.attrs:
              href = a_tag['href']

  except requests.RequestException as e:
      print(f"Request failed: {e}")
  return home_page + href


def get_teams_links(teams_page):
  urls=[]
  home_page = "https://www.basketball-reference.com/"
  scraper = cloudscraper.create_scraper()
  try:
      page = scraper.get(teams_page)
      page.raise_for_status()

      soup = BeautifulSoup(page.text, 'html.parser')

      #TABLE
      table_element = soup.find('table', id='teams_active')
      tr_elements = table_element.find_all('tr', class_='full_table')

      for element in tr_elements:
        th_element = element.find('th', class_='left', attrs={'data-stat': 'franch_name'})

        a_tag = th_element.find('a')
        if a_tag and 'href' in a_tag.attrs:
            href = a_tag['href']
            team_link = home_page + href
            urls.append(team_link)


  except requests.RequestException as e:
      print(f"Request failed: {e}")
  return urls

def prepare_teams_csv(urls):
  team_id = 0
  dict_list = []
  for url in urls:
    team_s_dict = get_team_seasons(url)
    keys = list(team_s_dict.keys())
    team_id +=1
    print(team_s_dict)
    for key in keys:
      if key=="team_code":
        team_s_dict["team_id"] = team_id
        del team_s_dict[key]
      else:
        #team_s_dict[key].update({"season_id" : key})
        #team_s_dict[key].update({"team_id" : team_s_dict["team_id"]})
        new_dict = {"team_id": team_id,"season_id": key}
        new_dict.update(team_s_dict[key])
        dict_list.append(new_dict)
        del team_s_dict[key]


  pd.DataFrame(dict_list).to_csv("./team_seasons.csv",index=False)

  return dict_list

if __name__ == "__main__":
    teams_page = get_tab_from_home("teams")
    teams_urls = get_teams_links(teams_page)
    prepare_teams_csv(teams_urls)