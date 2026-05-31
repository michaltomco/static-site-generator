from textnode import TextNode, TextType


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    if not old_nodes:
        return []
    if not delimiter:
        return old_nodes

    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            sections = node.text.split(delimiter)
            if len(sections) % 2 == 0:
                raise ValueError("invalid markdown: no closing delimiter")
            for i,t in enumerate(sections):
                if t:
                    new_nodes.append(TextNode(t, text_type if i%2 else TextType.TEXT))




    return new_nodes
