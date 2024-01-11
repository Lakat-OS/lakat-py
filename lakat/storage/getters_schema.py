get_branch_name_from_branch_state_id = {
  "title": "get_branch_name_from_branch_state_id",
  "type": "object",
  "properties": {
    "branch_state_id": {
      "type": "string",
      "format": "byte"
    }
  },
  "required": ["branch_state_id"],
  "response": {
    "type": "string",
    "varint_encoded": "true"
  }
}

get_branch_name_from_branch_id = {
  "title": "get_branch_name_from_branch_id",
  "type": "object",
  "properties": {
    "branch_id": {
      "type": "string",
      "format": "byte"
    }
  },
  "required": ["branch_id"],
  "response": {
    "type": "string",
    "varint_encoded": "true"
  }
}