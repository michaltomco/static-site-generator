import os
import shutil

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


def generate_page(from_path, template_path, dest_path):
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

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(html_page)


def main():
    prepare_files(src="static", dest="public")
    generate_page("content/index.md", "template.html", "public/index.html")


if __name__ == "__main__":
    main()
