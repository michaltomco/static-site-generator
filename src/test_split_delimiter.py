import unittest

from split_delimiter import split_nodes_delimiter
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_nodes_code_delimiter(self):
        nodes = [TextNode("This is text with a `code block` word", TextType.TEXT)]

        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_split_nodes_bold_delimiter(self):
        nodes = [TextNode("This is **bold** text", TextType.TEXT)]

        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)

        self.assertEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_split_nodes_italic_delimiter(self):
        nodes = [TextNode("This is _italic_ text", TextType.TEXT)]

        new_nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)

        self.assertEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_split_nodes_multiple_delimited_sections(self):
        nodes = [TextNode("Start `one` middle `two` end", TextType.TEXT)]

        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(
            new_nodes,
            [
                TextNode("Start ", TextType.TEXT),
                TextNode("one", TextType.CODE),
                TextNode(" middle ", TextType.TEXT),
                TextNode("two", TextType.CODE),
                TextNode(" end", TextType.TEXT),
            ],
        )

    def test_split_nodes_multiple_input_nodes(self):
        nodes = [
            TextNode("First `code` node", TextType.TEXT),
            TextNode(" and second `code` node", TextType.TEXT),
        ]

        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(
            new_nodes,
            [
                TextNode("First ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" node", TextType.TEXT),
                TextNode(" and second ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" node", TextType.TEXT),
            ],
        )

    def test_split_nodes_preserves_non_text_nodes(self):
        code_node = TextNode("already code", TextType.CODE)
        nodes = [
            TextNode("plain `code`", TextType.TEXT),
            code_node,
            TextNode("also **bold**", TextType.TEXT),
        ]

        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(
            new_nodes,
            [
                TextNode("plain ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                code_node,
                TextNode("also **bold**", TextType.TEXT),
            ],
        )
        self.assertIs(new_nodes[2], code_node)

    def test_split_nodes_unmatched_delimiter_raises(self):
        nodes = [TextNode("This has an `opening delimiter", TextType.TEXT)]

        with self.assertRaises(ValueError):
            split_nodes_delimiter(nodes, "`", TextType.CODE)

    def test_split_nodes_empty_input(self):
        self.assertEqual(split_nodes_delimiter([], "`", TextType.CODE), [])

    def test_split_nodes_empty_delimiter_returns_original_nodes(self):
        nodes = [TextNode("plain text", TextType.TEXT)]

        new_nodes = split_nodes_delimiter(nodes, "", TextType.CODE)

        self.assertIs(new_nodes, nodes)

    def test_split_nodes_drops_empty_sections(self):
        nodes = [TextNode("`code`", TextType.TEXT)]

        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(new_nodes, [TextNode("code", TextType.CODE)])


if __name__ == "__main__":
    unittest.main()
