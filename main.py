from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import lakat.branch as lakat_branch
import lakat.storage as lakat_storage

from config.encode_cfg import ENCODING_FUNCTION
from utils.encode.language import encode_string
from utils.encode.bytes import key_encoder

import math

from jsonrpc import JSONRPCResponseManager, dispatcher

@dispatcher.add_method
def create_genesis_branch(branch_type: int, signature: str, accept_conflicts: bool, msg: str):
    signature_bytes=signature.encode(ENCODING_FUNCTION)
    encoded_msg=encode_string(msg, ENCODING_FUNCTION)
    branchId = lakat_branch.create_genesis_branch(branch_type, signature_bytes, accept_conflicts, encoded_msg)
    return key_encoder(branchId)

@dispatcher.add_method
def restart_db_with_name(name: str):
    print("restart_db_with_name", name)
    return lakat_storage.restart_db_with_name(name=name)

@dispatcher.add_method
def restart_db():
    return lakat_storage.restart_db()

@dispatcher.add_method
def say_hello():
    return "Hello, World!"

@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(request.data, dispatcher)
    return Response(response.json, mimetype='application/json', )

if __name__ == '__main__':
    run_simple('0.0.0.0', 4000, application)
