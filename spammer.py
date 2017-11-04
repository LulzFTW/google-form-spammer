#!/usr/bin/env python3
import argparse
import hyper
import json
import random
import re
import requests
import socket
import string
import sys
import time
import urllib.parse

from functools import partial
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException

pattern = re.compile('var FB_PUBLIC_LOAD_DATA_ = (.*);', re.DOTALL)


def main():
    parser = argparse.ArgumentParser(description='Spams a Google Form.')
    parser.add_argument('url', help='the url of the form to spam')
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

    try:
        while True:
            status = 'Successful: %i, Failed: %i' % (success, fail)
            print(status, flush=True, end='\r')

            try:
                params = generate_response(form)
                data = urllib.parse.urlencode(params).encode('utf-8')
                headers = {'Content-type': 'application/x-www-form-urlencoded'}

                c.request('POST', action, data, headers)
                resp = c.get_response()
                text = resp.read().decode('utf-8')

                if pattern.search(text):
                    fail += 1
                else:
                    success += 1
            except socket.timeout:
                fail += 1
    except KeyboardInterrupt:
        print()


def field_text(id, params, post_data):
    add_entry(id, randstr(), post_data)


def field_choice(id, params, post_data, single=True):
    k = 1 if single else random.randint(1, len(params))
    items = random.sample([x[0] for x in params], k=k)
    for item in items:
        other = not item
        item = item or randstr()
        add_entry(id, item, post_data, other=other)

def field_date(id, params, post_data):
    pass


def field_time(id, params, post_data):
    pass


handlers = {
    0: field_text,                           # short answer
    1: field_text,                           # paragraph
    2: field_choice,                         # multiple choice
    3: field_choice,                         # dropdown
    4: partial(field_choice, single=False),  # checkbox
    5: field_choice,                         # linear scale
    7: field_choice                          # multiple choice grid
}


def generate_response(form):
    data = []
    for section in form[1][1]:
        type = section[3]
        if type in handlers:
            for field in section[4]:
                handlers[type](field[0], field[1], data)
    return data


def add_entry(id, value, post_data, other=False):
    name = 'entry.%i' % id
    if other:
        post_data.append((name, '__other_option__'))
        post_data.append((name + '.other_option_response', value))
    else:
        post_data.append((name, value))


def randstr(size=100, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

if __name__ == '__main__':
    main()
