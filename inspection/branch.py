import lakat.storage.local_storage as lakat_storage
import lakat.storage.branch_storage as lakat_local_branch_storage
from utils.encode.hashing import deserialize_from_key
from schema.bucket import bucket_schema
from typing import Tuple, List

#### BRANCH_DATE GETTERS ####


## Internal helper function to get the branch data from the branch state id


def _get_branch_data_from_branch_state_id(branch_state_id: bytes) -> bytes:
    """ " Get the branch data from the branch id

    Parameters
    ----------
    branch_id : bytes
        The branch id

    Returns
    -------
    bytes
        The branch data. The branch data is a dict. It contains the following keys
        - id: bytes
            The branch id
        - ns: bytes
            The namespace id
        - name: str
            The branch name
        - parent_id: bytes
            The parent branch id
        - stable_head: bytes
            The stable head id
        - config: bytes
            The branch config id
        - sprouts: array
            The sprout ids
        - sprout_selection: array
            The sprout selection ids
        - name_resolution: bytes
            The name resolution id
        - interaction: bytes
            The interaction id
        - parent_name_resolution: bytes
            The name resolution trie root id at the root submit (where the current branch emerged)
        - parent_interaction: bytes
            The interaction trie root id at the root submit (where the current branch emerged)
        - parent_data_trie: bytes
            The data trie root id at the root submit (where the current branch emerged)
        - signature: bytes
            The signature id
        - creation_ts: int
            The creation timestamp
    """
    return deserialize_from_key(
        key=branch_state_id, value=lakat_storage.get_from_db(branch_state_id)
    )


def _get_parsed_submit_trace_from_submit_trace_id(
    submit_trace_id: bytes, deserialize_buckets: bool = True
) -> dict:
    submit_trace = deserialize_from_key(
        key=submit_trace_id, value=lakat_storage.get_from_db(submit_trace_id)
    )
    buckets = []
    for change in submit_trace["submittedBucketsRefs"]:
        if deserialize_buckets:
            bucket = deserialize_from_key(
                key=change, value=lakat_storage.get_from_db(change)
            )
            buckets.append(bucket)
        else:
            buckets.append(change)
    registered_names = [
        {"name": name[0], "id": name[1]} for name in submit_trace["nameResolution"]]
    return dict(new_buckets=buckets, new_registered_names=registered_names)


def _get_registered_names_from_submit_trace_id(submit_trace_id: bytes) -> dict:
    submit_trace = deserialize_from_key(key=submit_trace_id, value=lakat_storage.get_from_db(submit_trace_id))
    return [{"name": name[0], "id": name[1]} for name in submit_trace["nameResolution"]]


def _find_branches_between_initial_and_final_branch(initial_branch_id: bytes, final_branch_id: bytes, number_of_branches_to_query: int) -> Tuple[bool, int, List[bytes]]:
    found = False
    traversed_branched = list()
    current_branch_id = initial_branch_id
    for i in range(number_of_branches_to_query):
        if current_branch_id==final_branch_id:
            number_of_branches_traversed = i
            found = True
            break
        branch_head_data = _get_branch_data_from_branch_state_id(branch_state_id=lakat_storage.get_from_db(current_branch_id))
        current_branch_id = branch_head_data["parent_branch"]
    return found, number_of_branches_traversed, traversed_branched


def _get_full_branch_info_from_branch_state_id(
    branch_state_id: bytes, deserialize_buckets: bool = True
) -> dict:
    """ " Get the full branch info from the branch state id

    Parameters
    ----------
    branch_state_id : bytes
        The branch state id

    Returns
    -------
    """
    branch_data = _get_branch_data_from_branch_state_id(branch_state_id=branch_state_id)
    # 1) dereference the branch config
    branch_data_config = deserialize_from_key(
        key=branch_data["config"],
        value=lakat_storage.get_from_db(branch_data["config"]),
    )
    # add the dereferenced data to the branch "config" data
    branch_data["config"] = dict(
        accept_conflicts=branch_data_config["acceptConflicts"],
        branch_type=branch_data_config["branchType"],
    )

    # 2) dereference the name resolution
    branch_data_stable_head = deserialize_from_key(
        key=branch_data["stable_head"],
        value=lakat_storage.get_from_db(branch_data["stable_head"]),
    )
    # add the dereferenced data to the branch "stable_head" data
    branch_data["stable_head"] = dict(
        parent_submit_id=branch_data_stable_head["parent_submit_id"],
        submit_msg=branch_data_stable_head["submit_msg"],
    )
    # 3) parse the submit trace
    branch_data_submit_trace = _get_parsed_submit_trace_from_submit_trace_id(
        submit_trace_id=branch_data_stable_head["submit_trace"],
        deserialize_buckets=deserialize_buckets,
    )
    branch_data["submit_trace"] = branch_data_submit_trace

    return branch_data


