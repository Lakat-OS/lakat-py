import re
import difflib
from typing import Mapping, List



# class Part:
#     def __init__(self, title, super_title, level, header, headerless_content) -> None:
#         self.title = title
#         self.super_title =  super_title
#         self.level = level
#         self.header = header
#         self.headerless_content = headerless_content

#     @property
#     def content(self):
#         header = f"{self.header}\n" if self.header else ""
#         return header + self.headerless_content


# class WikipediaStructuredText():

#     def __init__(self, wikitext):
#         self.wikitext = wikitext

#     # get a property called parts
#     @property
#     def parts(self):
#         return self.extract_parts()

#     def extract_parts(self) -> List[Part]:
#         sections = list()
#         section_stack = list()
#         # Extracting the short description
#         short_desc_match = re.search(r"{{short description\|(.*?)}}", self.wikitext)
#         short_description = short_desc_match.group(1) if short_desc_match else ""
#         sections.append(Part(title="Short Description", super_title="", level=0, header="", headerless_content=short_description))

#         # Regular expression for section titles
#         pattern = r"(={2,})([^=]+)\1"

#         # Find the start position of the first section header
#         first_section_match = re.search(pattern, self.wikitext)
#         summary_end = first_section_match.start() if first_section_match else len(self.wikitext)
#         summary_start = short_desc_match.end() if short_desc_match else 0
#         sections.append(Part(title="Summary", super_title="", level=1, headerless_content= self.wikitext[summary_start:summary_end].strip(), header=""))

#         # Splitting the text based on section titles
#         parts = re.split(pattern, self.wikitext)
        
#         for i in range(1, len(parts), 3):
#             level = len(parts[i])  # The number of '=' indicates the level of the section
#             title = parts[i + 1].strip()
#             headerless_content = parts[i + 2].strip()
#             super_title = ""

#             # Update the stack and determine the super_title
#             while section_stack and section_stack[-1].level >= level:
#                 section_stack.pop()
#             if section_stack:
#                 super_title = section_stack[-1].title

#             # Add the current section to the stack
#             current_part = Part(title=title, level=level, header=title, headerless_content=headerless_content, super_title=super_title)
#             section_stack.append(current_part)

#             # Add the section to the list of sections
#             sections.append(current_part)

#         return sections
    

class Part:
    def __init__(self, title, super_title, level, header, headerless_content, part_id, full_text="") -> None:
        self.title = title
        self.super_title = super_title
        self.level = level
        self.header = header
        self.headerless_content = headerless_content
        self.part_id = part_id
        self.full_text = full_text  # full_text includes the specific formatting

    @property
    def content(self):
        # header = f"{self.header}\n" if self.header else ""
        # return header + self.headerless_content
        return self.full_text
    

    # override the __repr__ method with __dict__
    def __repr__(self) -> str:
        cropped_dict = {k: str(v)[:min(30,len(str(v)))] for k, v in self.__dict__.items()}
        return str(cropped_dict)

class WikipediaStructuredText():

    def __init__(self, wikitext):
        self.wikitext = wikitext

    @property
    def parts(self):
        return self.extract_parts()

    def extract_parts(self) -> List[Part]:
        sections = list()
        section_stack = list()

        # Regular expression for section titles
        pattern = r"(={2,})([^=]+)\1"

        # Splitting the text based on section titles
        parts = re.split(pattern, self.wikitext)

        # Extract meta information and summary before the first section
        first_section_index = self.wikitext.find(parts[1]) if len(parts) > 1 else len(self.wikitext)
        pre_section_text = self.wikitext[:first_section_index]

        # Extract 0-level objects like {{something|content}}
        zero_level_pattern = r"{{(.*?)\|(.*?)}}"
        zero_level_objects = re.findall(zero_level_pattern, pre_section_text)
        part_id = 0
        for obj in zero_level_objects:
            meta_type, content = obj
            full_text = f"{{{{{meta_type}|{content}}}}}"
            sections.append(Part(title=meta_type, super_title="", level=0, header="", headerless_content=content, part_id=part_id, full_text=full_text))
            part_id += 1

        # Extract summary
        # Updated line in extract_parts method
        for obj in zero_level_objects:
            full_obj_text = '{{' + obj[0] + '|' + obj[1] + '}}'
            pre_section_text = re.sub(re.escape(full_obj_text), '', pre_section_text)

        summary_content = pre_section_text.strip()
        sections.append(Part(title="Summary", super_title="", level=1, header="", headerless_content=summary_content, part_id=part_id, full_text=summary_content))
        part_id += 1

        # Process each part for section extraction
        for i in range(1, len(parts), 3):
            level = len(parts[i])
            title = parts[i + 1].strip()
            headerless_content = parts[i + 2].strip()
            super_title = ""
            header = parts[i] + title + parts[i]
            full_text = header + "\n" + headerless_content

            # Update the stack and determine the super_title
            while section_stack and section_stack[-1].level >= level:
                section_stack.pop()
            if section_stack:
                super_title = section_stack[-1].title

            current_part = Part(title=title, super_title=super_title, part_id=part_id, level=level, header=title, headerless_content=headerless_content, full_text=full_text)
            section_stack.append(current_part)
            sections.append(current_part)

            part_id += 1

        return sections

