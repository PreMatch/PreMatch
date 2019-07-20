from flask import *
from auth import logged_handle
import os.path

help_site = Blueprint("PreMatch Help", __name__, template_folder="templates")


def render_file(filepath):
    def render_path(template, **kwargs):
        return render_template(template, is_logged_in=logged_handle() is not None, **kwargs)

    if os.path.isdir(filepath):
        index_within = filepath + "/index.md" if not filepath.endswith('/') else filepath + "index.md"
        if os.path.isfile(index_within):
            return render_path('help_page.html', filepath='/' + index_within)

    filepath += ".md"

    if not os.path.isfile(filepath):
        return render_path('missing_help.html'), 404
    return render_path('help_page.html', filepath='/' + filepath)


def to_filepath(query):
    return f"static/help/{query}"


@help_site.route("/help")
def help_homepage():
    return render_file(to_filepath("index"))


@help_site.route("/help/<path:path>")
def help_inner(path):
    return render_file(to_filepath(path))