## Exposed functions to get the branch data from the branch id


def get_branch_data_from_branch_id(
    branch_id: bytes, deserialize_buckets: bool = True
) -> bytes:
    """ " Get the branch data from the branch id

    Parameters
    ----------
    branch_id : bytes
        The branch id

    Returns
    -------
    bytes
        The branch data. The branch data is a dict. It contains the following keys
        - id: bytes
            The branch id
        - ns: bytes
            The namespace id
        - name: str
            The branch name
        - parent_id: bytes
            The parent branch id
        - stable_head: dict
            The stable head information dictonary
        - submit_tract: dict
            The changes made in this submit
        - config: dict
            The branch config dictionary
        - sprouts: array
            The sprout ids
        - sprout_selection: array
            The sprout selection ids
        - name_resolution: bytes
            The name resolution id
        - interaction: bytes
            The interaction id
        - parent_name_resolution: bytes
            The name resolution trie root id at the root submit (where the current branch emerged)
        - parent_interaction: bytes
            The interaction trie root id at the root submit (where the current branch emerged)
        - parent_data_trie: bytes
            The data trie root id at the root submit (where the current branch emerged)
        - signature: bytes
            The signature id
        - creation_ts: int
            The creation timestamp
    """
    return _get_full_branch_info_from_branch_state_id(
        branch_state_id=lakat_storage.get_from_db(branch_id),
        deserialize_buckets=deserialize_buckets,
    )


def get_branch_data_from_branch_state_id(
    branch_state_id: bytes, deserialize_buckets: bool = True
) -> bytes:
    return _get_full_branch_info_from_branch_state_id(branch_state_id,
        deserialize_buckets=deserialize_buckets,
    )


submit_object_schema = {
    "type": "object",
    "properties": {
        "parent_submit_id": {"type": "string", "format": "byte"},
        "submit_msg": {"type": "string", "varint_encoded": "true"}
    },
    "required": ["parent_submit_id", "submit_msg"],
}

branch_config_schema = {
    "type": "object",
    "properties": {
        "accept_conflicts": {"type": "boolean"},
        "branch_type": {"type": "integer"},
    },
    "required": ["accept_conflicts", "branch_type"],
}

submit_trace_schema = {
    "type": "object",
    "properties": {
        "new_buckets": {
            "type": "array",  ## TODO: add the bucket resolution option
            "items": {
                "oneOf": [
                    bucket_schema,
                    {"type": "string", "format": "byte"}
                ]
            }
        },
        "new_registered_names": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "varint_encoded": "true"},
                    "id": {"type": "string", "format": "byte"}},
                "required": ["name", "id"]
            },
        },
    },
    "required": ["new_buckets", "new_registered_names"],
}

get_branch_data_from_branch_id_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "byte"},
        "ns": {"type": "string", "format": "byte"},
        "name": {"type": "string", "varint_encoded": "true"},
        "parent_id": {"type": "string", "format": "byte"},
        "stable_head": submit_object_schema,
        "config": branch_config_schema,
        "sprouts": {"type": "array"},
        "sprout_selection": {"type": "array"},
        "name_resolution": {"type": "string", "format": "byte"},
        "interaction": {"type": "string", "format": "byte"},
        "parent_name_resolution": {"type": "string", "format": "byte"},
        "parent_interaction": {"type": "string", "format": "byte"},
        "parent_data_trie": {"type": "string", "format": "byte"},
        "signature": {"type": "string", "format": "byte"},
        "creation_ts": {"type": "integer"},
        "submit_trace": submit_trace_schema
    },
    "required": [
        "id",
        "ns",
        "name",
        "parent_id",
        "stable_head",
        "config",
        "name_resolution",
        "interaction",
        "parent_name_resolution",
        "parent_interaction",
        "parent_data_trie",
        "signature",
        "creation_ts",
        "submit_trace",
    ],
}

