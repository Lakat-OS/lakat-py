class SUBMIT:
    def __init__(self, parent_submit_id, submit_msg, trie_root, submit_trace):
        self.parent_submit_id=parent_submit_id
        self.submit_msg=submit_msg
        self.trie_root=trie_root
        self.submit_trace=submit_trace


class SUBMIT_TRACE:
    def __init__(self, branchId, config, newBranchHead, submittedBucketsRefs, pullRequests, nameResolution, nameResolutionRoot, nameTrie, dataTrie, reviewsTrace, socialTrace, socialRoot, sprouts, sproutSelectionTrace):
        self.branchId=branchId
        self.config=config
        self.newBranchHead=newBranchHead
        self.submittedBucketsRefs=submittedBucketsRefs
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