import unittest

from blocknode import BlockType, block_to_block_type


class TestBlockToBlockType(unittest.TestCase):
    def test_heading(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading"), BlockType.HEADING)

    def test_heading_requires_one_to_six_hashes_space_and_text(self):
        self.assertEqual(block_to_block_type("####### Heading"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("#Heading"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("# "), BlockType.PARAGRAPH)

    def test_code(self):
        block = "```\nprint('hello')\n```"

        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_requires_opening_newline_and_closing_fence(self):
        self.assertEqual(block_to_block_type("```print('hello')```"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("```\nprint('hello')"), BlockType.PARAGRAPH)

    def test_quote(self):
        block = ">First line\n> Second line\n>Third line"

        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_requires_every_line_to_start_with_greater_than(self):
        block = ">First line\nSecond line"

        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list(self):
        block = "- first item\n- second item\n- third item"

        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_requires_dash_space_on_every_line(self):
        self.assertEqual(block_to_block_type("- first item\n-second item"), BlockType.PARAGRAPH)

    def test_ordered_list(self):
        block = "1. first item\n2. second item\n3. third item"

        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_must_start_at_one_and_increment_by_one(self):
        self.assertEqual(block_to_block_type("2. first item\n3. second item"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("1. first item\n3. third item"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("1.first item\n2. second item"), BlockType.PARAGRAPH)

    def test_paragraph(self):
        block = "This is a regular paragraph\nwith another line."

        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


if __name__ == "__main__":
    unittest.main()
