import initialization.setup.wikipedia_articles as wikipedia_articles
import initialization.base.branch as base_branch
from initialization.wp_get_page import WikipediaPage
from config.scrape_cfg import EXAMPLE_ARTICLE_TITLE, WIKIPEDIA_API_URL
from utils.encode.bytes import encode_bytes_to_base64_str
from utils.format.rpc_call import wrap_rpc_call
import lakat.submit.functions as lakat_submit_functions
import os, json


def deploy_wikipedia_article(article_name=EXAMPLE_ARTICLE_TITLE, try_cache=True, verbose=False):
    """Deploy the entire edit history of a Wikipedia article."""
    if verbose:
        print(f"NOTE: We are in the beginning of the deployment of {article_name}. We fetch the history of the article.")
    random_large_batch_number = 105
    wp = WikipediaPage(WIKIPEDIA_API_URL)
    edit_history = wp.load_content_from_batches(
        EXAMPLE_ARTICLE_TITLE, 0, random_large_batch_number, download_if_not_exist=True)
    edit_history.reverse()
    if verbose:
        print(f"NOTE: We already fetched the history of {article_name}")
    response = base_branch.create_genesis_twig_branch("Wikipedia Community", "Genesis Submit", accept_conflicts=True, debug=verbose)
    print(response)
    
    # generate a public key bytes(1)
    public_key = encode_bytes_to_base64_str(bytes(1))

    deploy_wiki_article_ = True
    if try_cache:
        # load submissions from cache
        dir_path = f"./{wp.scrape_directory}/hist/{article_name}"
        filename = f"submissions.json"
        filepath = os.path.join(dir_path, filename)
        # check if file exists
        if not os.path.exists(filepath):
            if verbose:
                print(f"NOTE: We are deploying the entire edit history of {article_name}")
            deploy_wiki_article_ = True
        else: 
            deploy_wiki_article_ = False
            if verbose:
                print(f"NOTE: We are loading the entire deployment history of {article_name} from cache")
            with open(filepath, 'r') as file:
                submissions = json.load(file)
                if not submissions:
                    deploy_wiki_article_ = True

    if deploy_wiki_article_:
        if verbose:
            print(f"NOTE: We are submitting the entire edit history of {article_name}")
        submissions = wikipedia_articles._submit_article_history_from_edit_hist(
            edit_hist=edit_history,
            public_key=public_key,        
            branchId=response["decoded_branch_id"],
            returnSubmitKwargs=True, 
            verbose=verbose)
        
        # save submissions to cache
        # Create directories if they don't exist
        dir_path = f"./{wp.scrape_directory}/hist/{article_name}"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # save submissions to cache
        filename = f"submissions.json"
        filepath = os.path.join(dir_path, filename)
        with open(filepath, 'w') as file:
            json.dump(submissions, file, indent=wp._jsonIndent)

    if not deploy_wiki_article_:
        # use wrapped rpc call to submit the article
        if verbose:
            print(f"NOTE: We are deploying the entire edit history of {article_name} using wrapped rpc call")
        for j, submission in enumerate(submissions):
            branch_state_id = wrap_rpc_call(
                function=lakat_submit_functions.submit_content_for_twig,
                schema=lakat_submit_functions.submit_content_for_twig_schema,
                kwargs=submission)
            if verbose and j % 30 == 2:
                print(f"branch state id after {j} deployments is {branch_state_id}.")
        if verbose:
            print(f"NOTE: We are done deploying the entire edit history of {article_name} using wrapped rpc call")


