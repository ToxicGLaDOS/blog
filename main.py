#!/usr/bin/env python3
import os, importlib, shutil

import datetime
from utils.decorator import ContentGenerator
import urllib.parse
import xml.etree.ElementTree as ET


posts = []

BLOG_TITLE = "Black Olive Pineapple"

if os.path.exists('output'):
    shutil.rmtree('output')

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
                    posts.extend(obj())
                # Finds top level methods
                # this could recursively check nested classes, but I doubt I'll ever use that so :shrug:
                elif isinstance(obj, object):
                    for sub_name in dir(obj):
                        sub_obj = getattr(obj, sub_name)
                        if isinstance(sub_obj, ContentGenerator):
                            posts.extend(sub_obj())


def make_head():
    return f"""<head>
<link rel="stylesheet" href="styles.css">
<link rel="alternate" type="application/rss+xml" title="{BLOG_TITLE}" href=/rss.xml>
</head>"""

def make_header():
    dropdown = '<header><nav class="top-nav"><div>'
    for category in set([post.category for post in posts]):
        dropdown += f"""
        <div class="dropdown nav-category">
              <a href={category.replace(' ', '-') + '.html'}>{category}</a>
                  <div class="dropdown-content">"""
        # The stuff in the dropdown goes here
        #for post in [post for post in posts if post.category == category]:
        #    dropdown += f"""
        #              <a href="{post.title.replace(' ', '-') + '.html'}">{post.title}</a>
        #              """

        dropdown += f"""
                  </div>
        </div>"""
    dropdown += "</div></nav></header>"
    return dropdown

def make_footer():
    return f"""<footer><section>
    <a href=https://github.com/toxicglados>GitHub</a>
    </section></footer>"""

def make_title(title):
    return f"<h1><a href={get_title_link(title)}>{title}</a></h1>\n"

def make_rss_feed(posts):
    root = ET.Element('rss')
    root.set('version', '2.0')
    root.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
    channel = ET.SubElement(root, 'channel')
    title = ET.SubElement(channel, 'title')
    title.text = BLOG_TITLE
    link = ET.SubElement(channel, 'link')
    link.text = "https://blackolivepineapple.pizza"
    description = ET.SubElement(channel, 'description')
    description.text = "Jeff's blog about more than just pizza!"
    language = ET.SubElement(channel, 'language')
    language.text = "en-us"
    publication_time = datetime.datetime.now(datetime.timezone.utc).astimezone()
    pub_date = ET.SubElement(channel, 'pubDate')
    pub_date.text = publication_time.strftime('%a, %d %b %Y %H:%M:%S %z')

    for post in posts:
        item = ET.SubElement(channel, 'item')
        item_title = ET.SubElement(item, 'title')
        item_title.text = post.title
        item_link = ET.SubElement(item, 'link')
        item_link.text = f"https://blackolivepineapple.pizza/{get_title_link(post.title)}"
        item_description = ET.SubElement(item, 'description')
        item_description.text = post.content
        item_pub_date = ET.SubElement(item, 'pubDate')
        item_pub_date.text = datetime.datetime.strptime(post.date, '%m-%d-%Y %H:%M %z').strftime('%a, %d %b %Y %H:%M:%S %z')
        # The official rss example page uses a link as a GUID but I'm not sure
        # if I like that or not. Or if I even want a guid :shrug:
        # https://www.rssboard.org/files/sample-rss-2.xml
        item_guid = ET.SubElement(item, 'guid')
        item_guid.text = f"https://blackolivepineapple.pizza/{get_title_link(post.title)}"

    return ET.tostring(root)

def normalize_filename(title):
    # This is just cause I don't like space in my filenames :)
    filename = title.replace(' ', '-') + '.html'
    return filename

def get_title_link(title):
    return urllib.parse.quote_plus(title.replace(' ', '-')) + '.html'

# Sort posts by date posted, with most recent first
posts = list(reversed(sorted(posts, key=lambda post: datetime.datetime.strptime(post.date, '%m-%d-%Y %H:%M %z'))))

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
    output_filename = normalize_filename(post.title)
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
    output_filename = normalize_filename(category)
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

# Copy in static content
for file in os.listdir('static'):
    shutil.copy(os.path.join('static', file), os.path.join('output', file))

# Make rss feed
rss = make_rss_feed(posts)
# rss.xml is what xkcd uses, so good enough for me!
with open(os.path.join('output', 'rss.xml'), 'wb') as f:
    f.write(rss)