get_branch_data_from_branch_id_schema = {
  "type": "object",
  "properties": {
    "branch_id": {
      "type": "string",
      "format": "byte" 
    },
    "deserialize_buckets": {"type": "boolean"}
  },
  "required": ["branch_id"],
  "response": get_branch_data_from_branch_id_response_schema
}

get_branch_data_from_branch_state_id_schema = {
  "type": "object",
  "properties": {
    "branch_state_id": {
      "type": "string",
      "format": "byte" 
    },
    "deserialize_buckets": {"type": "boolean"}
  },
  "required": ["branch_state_id"],
  "response": get_branch_data_from_branch_id_response_schema
}


def get_local_branches():
    """ " Get the local branches

    Returns
    -------
    list
        The local branches
    """
    return lakat_local_branch_storage.get_local_branches()

get_local_branches_schema = {
  "type": "object",
  "properties": {},
  "required": [],
  "response": {
    "type": "array",
    "items": {"type": "string", "format": "byte"}
  }
}


def get_branch_history_from_branch_id(
    branch_id: bytes, depth: int, deserialize_buckets: bool = True
) -> list:
    """ " Get the branch history from the branch id

    Parameters
    ----------
    branch_id : bytes
        The branch id

    Returns
    -------
    list
        The branch history. The branch history is a list of branch state ids
    """
    branch_data = _get_branch_data_from_branch_state_id(
        branch_state_id=lakat_storage.get_from_db(branch_id),
        deserialize_buckets=deserialize_buckets,
    )
    branch_history = []
    achieved_depth = 0
    for i in range(depth):
        branch_history.append(branch_data)
        if branch_data["parent_id"] == b"":
            achieved_depth = i + 1
            break
        branch_data = _get_branch_data_from_branch_state_id(
            branch_state_id=branch_data["parent_id"],
            deserialize_buckets=deserialize_buckets,
        )
    return branch_history, achieved_depth


def get_branch_name_from_branch_id(branch_id: bytes) -> str:
    """ " Get the branch name from the branch id

    Parameters
    ----------
    branch_id : bytes
        The branch id

    Returns
    -------
    bytes
        The branch name
    """
    return _get_branch_data_from_branch_state_id(
        branch_state_id=lakat_storage.get_from_db(branch_id)
    )["name"]


get_branch_name_from_branch_id_schema = {
    "title": "get_branch_name_from_branch_id",
    "type": "object",
    "properties": {"branch_id": {"type": "string", "format": "byte"}},
    "required": ["branch_id"],
    "response": {"type": "string", "varint_encoded": "true"},
}

#### CONFIG ##########

# Internal helper function to get the branch config from the branch state id


def _get_config_from_branch_state_id(branch_state_id: bytes) -> bytes:
    """ " Get the branch config from the branch state id

    Parameters
    ----------
    branch_state_id : bytes
        The branch state id

    Returns
    -------
    bytes
        The branch config. The branch config is a dict. It contains the following keys
        - branch_type: int
            The branch type
        - accept_conflicts: bool
            The accept conflicts flag
        - accepted_proofs: array
            The accepted proofs
        - consensus_root: bytes
            The consensus root
    """
    branch_data = _get_branch_data_from_branch_state_id(branch_state_id=branch_state_id)
    branch_data_config = deserialize_from_key(
        key=branch_data["config"],
        value=lakat_storage.get_from_db(branch_data["config"]),
    )
    return dict(
        accept_conflicts=branch_data_config["acceptConflicts"],
        branch_type=branch_data_config["branchType"],
    )


# Exposed functions to get the branch config from the branch id


def get_config_from_branch_id(branch_id: bytes) -> bytes:
    """ " Get the branch config from the branch id

    Parameters
    ----------
    branch_id : bytes
        The branch id

    Returns
    -------
    bytes
        The branch config. The branch config is a dict. It contains the following keys
        - branch_type: int
            The branch type
        - accept_conflicts: bool
            The accept conflicts flag
    """
    return _get_config_from_branch_state_id(
        branch_state_id=lakat_storage.get_from_db(branch_id)
    )
