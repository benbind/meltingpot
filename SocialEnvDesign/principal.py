import math
import numpy as np

from SocialEnvDesign.voting_mechanism import care_graph_uniform_init, median_of_weighted_median_vote


class Principal:

  def __init__(self, num_players, num_games, starting_objective, fixed_tax=1, sigma_vals=None) -> None:
    self.set_objective(starting_objective)
    self.num_players = num_players
    self.num_games = num_games
    self.player_wealths = {f"game_{idx}" : [0] * num_players for idx in range(num_games)}
    self.collected_tax = {f"game_{idx}" : 0 for idx in range(num_games)}
    self.__tax_brackets = [(1,5),(6,10),(11,10000)]
    self.tax_vals = {f"game_{idx}" : [0,0,0] for idx in range(num_games)}
    self.fixed_tax = fixed_tax
    self.sigma_vals = sigma_vals

    if self.fixed_tax:
      self.fixed_tax_vals(self.fixed_tax)

  def vote_p_value(self, selfishness):
    self.selfishness = selfishness
    self.p_value = (
        math.log(
            median_of_weighted_median_vote(
                selfishness, care_graph_uniform_init(selfishness)
            )
        )
        + 1
    )
    self.sigma_tax_vals(self.selfishness)
    
  def update_tax_vals(self, actions):
    if not self.fixed_tax:
      for game_id in range(self.num_games):
        tax_choices = actions[game_id]
        for bracket_idx in range(len(tax_choices)):
          tax_val = tax_choices[bracket_idx].item()
          if tax_val != 11:
            self.tax_vals[f"game_{game_id}"][bracket_idx] = tax_val/10

  def sigma_tax_vals(self, selfishness):
    if self.fixed_tax == "4":
      sigma_avg = median_of_weighted_median_vote(
          selfishness, care_graph_uniform_init(selfishness)
      )
      base_tax = 1 - sigma_avg
      self.tax_vals = {
          f"game_{idx}": [base_tax * 0.5, base_tax, min(1, base_tax * 1.5)]
          for idx in range(self.num_games)
      }

  def fixed_tax_vals(self, fixed_tax):
    if fixed_tax == "1":
      self.tax_vals = {f"game_{idx}" : [0,.6,1] for idx in range(self.num_games)}
    if fixed_tax == "2": # U.S. federal
      self.tax_vals = {f"game_{idx}" : [.1,.25,.37] for idx in range(self.num_games)}
    if fixed_tax == "3": # Libertarian
      self.tax_vals = {f"game_{idx}" : [0,0,0] for idx in range(self.num_games)}
    if fixed_tax not in ["1", "2", "3", "4"]:
      raise ValueError("Invalid fixed_tax value. Must be 1, 2, 3, or 4")

  def set_objective(self, objective):
    objective = 'utilitarian' #!!! only utilitarian for now, remove later

    print("-----------Setting objective to", objective)
    if objective == "egalitarian":
      self.objective = self.egalitarian
    elif objective == "utilitarian":
      self.objective = self.utilitarian

  # tax calculated at the end of an episode based off player wealth for that episode
  def end_of_tax_period(self) -> float:
    games_taxes = {}
    total_collected = {}
    for game_id in self.player_wealths.keys():
      player_wealths = self.player_wealths[game_id]
      tax_vals = self.tax_vals[game_id]
      taxes = list(map(lambda x: self.__tax_calculator(x, self.__tax_brackets, tax_vals), player_wealths))
      total_collected[game_id] = sum(taxes)
      redistribution_amount = sum(taxes)/self.num_players
      games_taxes[game_id] = list(map(lambda x: x - redistribution_amount, taxes))
      # new_wealths = [wealth - tax + redistribution_amount for (wealth,tax) in zip(player_wealths,taxes)]
      # new_player_wealths[game_id] = new_wealths

    # reset player wealths for next tax period
    self.player_wealths = {f"game_{idx}" : [0] * self.num_players for idx in range(self.num_games)}

    return games_taxes

  def __tax_calculator(self, wealth, brackets, tax_vals):
    tax = 0
    for i, (lower,upper) in enumerate(brackets):
      (lower, upper) = brackets[i]
      tax_val = tax_vals[i]
      if wealth > lower:
        applicable_wealth=min(wealth, upper) - lower + 1
        tax += applicable_wealth * tax_val
    return tax

  def report_reward(self, reward) -> None:
    for i in range(len(reward)):
      game_id = i // self.num_players
      player_id = i % self.num_players
      self.player_wealths[f"game_{game_id}"][player_id] += reward[i]

  def utilitarian(self, reward):
    """Utilitarian objective"""
    result = []
    for i in range(0,len(reward),self.num_players):
      result.append(np.mean(reward[i:i+self.num_players]))

    return np.array(result).flatten()

  def egalitarian(self, reward):
    """Egalitarian objective"""
    return min(reward)
