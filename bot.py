#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
from time import sleep

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="THEREVENGERS"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=2
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def print_from_exchange(exchange):
    print(read_from_exchange(exchange))

id_num = 0

def do(option, sym, price, size, exchange):
    global id_num
    req = {"type": "add", "orderid_num": id_num, "symbol": sym, "dir": option.upper(), "price": price, "size": size}
    id_num += 1
    print(req)
    write_to_exchange(exchange, req)

def avg(lst):
    if len(lst) == 0:
        return -1
    return sum([l[0] * l[1] for l in lst]) / (sum([l[1] for l in lst]) + 0.0)

def add_action(symbol, option, price, size, exchange):
    global id_num
    id_num += 1
    request = {"type": "add", "orderid_num": id_num, "symbol", symbol,
    "dir": option, "price": price, "size": size}
    print(request)
    write_to_exchange(exchange, request)

def convert_action(exchange, symbol, size, option):
    global id_num
    id_num += 1
    request = {"type": "convert", "orderid_num", id_num, "symbol": symbol, "dir": option,
    "size": size}
    print(request)
    write_to_exchange(exchange, request)

def cancel_action(exchange):
    global id_num
    id_num += 1
    request = {"type": "cancel", "orderid_num", id_num}
    print(request)
    write_to_exchange(exchange, request)

#write functions for sums, averages, etc

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    # print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    #    do('buy', u'BOND', 1000, 1, exchange)
    print_from_exchange(exchange)
    stock = u'BOND'
    fair_price = 1000
    while True:
        data = read_from_exchange(exchange)
        print(data)
        if u'symbol' in data and u'sell' in data and data[u'symbol'] == stock:
            buy, sell = data[u'buy'], data[u'sell']
            avg_sell = int(avg(sells))
            avg_buy = int(avg(buys))
            if avg_buy < fair_price:
                do('buy', stock, avg_buy, 1, exchange)
            if avg_sell > fair_price:
                do('sell', stock, avg_sell, 1, exchange)
if __name__ == "__main__":
    main()
