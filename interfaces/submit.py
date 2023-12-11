class SUBMIT:
    def __init__(self, parent_submit_id, submit_msg, trie_root, submit_trace):
        self.parent_submit_id=parent_submit_id,
        self.submit_msg=submit_msg,
        self.trie_root=trie_root,
        self.submit_trace=submit_trace

class SUBMIT_TRACE:
    def __init__(self, changesTrace, pullRequests, nsRegistry, reviewsTrace, socialTrace, sproutSelectionTrace):
        self.changesTrace=changesTrace,
        self.pullRequests=pullRequests,
        self.reviewsTrace=reviewsTrace,
        self.nsRegistry=nsRegistry
        self.socialTrace=socialTrace,
        self.sproutSelectionTrace=sproutSelectionTrace