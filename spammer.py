#!/usr/bin/env python3
import argparse
import hyper
import json
import re
import requests
import socket
import sys

from json.decoder import JSONDecodeError
from requests.exceptions import RequestException
from urllib.parse import urlencode

from response import generate_response


pattern = re.compile('var FB_PUBLIC_LOAD_DATA_ = (.*);', re.DOTALL)
headers = {'Content-type': 'application/x-www-form-urlencoded'}


def main():
    parser = argparse.ArgumentParser(description='Spams a Google Form.')
    parser.add_argument('url', help='the url of the form to spam')
    parser.add_argument('--window-size', type=int, default=10,
                        help='number of requests to send at once')
    args = parser.parse_args()

    try:
        r = requests.get(args.url)
        r.raise_for_status()
    except RequestException as e:
        sys.exit(e)

    match = pattern.search(r.text)
    try:
        form = json.loads(match.group(1))
    except (AttributeError, JSONDecodeError):
        sys.exit('Could not parse form data.')

    action = '/forms/d/%s/formResponse' % form[14]
    success = fail = 0

    c = hyper.HTTPConnection('docs.google.com:443')

    while True:
        status = 'Successful: %i, Failed: %i' % (success, fail)
        print(status, flush=True, end='\r')

        r = [send_request(c, action, form) for _ in range(args.window_size)]

        for request in r:
            try:
                resp = c.get_response(request)
                if resp.status is not 200:
                    raise ValueError('invalid response from server')
                text = resp.read().decode('utf-8')
                if pattern.search(text):
                    raise ValueError('form response rejected')
                success += 1
            except (ValueError, ConnectionError, socket.timeout):
                fail += 1


def send_request(conn, action, form):
    params = generate_response(form)
    encoded = urlencode(params).encode('utf-8')
    return conn.request('POST', action, encoded, headers)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
