import datetime
from flask import request, session

def add_handlers(socketio, engine):
  @socketio.on("give_identity")
  def give_identity():
    player = engine.players[int(session["ID"])]
    player.sid = request.sid
  @socketio.on("hide_message")
  def hide_message(message_id):
    player = engine.players[int(session["ID"])]
    player.messages[message_id][1] = datetime.datetime.now()
  @socketio.on("select_color")
  def select_color(color):
    game = engine.game
    assert color in game.colors
    player = engine.players[int(session["ID"])]
    if color in game.owner :
      if game.owner[color] == player :
        player.send_message(engine.text["player_txt"]["color already selected"]\
        [player.lang_id], category="error", persistant=False)
      else:
        player.send_message(engine.text["player_txt"]["color not avalable"]\
        [player.lang_id].format(name = game.owner[color].name),
        category="error", persistant=False)
    else:
      player.choice = color
  @socketio.on("change_language")
  def change_language(lang):
    player = engine.players[int(session["ID"])]
    languages = engine.text["languages_name"]
    assert lang in languages
    new_lang_id = languages.index(lang)
    if new_lang_id != player.lang_id :
      player.lang_id = new_lang_id
      player.lang_txt = lang
      player.send_message(engine.text["player_txt"]["language change"]\
        [new_lang_id])
  @socketio.on("card_action")
  def card_action(take_card, playerID):
    game = engine.game
    current_player = game.current_player
    if playerID == current_player.ID :
      if take_card:
        current_player.cards.add(game.card[0])
        current_player.tokens += game.card[1]
        next_card = game.new_card()
        if next_card:
          game.card = next_card
        else:
          game.end()
      else:
        if current_player.tokens == 0:
          current_player.send_message(engine.text["player_txt"]["no tokens"]\
          [current_player.lang_id], category="error")
        else:
          current_player.tokens -= 1
          game.card[1] += 1
          game.current_player = game.players[(game.current_player.ID + 1) % \
            len(game.players)]
    else:
      game.players[playerID].send_message(engine.text["player_txt"]\
            ["not your turn"][current_player.lang_id], category="error")
    engine.socketio.emit("refresh", broadcast=True)
