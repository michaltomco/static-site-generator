from textnode import TextNode, TextType


def main():
    n = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(n)


main()
