#coding: utf-8

from django.conf import settings

LIMIT = getattr(settings, 'JSONRPC_LIST_MAX_QUANTITY', 50)
ASC, DESC = 0, 1


def handle_list(request,
                model=None, queryset=None,
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
    else:
        raise Exception("need model or queryset")

    if direction == DESC:
        order_by = '-' + order_by
    qs = qs.order_by(order_by)[start:start + limit]

    def build_struct(obj):
        if build_obj_struct:
            return build_obj_struct(obj)

        if hasattr(obj, 'as_dict') and callable(obj.as_dict):
            return obj.as_dict()

        return {'id': obj.pk}

    result = {'totalcount': qs.count()}
    result['records'] = [build_struct(obj) for obj in qs]
    return result
