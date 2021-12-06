from markdown import markdown
from markdown.extensions import fenced_code, codehilite


def format_markdown(text: str) -> str:
    return markdown(text,
                    extensions=[fenced_code.makeExtension(),
                                codehilite.makeExtension(user_pygments=True)])
