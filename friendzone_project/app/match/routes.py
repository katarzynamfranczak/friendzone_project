from . import match_bp
from friendzone_project.app.match.services import save_search_result, find_and_save_match


@match_bp.route("/", methods=["GET", "POST"])
def save_and_match():
    save_search_result()

    return find_and_save_match()



