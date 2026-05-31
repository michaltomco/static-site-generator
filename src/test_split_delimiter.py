import unittest

from split_delimiter import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    split_nodes_delimiter,
    split_nodes_delimiters,
    text_to_textnodes,
)
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


class TestSplitNodesDelimiters(unittest.TestCase):
    def test_split_nodes_delimiters(self):
        nodes = [
            TextNode("This has `code`, **bold**, and _italic_ text", TextType.TEXT)
        ]

        new_nodes = split_nodes_delimiters(nodes)

        self.assertEqual(
            new_nodes,
            [
                TextNode("This has ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(", ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(", and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.TEXT),
            ],
        )


class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )

        self.assertEqual(matches, [("image", "https://i.imgur.com/zjjcJKZ.png")])

    def test_extract_markdown_images_multiple(self):
        matches = extract_markdown_images(
            "![first](https://example.com/first.png) and "
            "![second](https://example.com/second.jpg)"
        )

        self.assertEqual(
            matches,
            [
                ("first", "https://example.com/first.png"),
                ("second", "https://example.com/second.jpg"),
            ],
        )

    def test_extract_markdown_images_ignores_links(self):
        matches = extract_markdown_images(
            "This [link](https://boot.dev) is not an image"
        )

        self.assertEqual(matches, [])

    def test_extract_markdown_links(self):
        matches = extract_markdown_links("This is a [link](https://boot.dev)")

        self.assertEqual(matches, [("link", "https://boot.dev")])

    def test_extract_markdown_links_multiple(self):
        matches = extract_markdown_links(
            "[Boot.dev](https://boot.dev) and [Google](https://google.com)"
        )

        self.assertEqual(
            matches,
            [
                ("Boot.dev", "https://boot.dev"),
                ("Google", "https://google.com"),
            ],
        )

    def test_extract_markdown_links_ignores_images(self):
        matches = extract_markdown_links(
            "This ![image](https://i.imgur.com/zjjcJKZ.png) is not a link"
        )

        self.assertEqual(matches, [])

    def test_extract_markdown_no_matches(self):
        self.assertEqual(extract_markdown_images("plain text"), [])
        self.assertEqual(extract_markdown_links("plain text"), [])


class TestSplitNodesLink(unittest.TestCase):
    def test_split_nodes_link(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_link([node])

        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            ],
        )

    def test_split_nodes_link_multiple_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) "
            "and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_link([node])

        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube",
                    TextType.LINK,
                    "https://www.youtube.com/@bootdotdev",
                ),
            ],
        )

    def test_split_nodes_link_starts_with_link(self):
        node = TextNode(
            "[to boot dev](https://www.boot.dev) and text after",
            TextType.TEXT,
        )

        new_nodes = split_nodes_link([node])

        self.assertEqual(
            new_nodes,
            [
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and text after", TextType.TEXT),
            ],
        )

    def test_split_nodes_link_preserves_non_text_nodes(self):
        link_node = TextNode("already linked", TextType.LINK, "https://boot.dev")

        new_nodes = split_nodes_link([link_node])

        self.assertEqual(new_nodes, [link_node])
        self.assertIs(new_nodes[0], link_node)

    def test_split_nodes_link_ignores_images(self):
        node = TextNode("![alt](https://example.com/image.png)", TextType.TEXT)

        new_nodes = split_nodes_link([node])

        self.assertEqual(
            new_nodes,
            [TextNode("![alt](https://example.com/image.png)", TextType.TEXT)],
        )


class TestSplitNodesImage(unittest.TestCase):
    def test_split_nodes_image(self):
        node = TextNode(
            "This is text with an image ![alt text](https://example.com/img.png)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_image([node])

        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with an image ", TextType.TEXT),
                TextNode("alt text", TextType.IMAGE, "https://example.com/img.png"),
            ],
        )

    def test_split_nodes_image_multiple_images(self):
        node = TextNode(
            "![first](https://example.com/first.png) and "
            "![second](https://example.com/second.png)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_image([node])

        self.assertEqual(
            new_nodes,
            [
                TextNode("first", TextType.IMAGE, "https://example.com/first.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("second", TextType.IMAGE, "https://example.com/second.png"),
            ],
        )

    def test_split_nodes_image_preserves_non_text_nodes(self):
        image_node = TextNode("already image", TextType.IMAGE, "https://example.com")

        new_nodes = split_nodes_image([image_node])

        self.assertEqual(new_nodes, [image_node])
        self.assertIs(new_nodes[0], image_node)

    def test_split_nodes_image_ignores_links(self):
        node = TextNode("[link](https://example.com)", TextType.TEXT)

        new_nodes = split_nodes_image([node])

        self.assertEqual(
            new_nodes,
            [TextNode("[link](https://example.com)", TextType.TEXT)],
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes(self):
        text = (
            "This is **bold** and _italic_ text with `code`, "
            "an image ![alt](https://example.com/image.png), "
            "and a [link](https://boot.dev)"
        )

        nodes = text_to_textnodes(text)

        self.assertEqual(
            nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text with ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(", an image ", TextType.TEXT),
                TextNode("alt", TextType.IMAGE, "https://example.com/image.png"),
                TextNode(", and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
