class SUBMIT:
    def __init__(self, parent_submit_id, submit_msg, trie_root, submit_trace):
        self.parent_submit_id=parent_submit_id
        self.submit_msg=submit_msg
        self.trie_root=trie_root
        self.submit_trace=submit_trace


class SUBMIT_TRACE:
    def __init__(self, config, newBranchHead, changesTrace, pullRequests, nameResolution, nameResolutionRoot, nameTrie, dataTrie, reviewsTrace, socialTrace, socialRoot, sprouts, sproutSelectionTrace):
        self.config=config
        self.newBranchHead=newBranchHead
        self.changesTrace=changesTrace
        self.pullRequests=pullRequests
        self.nameResolution=nameResolution
        self.nameResolutionRoot=nameResolutionRoot
        self.nameTrie=nameTrie
        self.dataTrie=dataTrie
        self.reviewsTrace=reviewsTrace
        self.socialTrace=socialTrace
        self.socialRoot=socialRoot
        self.sprouts=sprouts
        self.sproutSelectionTrace=sproutSelectionTrace