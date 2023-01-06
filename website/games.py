import random
import numpy as np
from abc import ABC, abstractmethod
from flask import Markup

from .text import color_names, logs_txt, player_txt

class The_game():
  def __init__(game, engine):
    game.engine = engine
    game.players = engine.players
    game.deck = game.init_deck()
    game.card = game.new_card()
    game.current_player = random.choice(game.players)

  def init_deck(game):
    deck = list(range(3, 36))
    for i in range(9):
        deck.remove(random.choice(deck))
    random.shuffle(deck)
    return deck

  def new_card(game):
    if len(game.deck) > 0:
      card = game.deck.pop(0)
      return [card, 0]
    else :
      return None

  def end(game):
    for player in game.players:
      player.score = 0
      for set in player.sorted_cards:
        player.score += set[0]
      player.score -= player.tokens
    game.card = "END"

