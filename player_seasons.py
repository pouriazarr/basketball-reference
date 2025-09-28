from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import unicodedata

def correct_name(x):
    if pd.isna(x):
        return x
    s = str(x)
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8')

def get_player_data(browser,team,season_list):
    print(team)
    player_seasons = []
    players = []
    for season_year, season_url in season_list:
        per_game_data_rows = []
        browser.get(season_url)
        per_game_table = browser.find_element(By.CSS_SELECTOR, 'table#per_game_stats')
        per_game_tbody = per_game_table.find_element(By.TAG_NAME, 'tbody')
        per_game_rows = per_game_tbody.find_elements(By.TAG_NAME, 'tr')
        per_game_thead = per_game_table.find_element(By.TAG_NAME, 'thead')
        per_game_header_row = per_game_thead.find_element(By.TAG_NAME, 'tr')
        per_game_headers = [th.text for th in per_game_header_row.find_elements(By.TAG_NAME, 'th')]
        for row in per_game_rows:
            cells = row.find_elements(By.XPATH, './*')
            if not cells:
                continue
            per_game_row_data = [cell.text.strip() for cell in cells]
            # print(per_game_row_data)
            per_game_row_data.append(team)
            per_game_row_data.append(season_year)
            per_game_data_rows.append(per_game_row_data)

        per_game_headers = per_game_headers + ['Team'] + ['Season']
        per_game_df = pd.DataFrame(per_game_data_rows, columns=per_game_headers)
        per_game_df.drop(columns=['Rk','Pos'], inplace=True)
        per_game_df['Player'] = per_game_df['Player'].apply(correct_name)

        player_data_rows = []
        player_table = browser.find_element(By.CSS_SELECTOR, 'table#roster')
        player_tbody = player_table.find_element(By.TAG_NAME, 'tbody')
        player_rows = player_tbody.find_elements(By.TAG_NAME, 'tr')
        player_thead = player_table.find_element(By.TAG_NAME, 'thead')
        player_header_row = player_thead.find_element(By.TAG_NAME, 'tr')
        player_headers = [th.text for th in player_header_row.find_elements(By.TAG_NAME, 'th')]
        for row in player_rows:
            cells = row.find_elements(By.XPATH, './*')
            if not cells:
                continue
            player_row_data = [cell.text.strip() for cell in cells]
            player_data_rows.append(player_row_data)

        player_df = pd.DataFrame(player_data_rows, columns=player_headers)
        player_df.drop(columns='No.', inplace=True)
        player_df['Player'] = player_df['Player'].apply(correct_name)

        salaries_data_rows = []
        salaries_table = browser.find_element(By.CSS_SELECTOR, 'table#salaries2')
        salaries_tbody = salaries_table.find_element(By.TAG_NAME, 'tbody')
        salaries_rows = salaries_tbody.find_elements(By.TAG_NAME, 'tr')
        salaries_thead = salaries_table.find_element(By.TAG_NAME, 'thead')
        salaries_header_row = salaries_thead.find_element(By.TAG_NAME, 'tr')
        salaries_headers = [th.text for th in salaries_header_row.find_elements(By.TAG_NAME, 'th')]
        salaries_headers[1] = 'Player'
        for row in salaries_rows:
            cells = row.find_elements(By.XPATH, './*')
            if not cells:
                continue
            salaries_row_data = [cell.text.strip() for cell in cells]
            salaries_data_rows.append(salaries_row_data)

        salaries_df = pd.DataFrame(salaries_data_rows, columns=salaries_headers)
        salaries_df.drop(columns='Rk', inplace=True)

        # df = per_game_df.merge(player_df, how='inner', on='Player')
        per_game_df = per_game_df.merge(salaries_df, how='left',on='Player')
        # df.drop(columns=['Age','Pos','Ht','Wt','Birth','Birth Date','College','Awards'], inplace=True)
        # player_df.drop(columns='Exp', inplace=True)

        player_seasons.append(per_game_df)
        players.append(player_df)
    if player_seasons and players:
        final_player_seasons_df = pd.concat(player_seasons, ignore_index=True)
        final_players_df = pd.concat(players, ignore_index=True)
        return final_player_seasons_df,final_players_df
    else:
        print(f"No data found for {team}")


