#coding: utf-8

from datetime import date, datetime
from exceptions import InvalidParamsError


def convert_value(p, ptype):
    if ptype == 'boolean':
        p = p.lower()
        assert p in ('true', 'false', 'on', 'off')
        p = (p == 'true') or (p == 'on')
    elif ptype == 'comma_separated':
        p = p.split(',')
    elif ptype in ('date', date):
        p = datetime.strptime(p, "%Y-%m-%d").date()
    elif ptype in ('datetime', datetime):
        p = datetime.strptime(p, "%Y-%m-%d %H:%M")
    elif isinstance(ptype, (tuple, list)):
        assert type(p) in ptype
    elif isinstance(ptype, dict):  # {'in': (int, xrange(7))}
        for condition, data in ptype.iteritems():
            assert type(data[0]) is type, "first item must be type of parameter in %s" % data
            p = data[0](p)
            if condition == 'in':
                iter = data[1]
                if callable(iter):
                    iter = iter()

                assert p in iter, "%s must be in %s" % (p, iter)
    elif ptype == 'list_of_int':
        numbers = p.split(',')
        try:
            p = [long(number.strip()) for number in numbers]
        except:
            raise InvalidParamsError
    elif ptype == 'list_of_positive':
        numbers = p.split(',')
        try:
            p = [long(number.strip()) for number in numbers]
            p = filter(lambda n: n >= 0, p)
        except:
            raise InvalidParamsError
    else:
        p = ptype(p)

    return p
