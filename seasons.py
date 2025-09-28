from selenium import webdriver
from selenium.webdriver.common.by import By
from player_seasons import get_player_data
import pandas as pd
import unicodedata


def get_season_data(browser,team_list):
    player_seasons_data = []
    players_data = []
    for team_name, team_url in team_list:
        browser.get(team_url)
        team= team_url.split("teams/")[1].split('/')[0]
        table = browser.find_element(By.CSS_SELECTOR, f'table#{team}')
        tbody = table.find_element(By.TAG_NAME, 'tbody')
        rows = tbody.find_elements(By.TAG_NAME, 'tr')
        season = []
        for row in rows:
            cells = row.find_elements(By.XPATH, './*')
            if not cells:
                continue
            first_cell = cells[0]
            link = first_cell.find_elements(By.TAG_NAME, 'a')
            if not link:
                continue
            season_text = link[0].text.strip()
            season_link = link[0].get_attribute("href")
            season.append((season_text, season_link))
        player_seasons,players = get_player_data(browser,team_name,season[1:8])
        player_seasons_data.append(player_seasons)
        players_data.append(players)
    final_player_seasons_df = pd.concat(player_seasons_data, ignore_index=True)
    final_player_seasons_df.drop_duplicates(inplace=True)
    final_player_seasons_df.reset_index(drop=True, inplace=True)


    final_players_df = pd.concat(players_data, ignore_index=True)
    final_players_df.drop_duplicates(subset=['Player', 'Birth Date'], inplace=True)
    final_players_df.reset_index(drop=True, inplace=True)
    final_players_df['id'] = final_players_df.index + 1
    final_players_df = final_players_df[['id', 'Player', 'Pos', 'Ht', 'Wt', 'Birth Date', 'Birth', 'College','Exp']]

    final_player_seasons_df = final_player_seasons_df.merge(final_players_df, on='Player', how='inner')
    final_player_seasons_df.drop(columns=['Age', 'Pos', 'Ht', 'Wt', 'Birth', 'Birth Date', 'College', 'Awards','Player'], inplace=True)
    final_player_seasons_df.insert(0, 'id', final_player_seasons_df.pop('id'))
    final_players_df.drop(columns='Exp', inplace=True)

    final_player_seasons_df.to_csv("Player_Seasons.csv", index=False)
    final_players_df.to_csv("Players.csv", index=False)
    print("Saved")



