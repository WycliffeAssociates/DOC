from typing import List
import os


def get_api_root() -> str:
    return os.environ.get("API_ROOT", "/api/v1")


def get_api_url() -> str:
    host = os.environ.get("API_HOST", "localhost")
    port = 5005 if host == "localhost" else 80
    root = get_api_root()
    return f"http://{host}:{port}{root}"


# FIXME Proper setting of working_dir is currently being handled by
# convert_html2pdf method of document_generator instance.
# NOTE This should be using IRG_WORKING_DIR if it is set in the shell,
# but this presupposes that the call to python -m test_flask on the
# tools repo is being called on the same shell as Docker container is
# being run in. But until now, I've been running tools in a fish shell
# and Docker container in a zshell.
def get_working_dir() -> str:
    """ The directory where the resources will be placed once
    acquired. IRG_WORKING_DIR is provided when running in a docker
    environment. Otherwise a suitable temporary local directory is
    generated automatically. """
    dir: str = ""
    if os.environ.get("IN_CONTAINER"):
        dir = os.environ.get("IRG_WORKING_DIR", "working/temp")
    else:
        dir = os.environ.get("IRG_WORKING_DIR", "../working/temp")
    return dir


def get_output_dir() -> str:
    """ The directory where the generated documents are placed. """
    dir: str = ""
    if os.environ.get("IN_CONTAINER"):
        dir = os.environ.get("IRG_OUTPUT_DIR", "working/temp")
    else:
        dir = os.environ.get("IRG_OUTPUT_DIR", "../working/temp")
    return dir


def get_translations_json_location() -> str:
    """ The location where the JSON data file that we use to lookup
    location of resources is located. """
    loc = os.environ.get(
        "TRANSLATIONS_JSON_LOCATION",
        "http://bibleineverylanguage.org/wp-content/themes/bb-theme-child/data/translations.json",
    )
    return loc


def get_individual_usfm_url_jsonpath() -> str:
    """ The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    individual USFM files (per bible book) may be found. """
    return "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='usfm'].url"


def get_resource_url_level_1_jsonpath() -> str:
    """ The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    resource URL, e.g., tn, tq, ta, obs, ulb, udb, etc., may normally be found. """
    return "$[?code='{}'].contents[?code='{}'].links[?format='zip'].url"


def get_resource_url_level_2_jsonpath() -> str:
    """ The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    resource URL, e.g., tn, tq, ta, obs, ulb, udb, etc., may
    additionally/alternatively be found. """
    return "$[?code='{}'].contents[*].subcontents[?code='{}'].links[?format='zip'].url"


def get_resource_download_format_jsonpath() -> str:
    """ The jsonpath location in TRANSLATIONS_JSON_LOCATION file where
    resource git repo may be found. """
    return "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='Download'].url"


def get_logging_config_file_path() -> str:
    """ The file path location where the dictConfig-style yaml
    formatted config file for logging is located. """
    filepath: str = ""
    if os.environ.get("IN_CONTAINER"):
        filepath = os.environ.get("LOGGING_CONFIG", "document/logging_config.yaml")
    else:
        filepath = "document/logging_config.yaml"
    return filepath


# FIXME Icon no longer lives at this location since they redesigned
# their website. For now I just copy over an old version of the icon
# into ./working/temp/.
def get_icon_url() -> str:
    """ Get the tn-icon.png from unfolding word. """
    return "https://unfoldingword.org/assets/img/icon-tn.png"
    # return "https://static1.squarespace.com/static/591e003db8a79bd6e6c9ffae/t/5e306da5898d7b14b76889dd/1600444722464/?format=1500w"


# def get_markdown_resource_types() -> List[str]:
#     """ Get the resource types that can have a Markdown file. """
#     return ["tn", "tq", "tw", "ta", "tn-wa", "tq-wa", "tw-wa", "ta-wa"]


# FIXME Fix literal paths now that directory organization has changed
def get_tex_format_location() -> str:
    """ Return the location of where the format.tex file is located
    that is used in converting the HTML to PDF using pandoc. """
    filepath: str = ""
    if os.getenv("IN_CONTAINER"):
        filepath = os.environ.get("TEX_FORMAT_FILEPATH", "../tex/format.tex")
    else:
        filepath = "../tex/format.tex"
    return filepath


