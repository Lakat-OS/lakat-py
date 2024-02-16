from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from config.db_cfg import DB_NAME
DB_NAME = "lakat_test_333"
import lakat.branch.functions as lakat_branch_functions
import lakat.storage.local_storage as lakat_storage
import lakat.submit.functions as lakat_submit_functions
import inspection.articles as inspection_articles
import inspection.branch as inspection_branch
import inspection.bucket as inspection_bucket
import initialization.setup.example_deployment as example_deployment_setup
from config.scrape_cfg import EXAMPLE_ARTICLE_TITLE
from config.env import WITH_INTIAL_ARTICLE_DEPLOYMENT
from config.encode_cfg import ENCODING_FUNCTION
from config.rpc_cfg import RPC_PORT
from utils.encode.language import encode_string
from utils.encode.bytes import key_encoder
from utils.format.schema import check_argument, convert_to_bytes_based_on_schema, convert_from_bytes_based_on_schema
from utils.format.rpc_call import wrap_rpc_call
import math
from jsonrpc import JSONRPCResponseManager, dispatcher


### Example Deployments 
if WITH_INTIAL_ARTICLE_DEPLOYMENT:
    try:
        example_deployment_setup.deploy_wikipedia_article(
            article_name=EXAMPLE_ARTICLE_TITLE,
            try_cache=False, verbose=True)
    except Exception as e1:
        print("Article Deployment did not work from cache. We try without cache. Reason is ", str(e1))
        try:
            example_deployment_setup.deploy_wikipedia_article(
                article_name=EXAMPLE_ARTICLE_TITLE,
                try_cache=True, verbose=True)
        except Exception as e2:
            print("Article Deployment did not work because: ", str(e2))


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
def create_offspring_branch_at_head(branch_id: str, branch_type: int, name: str, signature: str, accept_conflicts: bool, msg: str):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_id, branch_type=branch_type, name=name, signature=signature, accept_conflicts=accept_conflicts, msg=msg)
    # return call
    return wrap_rpc_call(
        function=lakat_branch_functions.create_offspring_branch_at_head,
        schema=lakat_branch_functions.create_offspring_branch_at_head_schema,
        kwargs=kwargs)


@dispatcher.add_method
def create_offspring_branch_at_submit(branch_id: str, branch_type: int, name: str, signature: str, accept_conflicts: bool, msg: str):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_id, branch_type=branch_type, name=name, signature=signature, accept_conflicts=accept_conflicts, msg=msg)
    # return call
    return wrap_rpc_call(
        function=lakat_branch_functions.create_offspring_branch_at_submit,
        schema=lakat_branch_functions.create_offspring_branch_at_submit_schema,
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
def get_local_branches():
    return wrap_rpc_call(
        function=inspection_branch.get_local_branches,
        schema=inspection_branch.get_local_branches_schema,
        kwargs=dict())

#### ARTICLE GETTERS ###################################

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
def get_article_root_id_from_article_name(branch_id: str,  name: bytes):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_id, name=name)
    # return call
    return wrap_rpc_call(
        function=inspection_articles.get_article_root_id_from_article_name,
        schema=inspection_articles.get_article_root_id_from_article_name_schema,
        kwargs=kwargs)

@dispatcher.add_method
def get_article_from_article_id(bucket_id: str):
    # convert arguments to keyword dictionary
    kwargs = dict(bucket_id=bucket_id)
    # return call
    return wrap_rpc_call(
        function=inspection_articles.get_article_from_article_id,
        schema=inspection_articles.get_article_from_article_id_schema,
        kwargs=kwargs)

##### BUCKET GETTERS ###################################

@dispatcher.add_method
def get_bucket_from_bucket_id(bucket_id: str):
    # convert arguments to keyword dictionary
    kwargs = dict(bucket_id=bucket_id)
    # return call
    return wrap_rpc_call(
        function=inspection_bucket.get_bucket_from_bucket_id,
        schema=inspection_bucket.get_bucket_from_bucket_id_schema,
        kwargs=kwargs) 

@dispatcher.add_method
def get_bucket_head_from_bucket_id(branch_id: str, bucket_id: str, deserialize_bucket: bool):
    # convert arguments to keyword dictionary
    kwargs = dict(branch_id=branch_id, bucket_id=bucket_id, deserialize_bucket=deserialize_bucket)
    # return call
    return wrap_rpc_call(
        function=inspection_bucket.get_bucket_head_from_bucket_id,
        schema=inspection_bucket.get_bucket_head_from_bucket_id_schema,
        kwargs=kwargs)      


##### DATABASE FUNCTIONS ################################

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
