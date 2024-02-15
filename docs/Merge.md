# Merge Functionality for Lakat.science Project

## Overview
This document outlines the proposed merge functionality between two branches, referred to as `peri` and `core`, in the Lakat.science project. The process involves tracking head IDs of bucket streams and the mapping between bucket names and bucket IDs.

## Branches and Ancestors
- **Branches Involved**: Two branches, `peri` and `core`.
  - `peri` is pulled into `core`.
- **Tracking**: Each branch maintains a record of the head IDs of bucket streams and the bucket name to bucket ID mapping.
- **Common Ancestor**: 
  - Determination of a common ancestor branch, denoted as `A`.
  - Branches on the core side are labeled `C_1, C_2, ..., C_n`.
  - Branches on the peri side are labeled `B_1, B_2, ..., B_n`.
  - The configuration may include only one `C` or `B`, and either, but not both, might coincide with `A`.

## Merge Algorithm
### Step 1: Name and ID Resolution
- The algorithm begins by processing all registered names of molecular buckets, either through querying the name-trie or going backwards through the submits.
- For each name in `B_n`:
  - Check if the name appears in any `C` names.
  - If a name is marked as "renamed", follow the new name reference.
  - Determine if the root-bucket-id is present in any of the data-tries of the `C` branches.

### Step 2: Handling Different Cases
- The algorithm categorizes each instance into different case slots in a backlog.
- Cases include:
  - New articles not present in `C`.
  - Articles with name matches but different root bucket IDs.
  - Articles with the same name and root bucket ID.

### Step 3: Iterating through Branches
- After processing `B_j`:
  - If `B_j` is not identical to `A`, move to `B_{j+1}`.
  - Consider the name resolution entry at the submit of `B_j` for additional article names.

### Step 4: Resolving Head Differences
- When an article name and root are the same but heads differ:
  - A decision is required on which head (peri or core) to adopt.
  - This can be specified in the merge argument by the user.
- Options include:
  - Adopting the peri head.
  - Adopting the core head.
  - Allowing both articles to coexist if the core branch permits conflicts.

### Step 5: Name Resolution and Conflicts
- The merger's input determines whether the peri or core name receives a suffix and a new entry in the core branch's name-trie.

## Conclusion
This document has outlined the initial steps and considerations for the merge functionality between the `peri` and `core` branches. Further details and iterations will follow as the project progresses.
