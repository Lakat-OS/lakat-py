from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from lakat.submit import content_submit
import math

from jsonrpc import JSONRPCResponseManager, dispatcher

@dispatcher.add_method
def submit(x):
    return content_submit()

@dispatcher.add_method
def say_hello():
    return "Hello, World!"

@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(request.data, dispatcher)
    return Response(response.json, mimetype='application/json')

if __name__ == '__main__':
    run_simple('localhost', 4000, application)
