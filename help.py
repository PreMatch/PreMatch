from flask import *

help_site = Blueprint("PreMatch Help", __name__, template_folder="templates")


@help_site.route("/help")
def redirect_to_gitbook():
    return redirect("//help.prematch.org", code=301)
