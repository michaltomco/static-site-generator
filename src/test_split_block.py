import unittest

from split_block import markdown_to_blocks


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""

        blocks = markdown_to_blocks(md)

        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_strips_outer_whitespace(self):
        md = "   # Heading   \n\n\t paragraph with padding \t\n"

        blocks = markdown_to_blocks(md)

        self.assertEqual(blocks, ["# Heading", "paragraph with padding"])

    def test_markdown_to_blocks_ignores_empty_blocks(self):
        md = "\n\n\nFirst block\n\n   \n\nSecond block\n\n"

        blocks = markdown_to_blocks(md)

        self.assertEqual(blocks, ["First block", "Second block"])

    def test_markdown_to_blocks_preserves_single_newlines_inside_blocks(self):
        md = "line one\nline two\nline three"

        blocks = markdown_to_blocks(md)

        self.assertEqual(blocks, ["line one\nline two\nline three"])

    def test_markdown_to_blocks_empty_markdown(self):
        self.assertEqual(markdown_to_blocks(""), [])


if __name__ == "__main__":
    unittest.main()
