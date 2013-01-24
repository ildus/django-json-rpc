#coding: utf-8

from django.conf import settings
from django.utils.translation import gettext as _
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
import exceptions

LIMIT = getattr(settings, 'JSONRPC_LIST_MAX_QUANTITY', 50)
ASC, DESC = 0, 1


def handle_list(request,
                model=None, queryset=None,
                collection=None,
                start=0, limit=LIMIT, direction=ASC,
                build_obj_struct=None,
                order_by='id'):

    ''' list helper, returns struct like:
            {'totalcount': 10, 'records':[{'id': 1, 'name': 'one'}, ...]}
    '''

    assert direction in (ASC, DESC)
    assert model or (queryset is not None)

    if model:
        qs = model._default_manager.all()
    elif queryset is not None:
        qs = queryset
    elif collection is not None:
        qs = collection
    else:
        raise Exception("need model or queryset")

    totalcount = 0
    if not collection:
        totalcount = qs.count()
        if isinstance(order_by, basestring):
            if direction == DESC:
                order_by = '-' + order_by
            qs = qs.order_by(order_by)
        elif isinstance(order_by, (list, tuple)):
            qs = qs.order_by(*order_by)
        qs = qs[start:start + limit]
    else:
        totalcount = len(qs)
        qs = qs[start:start + limit]

    def build_struct(obj):
        if build_obj_struct:
            return build_obj_struct(obj)

        if hasattr(obj, 'as_dict') and callable(obj.as_dict):
            return obj.as_dict()

        return {'id': obj.pk}

    result = {'totalcount': totalcount}
    result['records'] = [build_struct(obj) for obj in qs]
    return result


DICT_REQUIRED = _("An empty structure or is not dictionary")
PARAM_IS_REQUIRED = _("%(param)s is required for this request")
INVALID_BOOLEAN = _("Invalid boolean value")
VALUE_ISNT_POSSIBLE = _("The value is not in possible values")


def parse_int(struct, param, default=None, possible_values=None):
    try:
        val = int(struct.get(param, default))
    except:
        val = default

    if default is None and val is None:
        raise exceptions.InvalidParamsError

    if possible_values and val not in possible_values:
        raise exceptions.InvalidParamsError(VALUE_ISNT_POSSIBLE)

    return val


def parse_bool(struct, param, required=True):
    val = struct.get(param)
    if val is None and required:
        raise exceptions.InvalidParamsError(PARAM_IS_REQUIRED % {'param': param})

    if val not in (True, False, None):
        raise exceptions.InvalidParamsError(INVALID_BOOLEAN)

    return val


def parse_sort(struct, param, ordering_fields, default='id'):
    sort = struct.get(param)
    order_by = default
    if sort and isinstance(sort, basestring):
        desc = (sort and sort[0] == '-')
        if desc:
            sort = sort[1:]
        if sort and sort in ordering_fields:
            order_by = '%s%s' % ('-' if desc else '', ordering_fields[sort])

    return order_by


class RpcJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return unicode(o)
        else:
            return super(RpcJSONEncoder, self).default(o)
