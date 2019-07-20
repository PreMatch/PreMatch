from flask import *
import os.path

help_site = Blueprint("PreMatch Help", __name__, template_folder="templates")


def render_file(filepath):
    if os.path.isdir(filepath):
        index_within = os.path.join(filepath, "index.md")
        if os.path.isfile(index_within):
            return render_template('help_page.html', filepath='/' + index_within)

    filepath += ".md"

    if not os.path.isfile(filepath):
        return render_template('missing_help.html'), 404
    return render_template('help_page.html', filepath='/' + filepath)


def to_filepath(query):
    return f"static/help/{query}"


@help_site.route("/help")
def help_homepage():
    return render_file(to_filepath("index"))


@help_site.route("/help/<path:path>")
def help_inner(path):
    return render_file(to_filepath(path))
