# Documentation

## Submit

`def content_submit(contents: List[bytes], interactions: List[Mapping[str, any]], branchId: str, proof: bytes, msg: str, create_branch)-> dict`

1. check Contributor Proof
2. Get the name resolution bucket id (IN MEMORY)
    - It is stored the branch object (db-lookup)
3. Prepare and create bucket data (IN MEMORY)
    - Cast the contents into bucket data. 
    - Buckets are dicts with "data" and "new_registrations" keys
        - The "data" key contains a dict where the keys are the schemata and the values are all buckets of that given schema_id
        - The "new_registrations" key contains a list of new name registrations. Each entry contains a dict with the bucket id (key="id") and the bucket name (key="name").
4. Retrieve those buckets that are name registration deployments (IN MEMORY)
5. Create the Submit Trace (IN MEMORY)
6. Create the Submit Object (IN MEMORY)
7. Create Branch Object Update (IN MEMORY)
8. Create Name Registration Trie Update (IN MEMORY)
9. Collect all DB write queries, trie write queries and response data
10. Write DB queries into DB storage (buckets, submit trace, submit, branch)
11. Write Trie data into Branch Trie


## Trie vs DB
Think of the DB as the global source of truth across all branches.
Think of the Trie as a branch-specifiv validation object pertaining. Everything that is in the trie cannot be modified retrospectively.

- Buckets 
    - storage: DB and hash in Trie
    - namespace: Global
- Branch 
    - storeage: DB and hash in Trie
    - namespace: Global
- Config
    - storage: DB and hash in Trie
    - namespace: Branch
- Interaction
    - storage: value of Trie
    - namespace: Branch
- Submit
    - storage: DB
    - namespace: Branch
- SubmitTrace
    - storage: DB
    - namespace: Branch
    
## Branch

The branch itself is a container, not a bucket, but it is saved in the trie as if it was a bucket.


## TODO

[] Interaction Trie dump still has the same hash as the normal trie