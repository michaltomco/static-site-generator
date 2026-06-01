import os
import tempfile
import unittest
import sys
from unittest.mock import patch

from main import (
    extract_title,
    generate_page,
    generate_pages_recursive,
    main,
    prepare_files,
)


class TestPrepareFiles(unittest.TestCase):
    def test_prepare_files_copies_files_and_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "static")
            dest = os.path.join(tmpdir, "public")
            nested = os.path.join(src, "images")
            os.makedirs(nested)
            with open(os.path.join(src, "index.css"), "w") as f:
                f.write("body { color: red; }")
            with open(os.path.join(nested, "logo.png"), "w") as f:
                f.write("image data")

            prepare_files(src, dest)

            with open(os.path.join(dest, "index.css")) as f:
                self.assertEqual(f.read(), "body { color: red; }")
            with open(os.path.join(dest, "images", "logo.png")) as f:
                self.assertEqual(f.read(), "image data")

    def test_prepare_files_replaces_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "static")
            dest = os.path.join(tmpdir, "public")
            os.mkdir(src)
            os.mkdir(dest)
            with open(os.path.join(src, "new.css"), "w") as f:
                f.write("new")
            with open(os.path.join(dest, "old.css"), "w") as f:
                f.write("old")

            prepare_files(src, dest)

            self.assertTrue(os.path.exists(os.path.join(dest, "new.css")))
            self.assertFalse(os.path.exists(os.path.join(dest, "old.css")))

    def test_prepare_files_rejects_missing_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(Exception):
                prepare_files(os.path.join(tmpdir, "missing"), os.path.join(tmpdir, "public"))

    def test_prepare_files_rejects_file_destination(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "static")
            dest = os.path.join(tmpdir, "public")
            os.mkdir(src)
            with open(dest, "w") as f:
                f.write("not a directory")

            with self.assertRaises(Exception):
                prepare_files(src, dest)


class TestMain(unittest.TestCase):
    def test_main_prepares_static_files_for_public_directory(self):
        with patch.object(sys, "argv", ["main.py"]), patch(
            "main.prepare_files"
        ) as mock_prepare_files, patch(
            "main.generate_pages_recursive"
        ) as mock_generate_pages_recursive:
            main()

        mock_prepare_files.assert_called_once_with(src="static", dest="docs")
        mock_generate_pages_recursive.assert_called_once_with(
            "content", "template.html", "docs", "/"
        )

    def test_main_uses_cli_basepath_when_provided(self):
        with patch.object(sys, "argv", ["main.py", "/static-site-generator/"]), patch(
            "main.prepare_files"
        ), patch("main.generate_pages_recursive") as mock_generate_pages_recursive:
            main()

        mock_generate_pages_recursive.assert_called_once_with(
            "content", "template.html", "docs", "/static-site-generator/"
        )


