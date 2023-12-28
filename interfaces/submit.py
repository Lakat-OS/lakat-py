class SUBMIT:
    def __init__(self, parent_submit_id, submit_msg, trie_root, submit_trace):
        self.parent_submit_id=parent_submit_id
        self.submit_msg=submit_msg
        self.trie_root=trie_root
        self.submit_trace=submit_trace


class SUBMIT_TRACE:
    def __init__(self, config, trie, submit, changesTrace, pullRequests, nameResolution, nameResolutionRoot, nameTrie, dataTrie, reviewsTrace, socialTrace, sprouts, sproutSelectionTrace):
        self.config=config
        self.trie=trie
        self.submit=submit
        self.changesTrace=changesTrace
        self.pullRequests=pullRequests
        self.nameResolution=nameResolution
        self.nameResolutionRoot=nameResolutionRoot
        self.nameTrie=nameTrie
        self.dataTrie=dataTrie
        self.reviewsTrace=reviewsTrace
        self.socialTrace=socialTrace
        self.sprouts=sprouts
        self.sproutSelectionTrace=sproutSelectionTrace