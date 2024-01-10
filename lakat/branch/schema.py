create_genesis_branch_call = {
    "type": "object",
    "properties": {
        "branch_type": {"type": "integer"},
        "signature": {"type": "string", "format": "byte"},  # base64-encoded bytes
        "accept_conflicts": {"type": "boolean"},
        "msg": {"type": "string", "varint_encoded": "true"}
    },
    "required": ["branch_type", "signature", "accept_conflicts", "msg"]
}

create_genesis_branch_response = {"type": "string", "format": "byte"}  # base64-encoded bytes

