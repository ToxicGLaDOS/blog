import os
from markdown import Markdown
from utils.decorator import ContentGenerator
from utils.post import Post

@ContentGenerator
def nfs():
    os.chdir(os.path.dirname(__file__))
    with open('nfs.md') as f:
        md = Markdown(extensions=['fenced_code', 'meta'])
        content = md.convert(f.read())
        metadata = md.Meta
        title = metadata['title'][0]
        category = metadata['category'][0]
        date = metadata['date'][0]
        return Post(title, category, date, content)

@ContentGenerator
def new_node():
    os.chdir(os.path.dirname(__file__))
    with open('new_node.md') as f:
        md = Markdown(extensions=['fenced_code', 'meta'])
        content = md.convert(f.read())
        metadata = md.Meta
        title = metadata['title'][0]
        category = metadata['category'][0]
        date = metadata['date'][0]
        return Post(title, category, date, content)

if __name__ == "__main__":
    print(nfs())
