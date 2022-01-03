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


def make_head():
    return """<head>
<link rel="stylesheet" href="styles.css">
</head>"""

def make_header():
    dropdown = ""
    for category in set([post.category for post in posts]):
        dropdown += f"""<header>
        <nav class="top-nav">
        <div class="dropdown">
              <a href={category.replace(' ', '-') + '.html'}>{category}</a>
                  <div class="dropdown-content">"""

        #for post in [post for post in posts if post.category == category]:
        #    dropdown += f"""
        #              <a href="{post.title.replace(' ', '-') + '.html'}">{post.title}</a>
        #              """

        dropdown += f"""
              </div>
        </div>
        </nav>
        </header>"""

    return dropdown

def make_footer():
    return f"""<footer><section>
    <a href=https://github.com/toxicglados>GitHub</a>
    </section></footer>"""

def make_title(title):
    return f"<h1><a href={title.replace(' ', '-') + '.html'}>{title}</a></h1>\n"

all_posts = ""

all_posts += make_head()
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


# Generate a page per post
for post in posts:
    output_filename = post.title.replace(' ', '-') + '.html'
    page = ""
    page += make_head()
    page += make_header()
    page += "<section>"
    page += make_title(post.title)
    page += post.content
    page += "</section>"
    page += make_footer()
    with open(os.path.join('output', output_filename), 'w') as f:
        f.write(page)

# Generate a page per category
for category in set([post.category for post in posts]):
    output_filename = category.replace(' ', '-') + '.html'
    page = ""
    page += make_head()
    page += make_header()
    page += "<section>"
    for post in [post for post in posts if post.category == category]:
        page += make_title(post.title)
        page += post.content
    page += "</section>"
    page += make_footer()

    with open(os.path.join('output', output_filename), 'w') as f:
        f.write(page)

















