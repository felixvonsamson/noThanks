import datetime
import pickle
import secrets
import logging

from .players import Player

from .games import The_game
from .text import languages_name, color_names, logs_txt, player_txt, html_txt

class gameEngine(object):

  def __init__(engine, players_raw, lang_id):
    engine.lang_id = lang_id
    engine.lang_txt = languages_name[lang_id]
    engine.text = {
      "languages_name" : languages_name, 
      "color_names" : color_names,
      "logs_txt" : logs_txt,
      "player_txt" : player_txt,
      "html_txt" : html_txt
    }
    engine.n_players = [3, 4, 5, 6, 7, 8] # possible number of players
    
    engine.socketio = None
    engine.admin_sid = None

    engine.logger = logging.getLogger("Flouze")
    engine.init_logger()
    engine.logs = []
    engine.nonces = set()
    
    assert (len(players_raw) in engine.n_players)
    engine.players = [Player(engine, *player_raw)
              for player_raw in players_raw]
    for i, player in enumerate(engine.players):
      player.other_players = engine.players.copy()
      player.other_players.pop(i)
    engine.players_by_name = { player.name:player for player in engine.players }
    
    engine.log(logs_txt["start"][engine.lang_id])

    engine.game = The_game(engine)

  def init_logger(engine):
    engine.logger.setLevel(logging.INFO)
    s_handler = logging.StreamHandler()
    s_handler.setLevel(logging.INFO)
    engine.logger.addHandler(s_handler)

  def get_nonce(engine):
    while True:
      nonce = secrets.token_hex(16)
      if nonce not in engine.nonces:
        return nonce
  
  def use_nonce(engine, nonce):
    if nonce in engine.nonces:
      return False
    engine.nonces.add(nonce)
    return True
  
  def force_refresh(engine):
    engine.socketio.emit("refresh", broadcast=True)

  def update_fields(engine, updates, players=None):
    socketio = engine.socketio
    if players:
      for player in players:
        if player.sid:
          player.emit("update_data", updates)
    else:
      socketio.emit("update_data", updates, broadcast=True)

  def log(engine, message):
    log_message = datetime.datetime.now().strftime("%H:%M:%S : ") + message
    engine.logger.info(log_message)
    engine.logs.append(log_message)


  def save_data(engine):
    socketio = engine.socketio
    engine.socketio = None
    with open("data.pck", "wb") as file:
      pickle.dump(engine, file)
    engine.socketio = socketio

  @staticmethod
  def load_data():
    with open("data.pck", "rb") as file:
      engine = pickle.load(file)
    engine.init_logger()
    for player in engine.players:
      player.sid = None
    return engine
