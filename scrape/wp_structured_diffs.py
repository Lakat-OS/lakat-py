import re
import difflib
from scrape.wp_structured_text import WikipediaStructuredText
from scrape.wp_structured_text import Part
from typing import Mapping, List, Tuple

def _is_identical(part1, part2):
    return part1.full_text == part2.full_text

def _get_similarity(part1, part2):
    matcher = difflib.SequenceMatcher(None, part1.full_text, part2.full_text)
    # The ratio is a measure of the sequences' similarity
    return matcher.ratio()

def _has_same_title_and_super_title(part1, part2):
    return part1.title == part2.title and part1.super_title == part2.super_title

def _are_summaries(part1, part2):
    return part1.level == 1 and part2.level == 1


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

    # Placeholder for the _is_similar function
    # def _is_similar(part1, part2):
    #     ...

    def compare(self, similarity_threshold=0.7, zero_level_similarity_threshold=0.9,check_unpartnered=False):
        text1_parts = self.old.extract_parts()
        text2_parts = self.new.extract_parts()

        rearranged, could_be_new_or_modified, modified, new, deleted, partnered_indices, potentially_new_indices = [], [], [], [], [], [], []

        # Step 1: Find identical and potential new or modified parts
        for j, part2 in enumerate(text2_parts):
            found_partner = False
            for i, part1 in enumerate(text1_parts):
                if _is_identical(part1, part2):
                    rearranged.append({'old_index': i, 'new_index': j})
                    partnered_indices.append(i)
                    found_partner = True
                    break
            if not found_partner:
                could_be_new_or_modified.append((j, part2))

        # Step 2: Filter could_be_new_or_modified list
        for j, part2 in could_be_new_or_modified:
            similar_found = False
            for i, part1 in enumerate(text1_parts):
                if i not in partnered_indices:
                    similarity = _get_similarity(part1, part2)
                    cond1 =  part1.level!=0 and similarity >= similarity_threshold
                    cond2 =  part1.level==0 and similarity >= zero_level_similarity_threshold                        
                    cond3= _has_same_title_and_super_title(part1, part2)
                    cond4= _are_summaries(part1, part2)

                    if cond1 or cond2 or cond3 or cond4:
                        modified.append({'old_index': i, 'new_index': j, 'score': similarity})
                        partnered_indices.append(i)
                        similar_found = True
                        break
                    
            if not similar_found:
                potentially_new_indices.append(j)

        # update new_indices =
        new_indices = []
        # Step 3: Identify deleted parts
        for i, part1 in enumerate(text1_parts):
            if i not in partnered_indices:
                if check_unpartnered:
                    # Check if part1 is similar to any unpartnered part in text2
                    similar_found = False
                    for j in potentially_new_indices:
                        part2 = text2_parts[j]
                        similarity = _get_similarity(part1, part2)
                        cond1 =  part1.level!=0 and similarity >= similarity_threshold
                        cond2 =  part1.level==0 and similarity >= zero_level_similarity_threshold  
                        if cond1 or cond2:
                            # add to modified
                            if j in [m["new_index"] for m in modified]:
                                raise(f"Error: modified part {j} is already in modified list of new indices")
                            if i in [m["old_index"] for m in modified]:
                                raise(f"Error: modified part {i} is already in modified list of old indices")
                            
                            modified.append({'old_index': i, 'new_index': j, 'score': similarity})
                            similar_found = True
                            
                            break
                    if not similar_found:
                        new_indices.append(j)
                        deleted.append(i)
                else:
                    new_indices = potentially_new_indices
                    deleted.append(i)
        
        # Step 4: Identify added parts
        for j in new_indices:
            new.append(j)

        return {'rearranged': rearranged, 'modified': modified, 'new': new, 'deleted': deleted}



def is_similar(part1: Part, part2: Part, similarity_threshold=0.6, zero_level_similarity_threshold=0.9, blunt=True):
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
            sim_thr = _similar_content(part1.content, part2.content, blunt=blunt)
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



def _similar_content(content1: str, content2: str, blunt=True):
    """
    Checks if the content of two parts is similar using difflib's SequenceMatcher.

    :param content1: Content of the first part.
    :param content2: Content of the second part.
    :return: Similarity ratio (float) between the contents.
    """
    # Create a SequenceMatcher object
    if blunt:
        return float(content1 == content2)
    else:
        matcher = difflib.SequenceMatcher(None, content1, content2)
        # The ratio is a measure of the sequences' similarity
        return matcher.ratio()


# Helper function to find a similar part
def find_similar_part_in_second(part_1: Part, part_2_s: List[Part], similarity_threshold=0.6, zero_level_similarity_threshold=0.9) -> Tuple[Part or None, int, float]:
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
def find_similar_part_in_first(part_1_s: List[Part], part_2: Part, similarity_threshold=0.6, zero_level_similarity_threshold=0.9) -> Tuple[Part or None, int, float]:
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
        if i>9 and i<12:
            ftc = p.content
            ft2c = q.content
            print(p.title, q.title)
            print(ftc[0:min(30,len(ftc))])
            print(ft2c[0:min(30,len(ft2c))])
            print("contents are similar", _similar_content(ftc, ft2c))
            print("----")
        if not q:
            deleted.append({"part":p, "max_similarity": score, "most_similar_index": j})
        if q:
            ## TODO: remove!!
            if p.content == q.content:
                print("add to rearranged")
                rearranged.append({"old_index":i, "new_index": j})
            else:
                print("add to modified")
                modified.append({"old_index":i, "new_index": j, "score": score})
        
    # identify added
    for j, q in enumerate(text2_parts):
        p, i, score = find_similar_part_in_first(text1_parts, q, similarity_threshold=similarity_threshold,
        zero_level_similarity_threshold=zero_level_similarity_threshold)
        if not p:
            added.append({"part":q, "max_similarity": score, "most_similar_index": i})

    return {"deleted": deleted, "added": added, "rearranged": rearranged, "modified": modified}