# FIXME Fix literal paths now that directory organization has changed
def get_tex_template_location() -> str:
    """ Return the location of where the template.tex file is located
    that is used in converting the HTML to PDF using pandoc. """
    filepath: str = ""
    if os.getenv("IN_CONTAINER"):
        filepath = os.environ.get("TEX_TEMPLATE_FILEPATH", "../tex/template.tex")
    else:
        filepath = "../tex/template.tex"
    return filepath


def get_markdown_doc_file_names() -> List[str]:
    """ Return the file names, excluding suffix, of files that do not
    contain content but which may be in the same directory or
    subdirectories of a resource's acquired files. """
    return ["readme", "license"]


def get_document_html_header() -> str:
    """ Return the enclosing HTML and body element format string used
    to enclose the document's HTML content which was aggregated from
    all the resources in the document request. """
    return """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"></meta>
    <title>Bible</title>
    <style media="all" type="text/css">
        .indent-0 {
            margin-left:0em;
            margin-bottom:0em;
            margin-top:0em;
        }
        .indent-1 {
            margin-left:0em;
            margin-bottom:0em;
            margin-top:0em;
        }
        .indent-2 {
            margin-left:1em;
            margin-bottom:0em;
            margin-top:0em;
        }
        .indent-3 {
            margin-left:2em;
            margin-bottom:0em;
            margin-top:0em;
        }
        .c-num {
            color:gray;
        }
        .v-num {
            color:gray;
        }
        .tetragrammaton {
            font-variant: small-caps;
        }
        .footnotes {
            font-size: 0.8em;
        }
        .footnotes-hr {
            width: 90%;
        }
    </style>
</head>
<body>
"""


def get_document_html_footer() -> str:
    """ Return the enclosing HTML and body element format string used
    to enclose the document's HTML content which was aggregated from
    all the resources in the document request. """
    return """
        </div>
    </body>
</html>
"""


# Generate PDF from HTML
PANDOC_COMMAND = """pandoc \
--verbose \
--pdf-engine="xelatex" \
--template={8} \
--toc \
--toc-depth=2 \
-V documentclass="scrartcl" \
-V classoption="oneside" \
-V geometry='hmargin=2cm' \
-V geometry='vmargin=3cm' \
-V title="{0}" \
-V subtitle="Translation Notes" \
-V logo="{4}/icon-tn.png" \
-V date="{1}" \
-V revision_date="{6}" \
-V version="{2}" \
-V mainfont="Raleway" \
-V sansfont="Raleway" \
-V fontsize="13pt" \
-V urlcolor="Bittersweet" \
-V linkcolor="Bittersweet" \
-H {7} \
-o "{3}/{5}.pdf" \
"{3}/{5}.html"
"""

# Generate just LaTeX output so that we can debug LaTeX issues.
PANDOC_COMMAND2 = """pandoc -f html -t latex \
--verbose \
--template={8} \
--toc \
--toc-depth=2 \
-V documentclass="scrartcl" \
-V classoption="oneside" \
-V geometry='hmargin=2cm' \
-V geometry='vmargin=3cm' \
-V title="{0}" \
-V subtitle="Translation Notes" \
-V logo="{4}/icon-tn.png" \
-V date="{1}" \
-V revision_date="{6}" \
-V version="{2}" \
-V mainfont="Raleway" \
-V sansfont="Raleway" \
-V fontsize="13pt" \
-V urlcolor="Bittersweet" \
-V linkcolor="Bittersweet" \
-H {7} \
-o "{3}/{5}.latex" \
"{3}/{5}.html"
"""

# FIXME There is some issue with the HTML to LaTeX generation or from
# the LaTeX to PDF generation. It may be wise to tell pandoc to
# generate LaTeX from HTML also so that we can debug the LaTeX.
def get_pandoc_command() -> str:
    """ Return the pandoc command format string. """
    return PANDOC_COMMAND2


def get_english_repos_dict() -> dict:
    """ This is a hack to compensate for translations.json which only
    provides URLs for PDF assets in the English language. We need USFM
    and Markdown. """
    return {
        "ulb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_ulb",
        "udb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_udb",
        "tn-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn",
        "tw-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tw",
        "tq-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tq",
    }
