#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Displays the Bitcoin price at coincheck & upbit
"""

import os
import sys
import time

try:
    import requests
except ImportError:
    print("The requests library was not found. Run 'sudo -H pip install requests' to install it.")
    sys.exit()

from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont

coincheck_url = "https://coincheck.com/api/ticker"
upbit_url = "https://api.upbit.com/v1/ticker?markets=KRW-BTC"

def fetch_price(url):
    try:
        r = requests.get(url)
        return r.json()
    except:
        print("Error fetching from ".url)


def get_price_coincheck():
    data = fetch_price(coincheck_url)
    return [
        'BTC/JPY {}'.format(data['last']),
        '{}/{}'.format(data['high'], data['low'])
    ]


def get_price_upbit():
    data = fetch_price(upbit_url)[0]
    return [
        'BTC/KRW {}'.format(data['trade_price']),
        '{}/{}'.format(data['high_price'], data['low_price'])
    ]


def show_price(device):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 12)

    with canvas(device) as draw:
        rows = get_price_coincheck()
        draw.text((0, 0), rows[0], font=font2, fill="white")
        draw.text((0, 14), rows[1], font=font2, fill="white")

        if device.height >= 64:
            rows = get_price_upbit()
            draw.text((0, 32), rows[0], font=font2, fill="white")
            draw.text((0, 46), rows[1], font=font2, fill="white")


def main():
    while True:
        show_price(device)
        time.sleep(60)


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
