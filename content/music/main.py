import os
from markdown import Markdown
from utils.decorator import ContentGenerator
from utils.post import Post

@ContentGenerator
def markdown_posts() -> list[Post]:
    posts = []
    base_path = os.path.dirname(__file__)
    for obj in os.listdir(base_path):
        path = os.path.join(base_path, obj)
        # Get every .md file
        if os.path.isfile(path) and os.path.splitext(path)[1] == ".md":
            with open(os.path.join(base_path, obj)) as f:
                md = Markdown(extensions=['meta', 'tables', 'attr_list', 'pymdownx.tilde'])
                content = md.convert(f.read())
                metadata = md.Meta # type: ignore
                title = metadata['title'][0]
                category = metadata['category'][0]
                date = metadata['date'][0]
                posts.append(Post(title, category, date, content))

    return posts

if __name__ == "__main__":
    print(markdown_posts())
