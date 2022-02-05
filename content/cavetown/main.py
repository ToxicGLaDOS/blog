import os
from markdown import Markdown
from utils.decorator import ContentGenerator
from utils.post import Post

@ContentGenerator
def markdown_posts() -> list[Post]:
    posts = []
    base_path = os.path.dirname(__file__)
    with open(os.path.join(base_path, 'tilemaps_with_data.md')) as f:
        md = Markdown(extensions=['fenced_code', 'meta', 'codehilite'])
        content = md.convert(f.read())
        metadata = md.Meta # type: ignore
        title = metadata['title'][0]
        category = metadata['category'][0]
        date = metadata['date'][0]
        posts.append(Post(title, category, date, content))

    return posts

if __name__ == "__main__":
    print(markdown_posts())
