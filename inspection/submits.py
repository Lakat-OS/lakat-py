from typing import Tuple, List 
from inspection.branch import _find_branches_between_initial_and_final_branch
import lakat.storage.local_storage as lakat_storage
from utils.encode.hashing import deserialize_from_key


def _find_branches_between_two_submits(from_submit_id, until_submit_id: bytes, number_of_branches_to_query: int) -> Tuple[bool, int, List[bytes]]:
    initial_branch_id = _get_branch_id_from_submit_id(from_submit_id)
    final_branch_id = _get_branch_id_from_submit_id(until_submit_id)
    return _find_branches_between_initial_and_final_branch(
        initial_branch_id=initial_branch_id, 
        final_branch_id=final_branch_id, 
        number_of_branches_to_query=number_of_branches_to_query)


def _get_branch_id_from_submit_id(submit_id: bytes) -> bytes:
    submit_trace = _get_submit_trace_from_submit_id(submit_id=submit_id)
    return submit_trace["branchId"]

def _get_submit_trace_from_submit_id(submit_id: bytes) -> bytes:
    submit = deserialize_from_key(key=submit_id, value=lakat_storage.get_from_db(submit_id))
    return deserialize_from_key(key=submit["submit_trace"], value=lakat_storage.get_from_db(submit["submit_trace"]))