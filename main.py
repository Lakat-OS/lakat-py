from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import lakat.branch.functions as lakat_branch_functions
import lakat.storage.local_storage as lakat_storage
import lakat.submit.functions as lakat_submit_functions
import inspection.articles as inspection_articles
import inspection.branch as inspection_branch

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
        schema=lakat_branch_functions.create_genesis_branch_schema,
        kwargs=kwargs)


@dispatcher.add_method
def submit_content_to_twig(branch_id: str, contents: any, public_key: str, proof: str, msg: str):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_id, contents=contents, public_key=public_key, proof=proof, msg=msg)
    # return call
    return wrap_rpc_call(
        function=lakat_submit_functions.submit_content_for_twig,
        schema=lakat_submit_functions.submit_content_for_twig_schema,
        kwargs=kwargs)


@dispatcher.add_method
def get_branch_name_from_branch_id(branch_id: str):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_id)
    # return call
    return wrap_rpc_call(
        function=inspection_branch.get_branch_name_from_branch_id,
        schema=inspection_branch.get_branch_name_from_branch_id_schema,
        kwargs=kwargs)


@dispatcher.add_method
def get_branch_data_from_branch_id(branch_id: str, deserialize_buckets: bool):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_id, deserialize_buckets=deserialize_buckets)
    # return call
    return wrap_rpc_call(
        function=inspection_branch.get_branch_data_from_branch_id,
        schema=inspection_branch.get_branch_data_from_branch_id_schema,
        kwargs=kwargs)


@dispatcher.add_method
def get_branch_data_from_branch_state_id(branch_state_id: str, deserialize_buckets: bool):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_state_id, deserialize_buckets=deserialize_buckets)
    # return call
    return wrap_rpc_call(
        function=inspection_branch.get_branch_data_from_branch_state_id,
        schema=inspection_branch.get_branch_data_from_branch_state_id_schema,
        kwargs=kwargs)



@dispatcher.add_method
def get_article_from_article_name(branch_id: str, name: str):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_id, name=name)
    # return call
    return wrap_rpc_call(
        function=inspection_articles.get_article_from_article_name,
        schema=inspection_articles.get_article_from_article_name_schema,
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
