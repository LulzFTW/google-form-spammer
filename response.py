import random
import string

from functools import partial


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


def randstr(size=100, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
