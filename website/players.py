from datetime import datetime, timedelta
from flask import Markup, flash

class Player(object):
  def __init__(player, engine, ID, name, lang_id=None):
    player.engine = engine
    player.ID = ID
    player.sid = None
    player.name = name
    player.lang_id = int(lang_id) if lang_id else engine.lang_id
    player.lang_txt = engine.text["languages_name"][player.lang_id]
    player.color = None
    player.messages = []
    player.cards = set()
    player.tokens = 5
    player.score = None
  
  @property
  def sorted_cards(player):
    cards = sorted(player.cards)
    output = []
    series = []
    for i, num in enumerate(cards):
        if not series:
            series.append(num)
        elif num == series[-1] + 1:
            series.append(num)
        else:
            output.append(series)
            series = [num]
    output.append(series)
    return output


  def emit(player, *args):
    if player.sid:
      socketio = player.engine.socketio
      socketio.emit(*args, room=player.sid)
  
  def flash_message(player, message, category="message"):
    flash(Markup(message))
    player.send_message(message, category, emit=False, timeout=-1)

  def send_request(player, message, timeout=600):
    player.send_message(message, category="request", timeout=timeout)
  
  def send_message(player, message, category="message", 
                   emit=True, persistant=True, timeout=30):
    message = Markup(message)
    if persistant:
      now = datetime.now()
      timeout = timedelta(seconds=timeout)
      player.messages.append([now, now + timeout, category, message])
    if emit:
      msg_id = len(player.messages) - 1 if persistant else None
      player.emit("message", (msg_id, category, message))
  
  @property
  def messages_to_show(player):
    now = datetime.now()
    return [(msg_id, category, message) 
      for msg_id, (_, limit, category, message) in enumerate(player.messages) 
      if now <= limit]
