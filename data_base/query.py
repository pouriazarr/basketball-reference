import sqlite3
import pandas as pd

conn = sqlite3.connect('nba_database.db')

# write your query here
query = '''SELECT * FROM players
LIMIT 5;'''
df = pd.read_sql_query(query, conn)
print(df.to_string(index=False))

conn.close()