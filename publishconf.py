#!/usr/bin/env python
# -*- coding: utf-8 -*- #

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

AUTHOR = 'Jeff Smith'
SITENAME = 'Blackolive Pineapple Blog'
SITEURL = 'https://blackolivepineapple.pizza/'
THEME = 'theme/blackolivepineapple'
PATH = 'content'

TIMEZONE = 'America/Chicago'

DEFAULT_LANG = 'en'

# Blogroll
LINKS = (('Pelican', 'https://getpelican.com/'),
         ('Python.org', 'https://www.python.org/'),
         ('Jinja2', 'https://palletsprojects.com/p/jinja/'),)

# Social widget
SOCIAL = (('GitHub', 'https://github.com/ToxicGLaDOS'),
          ('Runescape', 'https://secure.runescape.com/m=hiscore_oldschool/hiscorepersonal?user1=Shalo123'),)

DEFAULT_PAGINATION = 10

DELETE_OUTPUT_DIRECTORY = True

RELATIVE_URLS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
#GOOGLE_ANALYTICS = ""
