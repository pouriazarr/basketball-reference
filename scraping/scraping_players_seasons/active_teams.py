from selenium import webdriver
from selenium.webdriver.common.by import By
from seasons import get_season_data

URL = "https://www.basketball-reference.com/teams/"
options = webdriver.ChromeOptions()
options.page_load_strategy = "eager"
browser = webdriver.Chrome(options=options)

try:
    browser.get(URL)
    table = browser.find_element(By.CSS_SELECTOR, 'table#teams_active')
    # print("Table tag:", table.tag_name)
    thead = table.find_element(By.TAG_NAME, 'thead')
    header_row = thead.find_element(By.TAG_NAME, 'tr')
    headers = [th.text for th in header_row.find_elements(By.TAG_NAME, 'th')]
    # print("Headers:", headers)
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    rows = tbody.find_elements(By.TAG_NAME, 'tr')

    teams = []
    for row in rows:
        cells = row.find_elements(By.XPATH, './*')
        if not cells:
            continue
        first_cell = cells[0]
        link = first_cell.find_elements(By.TAG_NAME, 'a')
        if not link:
            continue
        teams_text = link[0].text.strip()
        teams_link = link[0].get_attribute("href")
        teams.append((teams_text, teams_link))
        print(link[0].get_attribute('href'))
    get_season_data(browser,teams)
finally:
    browser.quit()
