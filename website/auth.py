from flask import current_app, request, session
from flask import render_template, redirect, url_for, flash
from flask import Blueprint

from .text import player_txt, logs_txt

auth = Blueprint("auth", __name__)

@auth.route("/login", methods = ["GET", "POST"])
def login():
  engine = current_app.config["engine"]
  if request.method == "POST":
    first_name = request.form.get("firstName")
    if first_name in engine.players_by_name.keys():
      player = engine.players_by_name[first_name]
      engine.log(logs_txt["connected"][engine.lang_id].format(
        name=first_name))
      player.flash_message(player_txt["connected"][player.lang_id])
      session["ID"] = player.ID
      engine.save_data()
      return redirect(url_for("views.home"))
    else:
      flash(player_txt["not recognized"][engine.lang_id], category = "error")
  return render_template("login.jinja", engine=engine)
