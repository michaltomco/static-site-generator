import re

from textnode import TextNode, TextType


def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiters(nodes)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def split_nodes_delimiters(old_nodes: list[TextNode]) -> list[TextNode]:
    nodes = old_nodes
    for delimiter, text_type in [
        ("`", TextType.CODE),
        ("**", TextType.BOLD),
        ("_", TextType.ITALIC),
    ]:
        nodes = split_nodes_delimiter(nodes, delimiter, text_type)
    return nodes

def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    if not old_nodes:
        return []
    if not delimiter:
        return old_nodes

    new_nodes = []

    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            sections = node.text.split(delimiter)
            if len(sections) % 2 == 0:
                raise ValueError("invalid markdown: no closing delimiter")
            for i, t in enumerate(sections):
                if t:
                    new_nodes.append(TextNode(t, text_type if i % 2 else TextType.TEXT))
        else:
            new_nodes.append(node)

    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_complex(old_nodes, TextType.LINK)


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_complex(old_nodes, TextType.IMAGE)


def _split_nodes_complex(
    old_nodes: list[TextNode], text_type: TextType
) -> list[TextNode]:
    if not old_nodes:
        return []

    regex = ""
    if text_type is TextType.IMAGE:
        regex = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    elif text_type is TextType.LINK:
        regex = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"

    new_nodes = []

    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            parts = re.split(regex, node.text)

            for i in range(0, len(parts), 3):
                text = parts[i]
                if text:
                    new_nodes.append(TextNode(text, TextType.TEXT))

                if i + 2 < len(parts):
                    link_text = parts[i + 1]
                    link_url = parts[i + 2]
                    new_nodes.append(TextNode(link_text, text_type, link_url))
        else:
            new_nodes.append(node)

    return new_nodes


def extract_markdown_images(text) -> list[tuple[str, str]]:
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text) -> list[tuple[str, str]]:
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
