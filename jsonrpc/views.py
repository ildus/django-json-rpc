from _json import dumps
from django.http import HttpResponse
from django.shortcuts import render_to_response
from jsonrpc.site import jsonrpc_site
from jsonrpc import mochikit
from django.core.urlresolvers import reverse


def browse(request):
    if (request.GET.get('f', None) == 'mochikit.js'):
        return HttpResponse(mochikit.mochikit, content_type='application/x-javascript')
    if (request.GET.get('f', None) == 'interpreter.js'):
        return HttpResponse(mochikit.interpreter, content_type='application/x-javascript')
    desc = jsonrpc_site.service_desc()
    return render_to_response('browse.html', {
                              'methods': desc['procs'],
                              'method_names_str': dumps(
                                  [m['name'] for m in desc['procs']])
                              })


def smd(request):
    def get_args(method):
        from inspect import getargspec
        return [a for a in getargspec(method).args if a != "self"]

    smd = {
        "serviceType": "JSON-RPC",
        "serviceURL": reverse("jsonrpc_mountpoint"),
        "methods": []
    }

    #TODO: write smd handler
    return HttpResponse(dumps(smd), mimetype="application/json")
