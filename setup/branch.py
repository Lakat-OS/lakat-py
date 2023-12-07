from scrape.wp_get_page import WikipediaPage
from scrape.wp_structured_diffs import Diff, _similar_content
from scrape.wp_structured_text import WikipediaStructuredText
import difflib
from config.scrape_cfg import EXAMPLE_ARTICLE_TITLE, WIKIPEDIA_API_URL
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA, BUCKET_ID_TYPE_NO_REF
from utils.serialize import serialize, unserialize

def add_article_to_branch(article_title, public_key, with_history=True):
    
    wp = WikipediaPage(WIKIPEDIA_API_URL)
    edit_history = wp.load_content_from_batches(
        article_title, 0, 105, download_if_not_exist=True)
    edit_history.reverse()

    for i, edit in enumerate(edit_history):
        # submit the edit to lakat

        if i==0:
            # create the first bucket and new branch.
            structured_text_old = WikipediaStructuredText(edit["*"])
            msg = edit["comment"]
            old_parts = structured_text_old.parts
            contents = list()
            for part in old_parts:
                data_dict = {
                    "schema_id": DEFAULT_ATOMIC_BUCKET_SCHEMA,
                    "public_key": public_key,
                    "parent_bucket": None,
                    "data": serialize(part.content),
                    "refs": serialize([])
                }
                contents.append(serialize(data_dict))

            molecular_data = [  
                {"id":0, "type": BUCKET_ID_TYPE_NO_REF},
                

        ind = 152
        str_text_old = WikipediaStructuredText(loaded_content[ind]["*"])
        str_text_new = WikipediaStructuredText(loaded_content[ind+1]["*"])
        diff = Diff(old=str_text_old, new=str_text_new)
        df = diff.get_diff(similarity_threshold=0.75, zero_level_similarity_threshold=0.95)
        df

        # print('pubkey', pub_key)
        # make some example submit Data:
        introduction = "Introduction"
        results = "Results"
        conclusion = "Conclusion"
        atomic = [introduction, results, conclusion]
        
        contents = list()
        for data in atomic:
            data_dict = {
                "schema_id": DEFAULT_ATOMIC_BUCKET_SCHEMA,
                "public_key": pub_key,
                "parent_bucket": None,
                "data": serialize(data),
                "refs": serialize([])
            }
            contents.append(serialize(data_dict))
        
        molecular_data = [
            {"id":0, "type": BUCKET_ID_TYPE_NO_REF},
            {"id":1, "type": BUCKET_ID_TYPE_NO_REF},
            {"id":2, "type": BUCKET_ID_TYPE_NO_REF}]
        
        contents.append(serialize({
            "schema_id": DEFAULT_MOLECULAR_BUCKET_SCHEMA,
            "public_key": pub_key,
            "parent_bucket": None, 
            "data": serialize(molecular_data),
            "refs": serialize([]) 
        }))

        res = content_submit(
            contents=contents, 
            branchId=None, 
            proof=b'', 
            msg='test', 
            create_branch=True)
