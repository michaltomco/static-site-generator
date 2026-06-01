import unittest

from markdown_processor import (
    code_to_html_node,
    heading_to_html_node,
    markdown_to_html_node,
    olist_to_html_node,
    paragraph_to_html_node,
    quote_to_html_node,
    text_to_children,
    ulist_to_html_node,
)


class TestMarkdownProcessor(unittest.TestCase):
    def test_text_to_children_converts_inline_markdown(self):
        children = text_to_children(
            "This has **bold**, _italic_, `code`, and a [link](https://boot.dev)"
        )

        self.assertEqual(
            [child.to_html() for child in children],
            [
                "This has ",
                "<b>bold</b>",
                ", ",
                "<i>italic</i>",
                ", ",
                "<code>code</code>",
                ", and a ",
                '<a href="https://boot.dev" >link</a>',
            ],
        )

    def test_paragraph_joins_lines_and_processes_inline_markdown(self):
        node = paragraph_to_html_node("This is **bold** text\non a new line")

        self.assertEqual(
            node.to_html(),
            "<p>This is <b>bold</b> text on a new line</p>",
        )

    def test_heading_uses_hash_count_as_heading_level(self):
        node = heading_to_html_node("### A _heading_")

        self.assertEqual(node.to_html(), "<h3>A <i>heading</i></h3>")

    def test_heading_rejects_missing_heading_text(self):
        with self.assertRaises(ValueError):
            heading_to_html_node("#")

    def test_code_block_wraps_raw_text_in_pre_and_code(self):
        node = code_to_html_node("```\nprint('hello')\n```")

        self.assertEqual(node.to_html(), "<pre><code>print('hello')\n</code></pre>")

    def test_code_block_rejects_invalid_fence(self):
        with self.assertRaises(ValueError):
            code_to_html_node("```print('hello')```")

    def test_unordered_list_creates_list_items(self):
        node = ulist_to_html_node("- one\n- **two**")

        self.assertEqual(node.to_html(), "<ul><li>one</li><li><b>two</b></li></ul>")

    def test_ordered_list_creates_list_items(self):
        node = olist_to_html_node("1. one\n2. `two`")

        self.assertEqual(
            node.to_html(),
            "<ol><li>one</li><li><code>two</code></li></ol>",
        )

    def test_quote_strips_markers_and_joins_lines(self):
        node = quote_to_html_node("> first line\n> second **line**")

        self.assertEqual(
            node.to_html(),
            "<blockquote>first line second <b>line</b></blockquote>",
        )

    def test_markdown_to_html_node_converts_mixed_blocks(self):
        markdown = """
# Title

This is a paragraph with **bold** text.

- item one
- item two

> quoted
> text
"""

        node = markdown_to_html_node(markdown)

        self.assertEqual(
            node.to_html(),
            "<div>"
            "<h1>Title</h1>"
            "<p>This is a paragraph with <b>bold</b> text.</p>"
            "<ul><li>item one</li><li>item two</li></ul>"
            "<blockquote>quoted text</blockquote>"
            "</div>",
        )


if __name__ == "__main__":
    unittest.main()
