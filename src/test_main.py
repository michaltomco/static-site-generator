import os
import tempfile
import unittest
from unittest.mock import patch

from main import extract_title, generate_page, main, prepare_files


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
        with patch("main.prepare_files") as mock_prepare_files, patch(
            "main.generate_page"
        ) as mock_generate_page:
            main()

        mock_prepare_files.assert_called_once_with(src="static", dest="public")
        mock_generate_page.assert_called_once_with(
            "content/index.md", "template.html", "public/index.html"
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

            generate_page(markdown_path, template_path, dest_path)

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
