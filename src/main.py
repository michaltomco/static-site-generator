import os
import shutil
import sys

from markdown_processor import markdown_to_html_node


def prepare_files(src, dest):
    if not os.path.exists(src) or not os.path.isdir(src):
        raise Exception(f"Invalid src file at {src}")

    if os.path.exists(dest):
        if not os.path.isdir(dest):
            raise Exception(f"Invalid dest file at {dest}")
        shutil.rmtree(dest)
    shutil.copytree(src=src, dst=dest)


def extract_title(markdown):
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line.lstrip("#").strip()
    raise Exception("No header")


def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    md = ""
    tpf = ""
    if os.path.exists(from_path) and os.path.isfile(from_path):
        with open(from_path) as f:
            md = f.read()
    else:
        raise Exception(f"Invalid from_path {from_path}")
    if os.path.exists(template_path) and os.path.isfile(template_path):
        with open(template_path) as f:
            tpf = f.read()
    else:
        raise Exception(f"Invalid template_path {template_path}")

    html_str = markdown_to_html_node(md).to_html()
    title = extract_title(md)
    html_page = tpf.replace("{{ Title }}", title).replace("{{ Content }}", html_str)
    html_page = html_page.replace('href="/', f'href="{basepath}')
    html_page = html_page.replace('src="/', f'src="{basepath}')

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(html_page)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    if not os.path.exists(dir_path_content) or not os.path.isdir(dir_path_content):
        raise Exception(f"Invalid content directory at {dir_path_content}")

    for entry in os.listdir(dir_path_content):
        content_path = os.path.join(dir_path_content, entry)
        dest_path = os.path.join(dest_dir_path, entry)
        if os.path.isdir(content_path):
            generate_pages_recursive(content_path, template_path, dest_path, basepath)
        elif os.path.isfile(content_path) and content_path.endswith(".md"):
            generate_page(content_path, template_path, dest_path[:-3] + ".html", basepath)


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    prepare_files(src="static", dest="docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)


if __name__ == "__main__":
    main()
