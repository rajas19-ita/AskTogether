import bleach
from bleach.css_sanitizer import CSSSanitizer

ALLOWED_TAGS = [
    "p", "br", "blockquote", "pre",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "b", "i", "u", "sup", "sub", "strike", "span", "font",
    "ul", "ol", "li",
    "table", "thead", "tbody", "tr", "td", "th",
    "img", "a"
]

ALLOWED_ATTRIBUTES = {
    "*": ["class", "style"],
    "a": ["href", "title", "target"],
    "img": ["src", "alt", "style"],
    "font": ["color", "style"],
    "table": ["class", "border", "cellpadding", "cellspacing"],
}

ALLOWED_PROTOCOLS = ["http", "https"]

css_sanitizer = CSSSanitizer(
    allowed_css_properties=[
        "color", "background-color", "text-align",
        "width", "height", "margin-left", "margin-right",
        "line-height", "vertical-align", "justify","table","table-bordered"
    ]
)

def sanitize_html(html: str) -> str:
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        css_sanitizer=css_sanitizer,
        strip=True
    )