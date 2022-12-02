import simplejson as  json

from django.shortcuts import render
from django.http import HttpResponse

import decimal
import datetime
from django.core.cache import cache


def get_fromcache(k):
    return cache.get(k)


def put2cache(q, k, t=300):
    cache.set(k, q,  t)

def json_true(req, dictt=None):
   
    d  = {"status": True}    
    resp = None
    if not dictt is None:
        resp = {**d, **dictt}
    else:
        resp = d
    resp = json_dumps(resp) 
    if req.GET.get("html", ""):
        return render(req, "json.html", {"data": resp}) 


    return HttpResponse(resp, headers={"Content-Type": "application/json"})

def json_500false(req, dicct):
    
    d  = {"status": False}    
    resp = None
    if not dicct is None:
        resp = {**d, **dicct}
    else:
        resp = d

    resp = json_dumps(resp) 
    if req.GET.get("html", "") :
        return render(req, "json.html", {"data": resp}) 

    return HttpResponse(resp, status_code=500, headers={"Content-Type": "application/json"})

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        print(o)
        if isinstance(o, decimal.Decimal):
        # wanted a simple yield str(o) in the next line,
        # but that would mean a yield on the line with super(...),
        # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        
        if isinstance(o, datetime.datetime):
            return (str(o) for o in [o])

        if isinstance(o, datetime.date):
            return (str(o) for o in [o])

        return super(DecimalEncoder, self).default(o)


def jsonencoder(o):

    if isinstance(o, datetime.datetime):
        return str(o)

    if isinstance(o, datetime.date):
        return str(o)

    return json.JSONEncoder.default(o)


def json_dumps(diccc=None):        
    if diccc is None:
        return "{}" #))
    #return json.dumps(diccc, cls=DecimalEncoder)
    return json.dumps(diccc, default=jsonencoder)




