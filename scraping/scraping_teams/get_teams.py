from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import cloudscraper
import time


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


def get_teams_links(teams_page):
    urls=[]
    home_page = "https://www.basketball-reference.com"
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

def get_team_season_link(url):

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
    tr_element = tbody_elements.find_all('tr')[1]
    th_element = tr_element.find('th', class_='left', attrs={'data-stat': 'season'})
    a_tag = th_element.find('a')
    if a_tag and 'href' in a_tag.attrs:
        href = a_tag['href']
        team_season_link = home_page + href
        #print("Extracted href:", team_season_link)
        return team_season_link

def get_Arena_Conference(url):
    team_info={}
    scraper = cloudscraper.create_scraper()
    try:
        time.sleep(4)
        url = get_team_season_link(url)
        page = scraper.get(url)
        page.raise_for_status()

        soup = BeautifulSoup(page.text, 'html.parser')

        #TABLE
        div_elements = soup.find('div', id='meta')
        div_element = div_elements.find('div',attrs={'data-template' : "Partials/Teams/Summary"})
        p_elements = div_element.find_all('p')

        pattern = r"NBA\s*([A-Za-z\s]+)\s*(?:</p>|</a>|$)"
        match = re.search(pattern, p_elements[0].text)
        conference = match.group(1).strip()
        team_info["Conference"] = conference

        for p in p_elements:
            strong = p.find('strong')
            if strong and strong.text.strip() == 'Arena:':
                arena_value = p.text.replace(strong.text, '').strip().split('   ')
                arena_value = arena_value[0].strip()
                team_info["Arena"] = arena_value
        return team_info
    
    except requests.RequestException as e:
        print(f"Request failed: {e}")

def get_Divisions(url):
    division_info={}
    scraper = cloudscraper.create_scraper()
    try:
        time.sleep(4)
        url_team_season = get_team_season_link(url)
        page = scraper.get(url_team_season)
        page.raise_for_status()

        soup = BeautifulSoup(page.text, 'html.parser')

        #TABLE
        div_elements = soup.find_all('div', class_='division')
        for p in div_elements:
            strong = p.find('strong')
            if strong:
                strong_text = strong.text.strip()
                #<strong> value
                remaining_text = p.text.replace(strong_text, '').strip()
                division_info[strong_text] = remaining_text.replace("\n",'').replace(":",'').replace(" ","").split(',')

        return division_info
    
    except requests.RequestException as e:
        print(f"Request failed: {e}")

def get_Teams_Data(urls):
    teams_info = []
    division_dict = get_Divisions(urls[0])
    print(division_dict)
    scraper = cloudscraper.create_scraper()
    for url in urls:
        try:
            time.sleep(4)
            
            arena_conference_info = get_Arena_Conference(url)

            page = scraper.get(url)
            page.raise_for_status()

            soup = BeautifulSoup(page.text, 'html.parser')

            pattern = r"/teams/([A-Z]{3})/"
            match = re.search(pattern, url)
            team_code = match.group(1)

            table_element = soup.find('table', id=team_code)
            tbody_elements = table_element.find('tbody')
            tr_element = tbody_elements.find_all('tr')[1]
            th_element = tr_element.find('th', class_='left', attrs={'data-stat': 'season'})
            a_tag = th_element.find('a')
            if a_tag and 'href' in a_tag.attrs:
              href = a_tag['href']
              print("Extracted href:", href)


            div_element = soup.find('div', id='meta')
            p_elements = div_element.find_all('p')

            team_info = {}
            for element in p_elements[2:]:
                text = element.get_text(strip=True)
                if ':' in text:
                    key, value = [part.strip() for part in text.split(':', 1)]
                    if key == "Team Names":
                        value = [name.strip() for name in value.split(',')][0]
                        key = "Team Name"
                        team_info[key] = value
                    elif key == "Team Name":
                        value = [name.strip() for name in value.split(',')][0]
                        team_info[key] = value

                    elif key == "Record":
                        parts = value.split(',')
                        win_loss = parts[0].strip()
                        if "NBA" in value:
                            win_loss = value[value.find('(')+1:value.find(' NBA')].strip()
                        win_loss = ''.join([c for c in win_loss if c.isdigit() or c == '-'])
                        win_percentage = parts[1].strip() if len(parts) > 1 else ""
                        win_percentage = ''.join([c for c in win_percentage if c.isdigit() or c == '.'])
                        team_info[key] = {"Win-Loss": win_loss, "Win Percentage": win_percentage}

                    elif key == "Seasons":
                        parts = value.split(';')
                        num_seasons = parts[0].strip()
                        if "NBA" in num_seasons:
                            num_seasons = num_seasons[num_seasons.find('(')+1:num_seasons.find(' NBA')].strip()
                        num_seasons = ''.join([c for c in num_seasons if c.isdigit()])
                        team_info[key] = {"Number of Seasons": num_seasons}

                    elif key == "Playoff Appearances":
                        if "NBA" in value:
                            value = value[value.find('(')+1:value.find(' NBA')].strip()
                        value = ''.join([c for c in value if c.isdigit()])
                        team_info[key] = value

                    elif key == "Championships":
                        if "NBA" in value:
                            value = value[value.find('(')+1:value.find(' NBA')].strip()
                        value = ''.join([c for c in value if c.isdigit()])
                        team_info[key] = value
                    else:
                        team_info[key] = value.replace(' ', '')

            team_info["Arena"] = arena_conference_info["Arena"]
            team_info["Conference"] = arena_conference_info["Conference"]
            for key in division_dict:
              for division in division_dict[key]:
                if (division in team_info["Team Name"]) or (division in team_info["Team Name"].strip(' ')) or ([x for x in team_info["Team Name"].split() if x in division]):
                  team_info["Division"] = key

            teams_info.append(team_info)
            print(team_info)

        except requests.RequestException as e:
            print(f"Request failed: {e}")

    return teams_info

def prepare_teams_csv(teams_infos):
  id = 0
  for dictio in teams_infos:
    id = id + 1
    dictio["id"] = id
    keys = list(dictio.keys())
    for key in keys:
      if key=="Seasons":
        dictio["seasons_played"] = dictio[key]["Number of Seasons"]
        del dictio[key]
      if key=="Record":
        dictio["win_loss"] = dictio[key]["Win-Loss"]
        dictio["win"] = dictio["win_loss"].split('-')[0]
        dictio["loss"] = dictio["win_loss"].split('-')[1]
        dictio["win_percentage"] = dictio[key]["Win Percentage"]
        del dictio[key]
        del dictio["win_loss"]
      if key=="Playoff Appearances":
        dictio["playoff_appearances"] = dictio[key]
        del dictio[key]
      if key=="Championships":
        dictio["championships"] = dictio[key]
        del dictio[key]
      if key=="Team Name":
        dictio["team_name"] = dictio[key]
        del dictio[key]
      if key=="Division":
        dictio["division"] = dictio[key]
        del dictio[key]
      if key=="Conference":
        dictio["conference"] = dictio[key]
        del dictio[key]
      if key=="Arena":
        dictio["arena"] = dictio[key]
        del dictio[key]
      if key=="Location":
        dictio["location"] = dictio[key]
        del dictio[key]

  pd.DataFrame(teams_infos).to_csv("./teams.csv",index=False)

  return teams_infos

if __name__ == "__main__":
    teams_page = get_tab_from_home("teams")
    urls = get_teams_links(teams_page)
    teams_info = get_Teams_Data(urls)
    prepare_teams_csv(teams_info)