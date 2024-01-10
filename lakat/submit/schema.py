atomic_bucket_content_schema = {
    "type": "object",
    "properties": {
        "data": {"type": "string", "varint_encoded": "true"},
        "schema": {"type": ["integer", "string"]},
        "parent_id": {"type": "string", "format": "byte", "varint_encoded": "false"},
        "signature": {"type": "string", "format": "byte", "varint_encoded": "false"},
        "refs": {
            "type": "array",
            "items": {"type": "string", "format": "byte", "varint_encoded": "false"}
        }
    },
    "required": ["data", "schema", "parent_id", "signature", "refs"]
}

molecular_bucket_content_schema = {
    "type": "object",
    "properties": {
        "data": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "varint_encoded": "true"},
                "order": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "oneOf": [
                                    {"type": "string", "format": "byte"},
                                    {"type": "integer"}, 
                                    {"type": "string"}
                                ]
                            },
                            "type": {
                                "oneOf": [
                                    {"type": "integer"}, 
                                    {"type": "string"}
                                ]
                            }
                        },
                        "required": ["id", "type"]
                    }
                }
            },
            "required": ["name", "order"]
        },
        "schema": {"type": ["integer", "string"]},
        "parent_id": {"type": "string", "format": "byte"},
        "signature": {"type": "string", "format": "byte"},
        "refs": {
            "type": "array",
            "items": {"type": "string", "format": "byte"}
        }
    },
    "required": ["data", "schema", "parent_id", "signature", "refs"]
}

bucket_contents_schema = {
    "type": "array",
    "items": {
        "oneOf": [
            atomic_bucket_content_schema,
            molecular_bucket_content_schema
        ]
    }
}

submit_content_for_twig_call = {
    "type": "object",
    "properties": {
        "branch_id": {"type": "string", "format": "byte"},  # base64-encoded bytes
        "contents": bucket_contents_schema,
        "public_key": {"type": "string", "format": "byte"},  # base64-encoded bytes
        "proof": {"type": "string", "format": "byte"},  # base64-encoded bytes
        "msg": {"type": "string", "varint_encoded": "true"}
    },
    "required": ["branch_id", "contents", "public_key", "proof", "msg"]
}

submit_content_for_twig_response = {"type": "string", "format": "byte"}  # base64-encoded bytes
