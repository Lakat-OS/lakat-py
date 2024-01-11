from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import lakat.branch.functions as lakat_branch_functions
from lakat.branch.schema import create_genesis_branch_call, create_genesis_branch_response
import lakat.storage.local_storage as lakat_storage
import lakat.submit.functions as lakat_submit_functions
import lakat.submit.schema as lakat_submit_schema
import lakat.storage.getters_schema as lakat_getters_schema
import lakat.storage.getters as lakat_getters

from config.encode_cfg import ENCODING_FUNCTION
from config.rpc_cfg import RPC_PORT
from utils.encode.language import encode_string
from utils.encode.bytes import key_encoder
from utils.format.schema import check_argument, convert_to_bytes_based_on_schema, convert_from_bytes_based_on_schema
from utils.format.rpc_call import wrap_rpc_call
import math

from jsonrpc import JSONRPCResponseManager, dispatcher

@dispatcher.add_method
def create_genesis_branch(branch_type: int, name: str, signature: str, accept_conflicts: bool, msg: str):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_type=branch_type, name=name, signature=signature, accept_conflicts=accept_conflicts, msg=msg)
    # return call
    return wrap_rpc_call(
        function=lakat_branch_functions.create_genesis_branch,
        call_schema=create_genesis_branch_call,
        response_schema=create_genesis_branch_response,
        kwargs=kwargs)


@dispatcher.add_method
def submit_content_to_twig(branch_id: str, contents: any, public_key: str, proof: str, msg: str):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_id, contents=contents, public_key=public_key, proof=proof, msg=msg)
    # return call
    return wrap_rpc_call(
        function=lakat_submit_functions.submit_content_for_twig,
        call_schema=lakat_submit_schema.submit_content_for_twig_call,
        response_schema=lakat_submit_schema.submit_content_for_twig_response,
        kwargs=kwargs)

@dispatcher.add_method
def get_branch_name_from_branch_id(branch_id: str):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_id)
    # return call
    return wrap_rpc_call(
        function=lakat_getters.get_branch_name_from_branch_id,
        call_schema=lakat_getters_schema.get_branch_name_from_branch_id, ## TODO: get rid of the response schema
        response_schema=lakat_getters_schema.get_branch_name_from_branch_id["response"],
        kwargs=kwargs)



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
    run_simple('0.0.0.0', RPC_PORT, application)