class TestGeneratePage(unittest.TestCase):
    def test_generate_page_replaces_template_placeholders(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_path = os.path.join(tmpdir, "index.md")
            template_path = os.path.join(tmpdir, "template.html")
            dest_path = os.path.join(tmpdir, "public", "index.html")

            with open(markdown_path, "w") as f:
                f.write("# Test Title\n\nThis is **bold** text.")
            with open(template_path, "w") as f:
                f.write("<title>{{ Title }}</title><main>{{ Content }}</main>")

            generate_page(markdown_path, template_path, dest_path, "/")

            with open(dest_path) as f:
                self.assertEqual(
                    f.read(),
                    "<title>Test Title</title>"
                    "<main><div><h1>Test Title</h1>"
                    "<p>This is <b>bold</b> text.</p></div></main>",
                )

    def test_generate_page_rejects_missing_markdown_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = os.path.join(tmpdir, "template.html")
            with open(template_path, "w") as f:
                f.write("{{ Title }} {{ Content }}")

            with self.assertRaises(Exception):
                generate_page(
                    os.path.join(tmpdir, "missing.md"),
                    template_path,
                    os.path.join(tmpdir, "public", "index.html"),
                    "/",
                )

    def test_generate_page_rejects_missing_template_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_path = os.path.join(tmpdir, "index.md")
            with open(markdown_path, "w") as f:
                f.write("# Title")

            with self.assertRaises(Exception):
                generate_page(
                    markdown_path,
                    os.path.join(tmpdir, "missing.html"),
                    os.path.join(tmpdir, "public", "index.html"),
                    "/",
                )

    def test_generate_page_rewrites_root_relative_paths_with_basepath(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_path = os.path.join(tmpdir, "index.md")
            template_path = os.path.join(tmpdir, "template.html")
            dest_path = os.path.join(tmpdir, "docs", "index.html")

            with open(markdown_path, "w") as f:
                f.write("# Title\n\n![alt](/images/pic.png)\n\n[Home](/)")
            with open(template_path, "w") as f:
                f.write('<link href="/index.css" rel="stylesheet" />{{ Content }}')

            generate_page(markdown_path, template_path, dest_path, "/repo/")

            with open(dest_path) as f:
                html = f.read()
            self.assertIn('href="/repo/index.css"', html)
            self.assertIn('src="/repo/images/pic.png"', html)
            self.assertIn('href="/repo/"', html)


class TestGeneratePagesRecursive(unittest.TestCase):
    def test_generate_pages_recursive_generates_matching_html_tree(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content_dir = os.path.join(tmpdir, "content")
            blog_dir = os.path.join(content_dir, "blog", "post")
            dest_dir = os.path.join(tmpdir, "public")
            template_path = os.path.join(tmpdir, "template.html")
            os.makedirs(blog_dir)
            with open(os.path.join(content_dir, "index.md"), "w") as f:
                f.write("# Home\n\nWelcome.")
            with open(os.path.join(blog_dir, "index.md"), "w") as f:
                f.write("# Blog Post\n\nPost body.")
            with open(os.path.join(content_dir, "draft.txt"), "w") as f:
                f.write("# Draft\n\nThis should not be generated.")
            with open(template_path, "w") as f:
                f.write("<title>{{ Title }}</title>{{ Content }}")

            generate_pages_recursive(content_dir, template_path, dest_dir, "/")

            with open(os.path.join(dest_dir, "index.html")) as f:
                self.assertEqual(
                    f.read(),
                    "<title>Home</title><div><h1>Home</h1><p>Welcome.</p></div>",
                )
            with open(os.path.join(dest_dir, "blog", "post", "index.html")) as f:
                self.assertEqual(
                    f.read(),
                    "<title>Blog Post</title>"
                    "<div><h1>Blog Post</h1><p>Post body.</p></div>",
                )
            self.assertFalse(os.path.exists(os.path.join(dest_dir, "draft.html")))

    def test_generate_pages_recursive_rejects_missing_content_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(Exception):
                generate_pages_recursive(
                    os.path.join(tmpdir, "missing"),
                    os.path.join(tmpdir, "template.html"),
                    os.path.join(tmpdir, "public"),
                    "/",
                )


class TestExtractTitle(unittest.TestCase):
    def test_extract_title_returns_h1_text(self):
        markdown = "# My Page Title\n\nThis is body text."

        self.assertEqual(extract_title(markdown), "My Page Title")

    def test_extract_title_ignores_lower_level_headings(self):
        markdown = "## Section Title\n\n# Page Title\n\n### Subsection"

        self.assertEqual(extract_title(markdown), "Page Title")

    def test_extract_title_strips_surrounding_whitespace(self):
        markdown = "#    Padded Title    \n\nContent"

        self.assertEqual(extract_title(markdown), "Padded Title")

    def test_extract_title_requires_h1_at_start_of_line(self):
        markdown = "Paragraph with # not a title\n\n## Not H1"

        with self.assertRaises(Exception):
            extract_title(markdown)


if __name__ == "__main__":
    unittest.main()
