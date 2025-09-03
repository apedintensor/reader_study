import sqlite3, os
path='test.db'
print('DB exists?', os.path.exists(path))
conn=sqlite3.connect(path)
cur=conn.cursor()
cur.execute('PRAGMA table_info(block_feedback)')
cols=cur.fetchall()
print('block_feedback columns:')
for c in cols:
    print(c)
