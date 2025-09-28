import sqlite3
import pandas as pd

conn = sqlite3.connect('nba_database.db')

# write your query
query = '''SELECT * FROM player_seasons
WHERE team_id = 4 and season_id = 3
LIMIT 5;'''
df = pd.read_sql_query(query, conn)
print(df.to_string(index=False))

conn.close()