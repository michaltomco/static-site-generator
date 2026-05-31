from enum import Enum
import re


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(text: str) -> BlockType:
    if re.fullmatch(r"#{1,6} .+", text):
        return BlockType.HEADING

    if re.fullmatch(r"```\n[\s\S]*```", text):
        return BlockType.CODE

    lines = text.split("\n")

    if all(re.fullmatch(r">.*", line) for line in lines):
        return BlockType.QUOTE

    if all(re.fullmatch(r"- .+", line) for line in lines):
        return BlockType.UNORDERED_LIST

    for index, line in enumerate(lines, start=1):
        match = re.fullmatch(r"(\d+)\. .+", line)
        if match is None or int(match.group(1)) != index:
            return BlockType.PARAGRAPH
    else:
        return BlockType.ORDERED_LIST
