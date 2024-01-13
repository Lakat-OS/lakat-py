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