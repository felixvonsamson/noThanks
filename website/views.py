from flask import current_app, request, session, g
from flask import render_template, redirect, url_for, flash
from flask import Blueprint

views = Blueprint("views", __name__)
flash_error = lambda msg: flash(msg, category="error")

@views.before_request
def check_user():
  g.engine = current_app.config["engine"]
  assert session["ID"] in range(len(g.engine.players))
  g.player = g.engine.players[session["ID"]]
  def render_template_ctx(page):
    return render_template(page, engine=g.engine, player=g.player)
  g.render_template_ctx = render_template_ctx

@views.route("/", methods=["GET", "POST"])
def home():
  return g.render_template_ctx("table.jinja")
