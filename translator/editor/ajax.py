from functools import wraps
import json
from django.http import HttpResponse


def json_view(view):

    @wraps(view)
    def inner_view(request, *args, **kwargs):
        deserialized = json.loads(request.body)
        response = view(deserialized, request, *args, **kwargs)
        serialized = json.dumps(response)
        return HttpResponse(serialized, content_type='application/json', status=200)

    return inner_view
