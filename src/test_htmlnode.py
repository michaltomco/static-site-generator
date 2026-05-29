import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_no_props(self):
        node = HTMLNode("a", "Click me")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_with_props(self):
        node = HTMLNode(
            "a",
            "Click me",
            props={"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank" ',
        )

    def test_to_html_not_implemented(self):
        node = HTMLNode("p", "Hello, world!")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_htmlnode_constructor_sets_fields(self):
        child = HTMLNode("span", "child")
        node = HTMLNode("div", "parent", child, {"class": "container"})

        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "parent")
        self.assertEqual(node.children, child)
        self.assertEqual(node.props, {"class": "container"})

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_with_props(self):
        node = LeafNode("a", "Click me", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.google.com" >Click me</a>',
        )

    def test_leaf_to_html_without_tag(self):
        node = LeafNode(None, "Hello, world!")
        self.assertEqual(node.to_html(), "Hello, world!")

    def test_leaf_to_html_missing_value_raises(self):
        node = LeafNode("p", "")
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_parent_to_html_with_multiple_children(self):
        parent_node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, " normal text "),
                LeafNode("i", "italic text"),
            ],
        )
        self.assertEqual(
            parent_node.to_html(),
            "<p><b>Bold text</b> normal text <i>italic text</i></p>",
        )

    def test_parent_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container"})
        self.assertEqual(
            parent_node.to_html(),
            '<div class="container" ><span>child</span></div>',
        )

    def test_parent_to_html_with_nested_props(self):
        child_node = ParentNode(
            "a",
            [LeafNode(None, "click here")],
            {"href": "https://www.google.com"},
        )
        parent_node = ParentNode("p", [LeafNode(None, "Go "), child_node])
        self.assertEqual(
            parent_node.to_html(),
            '<p>Go <a href="https://www.google.com" >click here</a></p>',
        )

    def test_parent_to_html_missing_tag_raises(self):
        parent_node = ParentNode(None, [LeafNode("span", "child")])
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_parent_to_html_missing_children_raises(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_parent_to_html_empty_children_raises(self):
        parent_node = ParentNode("div", [])
        with self.assertRaises(ValueError):
            parent_node.to_html()


if __name__ == "__main__":
    unittest.main()
