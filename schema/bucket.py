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

default_atomic_bucket_data_schema = {"type": "string", "varint_encoded": "true"}
default_molecular_bucket_data_schema = {
          "type": "array",
          "items": {"type": "string", "format": "byte"}
        }

bucket_schema = {
  "type": "object",
  "properties": {
    "schema_id": {"type": "integer"},
    "signature": {"type": "string", "format": "byte"},
    "public_key": {"type": "string", "format": "byte"},
    "parent_bucket": {"type": "string", "format": "byte"},
    "root_bucket": {"type": "string", "format": "byte"},
    "data": {
      "oneOf": [
        default_atomic_bucket_data_schema,
        default_molecular_bucket_data_schema]
    },
    "refs": {
      "type": "array",
      "items": {"type": "string", "format": "byte"}
    },
    "timestamp": {"type": "integer"}
  },
  "required": ["schema_id", "signature", "public_key", "parent_bucket", "root_bucket", "data", "refs", "timestamp"]
}
