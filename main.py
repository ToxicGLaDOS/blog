#!/usr/bin/env python3
import os, importlib

from utils.decorator import ContentGenerator

posts = []

for root, dirs, files in os.walk("./content"):
    for file in files:
        if file.endswith('.py') and file != "__init__.py":
            path = os.path.join(root, file)
            # This converts ./foo/bar/baz.py -> foo.bar.baz
            module_import_path = os.path.splitext(path)[0][2:].replace('/', '.')
            module = importlib.import_module(module_import_path)
            for name in dir(module):
                obj = getattr(module, name)
                # Finds top level functions
                if isinstance(obj, ContentGenerator):
                    posts.append(obj())
                # Finds top level methods
                # this could recursively check nested classes, but I doubt I'll ever use that so :shrug:
                elif isinstance(obj, object):
                    for sub_name in dir(obj):
                        sub_obj = getattr(obj, sub_name)
                        if isinstance(sub_obj, ContentGenerator):
                            posts.append(sub_obj())


def make_header():
    return ""

def make_footer():
    return f"""<section>
    <a href=https://github.com/toxicglados>GitHub</a>
    </section>"""

def make_title(title):
    return f"<h1>{title}</h1>\n"

all_posts = ""

all_posts += make_header()

all_posts += "<section>"

for post in posts:
    all_posts += make_title(post.title)
    all_posts += post.content
all_posts += "</section>"

all_posts += make_footer()

os.chdir(os.path.dirname(__file__))
if not os.path.exists('output'):
    os.mkdir('output')

output_filename = "index.html"
with open(os.path.join('output', output_filename), 'w') as f:
    f.write(all_posts)

