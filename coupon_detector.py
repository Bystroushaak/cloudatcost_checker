#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import json
import argparse

import dhtmlparser
from httpkie import Downloader


# Variables ===================================================================
DOWNER = Downloader()
BASE_URL = "https://members.cloudatcost.com"


# Functions & objects =========================================================
def get_item_id(data):
    dom = dhtmlparser.parseString(data)
    link = dom.find("a", fn=lambda x: x.getContent() == "Apply Coupon")

    if not link or "onclick" not in link[0].params:
        raise ValueError("Can't find coupon code!")

    iid = link[0].params["onclick"]

    return iid.split("'")[1]


def get_ghash(data):
    data = data.splitlines()
    data = filter(lambda x: "gHash =" in x, data)

    if not data:
        raise ValueError("Can't locate gHash!")

    ghash = data[0].split("=", 1)[-1].strip()

    return ghash.split('"')[1]  # remove quotes


def check_coupon(coupon_code):
    DOWNER.download(BASE_URL + "/order.php?step=1&productGroup=4")
    DOWNER.download(
        BASE_URL + "/order.php?step=2",
        post={
            "productGroup": "4",
            "product": "6",
            "formId": "packageSelect",
            "priceTerm": "0"
        }
    )
    data = DOWNER.download(
        BASE_URL + "/order.php?step=4",
        post={
            "formId": "configureProduct",
            "product": "6",
            "PCT_45": "",
            "addonSelect_1": "addon_1_27_0"
        }
    )

    item_id = get_item_id(data)
    DOWNER.headers["Referer"] = BASE_URL + "/order.php?step=4"
    DOWNER.headers["X-Requested-With"] = "XMLHttpRequest"
    DOWNER.headers["X-Session-Hash"] = get_ghash(data)

    data = DOWNER.download(
        BASE_URL + "/index.php?fuse=admin&action=validateCoupon",
        post={
            "couponCode": coupon_code,
            "itemID": item_id
        }
    )

    json_data = json.loads(data)

    return json_data["success"]


def test_check_coupon():
    test_cases = [
        "BIGGER50",
        "BIGGER75",
        "OMGFREE"
    ]

    for coupon_code in test_cases:
        print coupon_code, test_coupon(coupon_code)


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""This script is used to check coupons @ Cloud At Cost.
                       In other words: This can get you server for free!"""
    )
    parser.add_argument(
        "coupon",
        help="Code of the coupon."
    )

    args = parser.parse_args()

    result = check_coupon(args.coupon)

    print result
    sys.exit(1 - int(result))  # convert python's True to bash's true
