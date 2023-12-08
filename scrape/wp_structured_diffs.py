import re
import difflib
from scrape.wp_structured_text import WikipediaStructuredText
from scrape.wp_structured_text import Part
from typing import Mapping, List


class Diff:

    def __init__(self, 
        old: WikipediaStructuredText, 
        new: WikipediaStructuredText
    ):
        self.old = old
        self.new = new

    def get_diff(self, similarity_threshold=0.6, zero_level_similarity_threshold=0.9):
        """Return the diff between the old and new text."""
        return analyze_differences(self.old.parts, self.new.parts, similarity_threshold=similarity_threshold, 
        zero_level_similarity_threshold=zero_level_similarity_threshold)




def is_similar(part1: Part, part2: Part, similarity_threshold=0.6, zero_level_similarity_threshold=0.9):
    """
    Determines if two parts are similar based on their title, level, super_title, and content.

    :param part1: First part to compare.
    :param part2: Second part to compare.
    :param similarity_threshold: Threshold for content similarity.
    :return: Boolean indicating if the parts are similar. and the similarity ratio (float) between the contents.
    """
    # Check if levels are different
    if part1.level != part2.level:
        return False, 0
    
    if part1.level == 1 and part2.level == 1:
        return True, 1

    # Check if titles and super_titles are the same
    if part1.title == part2.title and part1.super_title == part2.super_title and part1.level == part2.level:
        # same title, same super-title, same level
        if part1.level == 0:
            sim_thr = _similar_content(part1.content, part2.content)
            return sim_thr >= zero_level_similarity_threshold, sim_thr
        else:
            # TODO: maybe change this
            return True, 1

    sim_thr = _similar_content(part1.content, part2.content)
    # Check if titles are different but contents are similar
    if part1.title != part2.title and part1.super_title == part2.super_title:
        # if part1.level == 0:
        #     return sim_thr >= zero_level_similarity_threshold, sim_thr
        return sim_thr >= similarity_threshold, sim_thr

    # Check if super_titles are different but titles are the same and contents are similar
    if part1.super_title != part2.super_title and part1.title == part2.title:
        # if part1.level == 0:
        #     return sim_thr >= zero_level_similarity_threshold, sim_thr
        return sim_thr >= similarity_threshold, sim_thr

    return False, 0



def _similar_content(content1: str, content2: str):
    """
    Checks if the content of two parts is similar using difflib's SequenceMatcher.

    :param content1: Content of the first part.
    :param content2: Content of the second part.
    :return: Similarity ratio (float) between the contents.
    """
    # Create a SequenceMatcher object
    matcher = difflib.SequenceMatcher(None, content1, content2)

    # The ratio is a measure of the sequences' similarity
    return matcher.ratio()


# Helper function to find a similar part
def find_similar_part_in_second(part_1: Part, part_2_s: List[Part], similarity_threshold=0.6, zero_level_similarity_threshold=0.9):
    most_similar_part = [None, 0, 0, False]
    for i, other_part in enumerate(part_2_s):
        flag, sim_score = is_similar(part_1, other_part, similarity_threshold=similarity_threshold,
        zero_level_similarity_threshold=zero_level_similarity_threshold)
        if sim_score > most_similar_part[2]:
            most_similar_part = [other_part, i, sim_score, flag]
    if most_similar_part[3]:
        return most_similar_part[0], most_similar_part[1], most_similar_part[2]
    return None, most_similar_part[1], most_similar_part[2]

# Helper function to find a similar part
def find_similar_part_in_first(part_1_s: List[Part], part_2: Part, similarity_threshold=0.6, zero_level_similarity_threshold=0.9):
    most_similar_part = [None, 0, 0, False]
    for i, other_part in enumerate(part_1_s):
        flag, sim_score = is_similar(other_part, part_2, similarity_threshold=similarity_threshold, 
        zero_level_similarity_threshold=zero_level_similarity_threshold)
        if sim_score > most_similar_part[2]:
            most_similar_part = [other_part, i, sim_score, flag]
    if most_similar_part[3]:
        return most_similar_part[0], most_similar_part[1], most_similar_part[2]
    return None, most_similar_part[1], most_similar_part[2]


def analyze_differences(text1_parts: List[Part], text2_parts: List[Part], similarity_threshold=0.6, zero_level_similarity_threshold=0.9):
    deleted, added, rearranged, modified = [], [], [], []


    # Identify deleted, rearranged, modified
    for i, p in enumerate(text1_parts):
        q, j, score = find_similar_part_in_second(p, text2_parts, similarity_threshold=similarity_threshold, 
        zero_level_similarity_threshold=zero_level_similarity_threshold)
        if not q:
            deleted.append({"part":p, "max_similarity": score, "most_similar_index": j})
        if q:
            if p.content == q.content:
                rearranged.append({"old_index":i, "new_index": j})
            else:
                modified.append({"old_index":i, "new_index": j, "score": score})
        
    # identify added
    for j, q in enumerate(text2_parts):
        p, i, score = find_similar_part_in_first(text1_parts, q, similarity_threshold=similarity_threshold,
        zero_level_similarity_threshold=zero_level_similarity_threshold)
        if not p:
            added.append({"part":q, "max_similarity": score, "most_similar_index": i})

    return {"deleted": deleted, "added": added, "rearranged": rearranged, "modified": modified}