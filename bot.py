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
test_exchange_index=1
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

def send(option, sym, price, size, exchange):
    global id_num
    req = {"type": "add", "order_id": id_num, "symbol": sym, "dir": option.upper(), "price": price, "size": size}
    id_num += 1
    print(req)
    write_to_exchange(exchange, req)

def add_action(symbol, option, price, size, exchange):
    global id_num
    id_num += 1
    request = {"type": "add", "order_id": id_num, "symbol": symbol,
    "dir": option, "price": price, "size": size}
    print(request)
    write_to_exchange(exchange, request)

def convert_action(exchange, symbol, size, option):
    global id_num
    id_num += 1
    request = {"type": "convert", "order_id": id_num, "symbol": symbol, "dir": option,
    "size": size}
    print(request)
    write_to_exchange(exchange, request)

def cancel_action(exchange):
    global id_num
    id_num += 1
    request = {"type": "cancel", "order_id": id_num}
    print(request)
    write_to_exchange(exchange, request)

def avg(lst):
    if len(lst) == 0:
        return -1
    return sum([l[0] * l[1] for l in lst]) / (sum([l[1] for l in lst]) + 0.0)

def etf_running_avg(mat, lst):
    lst = [avg(lst), sum([l[1] for l in lst])]
    mat.append(lst)
    if len(mat) > 5:
        del mat[0]

def weighted_sum(weights, vals):
    return sum([weights[k] * vals[k] for k in vals.keys()])

# ~~~~~============== MAIN LOOP ==============~~~~~

bond = 'BOND'
vale = 'VALBZ'
valbz = 'VALE'
gs = 'GS'
ms = 'MS'
wfc = 'WFC'
xlf = 'XLF'
count_dic = {bond: 0, valbz: 0, vale: 0, gs: 0, ms: 0, wfc: 0, xlf: 0, vale: 0, valbz: 0}

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("the exchange replied" , hello_from_exchange,file=sys.stderr)
    print_from_exchange(exchange)
    bond_price = 1000
    valbz_vale_buys = {valbz: 0, vale: 0}
    valbz_vale_sells = {valbz: 0, vale: 0}

    while True:
        data = read_from_exchange(exchange)
        print(data)
        if u'error' in data and data[u'error'] == u'TRADING_CLOSED':
            quit()
        if u'symbol' in data and u'sell' in data and data[u'symbol'] == bond:
            buy, sell = data[u'buy'], data[u'sell'] 
            avg_sell = int(avg(sell))
            avg_buy = int(avg(buy))
            if avg_sell > bond_price:
                send('sell', bond, avg_sell, 1, exchange)
            if avg_buy < bond_price:
                send('buy', bond, avg_buy, 1, exchange)
        if data and data[u'type'] == 'fill':
            count_dic[data[u'symbol']] += int(data[u'size']) * (-1 if data[u'dir'] == 'SELL' else 1)
        elif data and data[u'type'] == 'trade' and data[u'symbol'] in valbz_vale_buys.keys():
            valbz_vale_buys[data[u'symbol']] = int(data[u'price'])
            valbz_vale_sells[data[u'symbol']] = int(data[u'price'])
        elif data and u'symbol' in data and u'sell' in data:
            buys, sells = data[u'buy'], data[u'sell']
            avg_sell = int(avg(sells))
            avg_buy = int(avg(buys))
            if False: #etf stocks case initial
                print()
            elif False: #etf stocks case where none have value 0
                print()
            elif data[u'symbol'] in valbz_vale_buys.keys():
                number = 8
                diff = 11
                if count_dic[vale] > number:
                    convert(exchange, vale, count_dic[vale], 'sell')
                elif count_dic[vale] < -number:
                    convert(exchange, vale, -count_dic[vale], 'buy')
                if count_dic[valbz] > number:
                    convert(exchange, valbz, count_dic[valbz], 'sell')
                elif count_dic[valbz] < -number:
                    convert(exchange, valbz, count_dic[valbz], 'buy')
                if valbz_vale_buys[valbz] > diff + valbz_vale_buys[vale]:
                    send('buy', vale, valbz_vale_buys[vale], 1, exchange)
                    send('sell', valbz, valbz_vale_sells[valbz], 1, exchange)
                elif valbz_vale_sells[vale] > diff + valbz_vale_sells[valbz]:
                    send('sell', vale, valbz_vale_sells[vale], 1, exchange)
                    send('buy', valbz, valbz_vale_buys[valbz], 1, exchange)
                if valbz_vale_buys[vale] > diff + valbz_vale_buys[valbz]:
                    send('buy', valbz, valbz_vale_buys[valbz], 1, exchange)
                    send('sell', vale, valbz_vale_sells[vale], 1, exchange)
                elif valbz_vale_sells[valbz] > diff + valbz_vale_sells[vale]:
                    send('sell', valbz, valbz_vale_sells[valbz], 1, exchange)
                    send('buy', vale, valbz_vale_buys[vale], 1, exchange)
if __name__ == "__main__":
    main()
