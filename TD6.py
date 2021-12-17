import requests
import sqlite3
import json
from enum import Enum
import hmac
from typing import Dict
import hashlib
import time

binance="https://api.binance.com"
api_key=""
secret_key=""

class Interval(Enum):
    minutes = { 1 :'1m',3:'3m',5:'5m',15:'15m',30:'30m'}
    heures = { 1 : '1h',2: '2h',4: '4h',6: '6h',8: '8h',12: '12h'}
    days ={1 : '1d',3:'3d'}
    semaine = '1w'
    mois ='1m'
    
def listcrypto():
    response=requests.get(binance+'/api/v3/exchangeInfo')
    txt=response.text
    data=txt.split('symbols":[{"symbol":')[1]
    splitdata=data.split('},{"symbol":')
    return splitdata    

def getOrderBook(pair,limit):
    r=requests.get(binance + "/api/v3/depth?symbol=" + pair +"&limit=" + str(limit))
    return (r.json()['asks'],r.json()['bids'])
    
def insertCandlesbdd(a,connection):
    cursor = connection.cursor()
    request = f"insert into candles (openTime ,open , high ,low , close ,volume ,closeTime) values ({a[0]},{a[1]},{a[2]},{a[3]},{a[4]},{a[5]},{a[6]})"
    cursor.execute(request)
    connection.commit()


def refreshDataCandle(pair,duration):
    r = requests.get(binance+ "/api/v3/klines?symbol=" + pair +"&interval=" +duration)
    connection = sqlite3.connect('ApiBinance.db')
    for a in r.json():
        insertCandlesbdd(a,connection)
    connection.close()

def refreshData(pair):
    headers = {
        'Content-Type': 'application/json',
        'X-MBX-APIKEY': api_key
    }
    r = requests.get(binance + "/api/v3/historicalTrades?symbol=" + pair,headers=headers)
    connection = sqlite3.connect('ApiBinance.db')
    print(r.json()[0])
    for a in r.json():
        tradesdata(a,connection)
    connection.close()
    
def tradesdata(a,connection):
    cursor = connection.cursor()
    request = f"insert into trades (idTrade ,price , qty ,quoteqty , time ,isBuyerMaker ,isbestMatch ) values ({a['id']},{a['price']},{a['qty']},{a['quoteQty']},{a['time']},{a['isBuyerMaker']},{a['isBestMatch']})"
    cursor.execute(request)
    connection.commit()
    
def createOrder(api_key, secret_key,direction,price,amount,pair,orderType):
    timestamp = requests.get(binance + "/api/v3/time").json()["serverTime"]
    query_string = "symbol="+pair+"&side="+direction+"&type="+orderType +"&timeInForce=GTC&quantity="+amount+ "&price="+price+ "&timestamp="+str(timestamp)
    signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {
        'Content-Type': 'application/json',
        'X-MBX-APIKEY': api_key
    }
    r = requests.post(binance + "/api/v3/order?"
                      + "symbol="+pair
                      + "&side="+direction
                      + "&type="+orderType
                      + "&timeInForce=GTC"
                      + "&quantity="+amount
                      + "&price="+price
                      + "&timestamp="+str(timestamp)
                      + "&signature="+signature,headers=headers)
    print(r.json())
    return r.json()

def cancelOrder(api_key,secret_key,uuid,pair):
    timestamp = requests.get(binance + "/api/v3/time").json()["serverTime"]
    query_string = "symbol="+pair+"&orderId="+uuid+"&timestamp="+str(timestamp)
    signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {
        'Content-Type': 'application/json',
        'X-MBX-APIKEY': api_key
    }
    r=requests.delete(binance+"/api/v3/order?symbol="+pair+"&orderId="+uuid+"&timestamp="+str(timestamp)+"&signature="+signature,headers=headers)
    print(r.text)
     
if __name__ == '__main__':
    listcrypto()
    #getOrderBook("BTCUSDT",50)
    #refreshDataCandle('BTCUSDT',Interval['minutes'].value[5])
    #refreshData("BTCUSDT")
    #createOrder()
