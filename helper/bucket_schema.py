from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA

def is_molecular_bucket(schema_id: int) -> bool:
    """ Check if the bucket is molecular or not

    Parameters
    ----------
    schema_id : int
        The schema id

    Returns
    -------
    bool
        True if the bucket is molecular, False otherwise
    """
    return schema_id in [DEFAULT_MOLECULAR_BUCKET_SCHEMA]