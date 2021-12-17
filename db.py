import sqlite3
conn = sqlite3.connect('ApiBinance.db')
cur = conn.cursor()
#req = "create table candles(id integer primary key autoincrement,openTime int,open text, high text,low text, close text,volume text,closeTime int)"
req = "create table trades(id integer primary key autoincrement,idTrade int,price text, qty text,quoteqty text, time int,isBuyerMaker text,isbestMatch text)"
cur.execute(req)
conn.commit()