from pygments.lexer import RegexLexer
from pygments.token import (
    Comment, String, Number, Literal, Keyword, Operator, Text
)


class Lexer(RegexLexer):
    """
    A simple lexer for py3status configuration files.
    This helps make the documentation more beautiful
    """
    name = 'Py3status'
    aliases = ['py3status']
    filenames = ['*.conf']

    tokens = {
        'root': [
            (r'#.*?$', Comment),
            (r'"(?:[^"\\]|\\.)*"', String.Double),
            (r"'(?:[^'\\]|\\.)*'", String.Single),
            (r'([0-9]+)|([0-9]*)\.([0-9]*)', Number),
            (r'True|False|None', Literal),
            (r'(\+=)|=', Operator),
            (r'\s+', Text),
            (r'[{}\[\](),:]', Text,),
            (r'\S+', Keyword),
        ],
    }
