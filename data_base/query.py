import sqlite3
import pandas as pd

conn = sqlite3.connect('nba_database.db')

# write your query
query = ''' SELECT * FROM mvp_candidates;'''
df = pd.read_sql_query(query, conn)
print(df.to_string(index=False))

conn.close()