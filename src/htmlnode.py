from functools import reduce


class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: "list[HTMLNode]|None" = None,
        props: dict[str, str] | None = None,
    ):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self) -> str:
        #     parts:list[str] = []
        #     if self.props:
        #         for k,v in self.props.items():
        #             parts.append(f"{k}={v} ")
        #     return "".join(parts)
        #

        return (
            " "
            + reduce(lambda a, b: a + b, (f'{k}="{v}" ' for k, v in self.props.items()))
            if self.props
            else ""
        )

    def __repr__(self):
        return f"HTMLNode - {self.tag}, {self.value}, {self.children}, {self.props}"


class LeafNode(HTMLNode):
    def __init__(
        self, tag: str | None, value: str, props: dict[str, str] | None = None
    ):
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self):
        if not self.value:
            raise ValueError

        if not self.tag:
            return self.value

        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"LeafNode - {self.tag}, {self.value}, {self.props}"


class ParentNode(HTMLNode):
    def __init__(
        self, tag: str, children: "list[HTMLNode]", props: dict[str, str] | None = None
    ):
        super().__init__(tag, children=children, props=props)

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("Tag missing!")

        if not self.children:
            raise ValueError("Children missing!")

        return (
            f"<{self.tag}{self.props_to_html()}>"
            f"{''.join(n.to_html() for n in self.children)}"
            f"</{self.tag}>"
        )
