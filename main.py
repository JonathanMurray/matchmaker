import pprint
import random
import numpy
from collections import Counter
import matplotlib.pyplot as plt


# DEFINITIONS
#--------------------------

TEAM_SIZE = 5

class Player:
	def __init__(self, name, mmr):
		self.name = str(name)
		self.mmr = int(mmr)

	def __str__(self):
		return self.name + "(" + str(self.mmr) + ")"

	def __repr__(self):
		return self.__str__()

class Replay:
	def __init__(self, team_1, team_2, winner):
		self.mmr_diff = avg_mmr(team_2) - avg_mmr(team_1)
		self.winner = winner

	def __repr__(self):
		return "mmr diff: " + str(self.mmr_diff)

class PlayerReplay:
	def __init__(self, replay_index, team_number):
		self.replay_index = replay_index
		self.team_number = team_number




# HELPERS
#--------------------------

def avg_mmr(players):
	return sum([p.mmr for p in players]) / len(players)

def play_and_save_replay(team_1, team_2, replays, player_histories):
	winner = play(team_1, team_2)
	replay = Replay(team_1, team_2, winner)
	replays.append(replay)
	replay_index = len(replays) - 1
	for i in range(2):
		team = [team_1, team_2][i]
		for p in team:
			pr = PlayerReplay(replay_index, i + 1)
			add_to_arr_map(p.name, pr, player_histories)

def add_to_arr_map(key, element, multi_map):
	if not key in multi_map:
		multi_map[key] = []
	arr = multi_map[key]
	arr.append(element)

def player_replay_str(p_replay, replays):
	replay = replays[p_replay.replay_index]
	team_number = p_replay.team_number
	victory = team_number == replay.winner
	mmr_diff = replay.mmr_diff if team_number == 2 else - replay.mmr_diff
	return ("Victory" if victory else "Defeat") + " [mmr diff: " + str(mmr_diff) + "]"

def debug(msg):
	if DEBUG:
		print msg


def plot(players, vals_by_name, ylabel):
	mmrs = [p.mmr for p in players]
	yvals = [vals_by_name[p.name] for p in players]
	plt.xlabel('MMR')
	plt.ylabel(ylabel)
	plt.title('Players')
	plt.plot(mmrs, yvals, 'ro')
	plt.grid(True)
	plt.show()



# ENVIRONMENT
# -------------------------

def random_player(name):
	mmr = numpy.random.normal(2200, 600)
	return Player(name, mmr)

def create_players(num):
	arr = [random_player("p" + str(i)) for i in range(num)]
	return dict([(p.name, p) for p in arr])

def player_happiness(p_replay, replays):
	replay = replays[p_replay.replay_index]
	victory = p_replay.team_number == replay.winner
	unfairness = min(1, replay.mmr_diff / 500.0)
	if victory:
		return 100 * (1 - unfairness)
	else:
		return - 100 * unfairness

def is_victory(p_replay, replays):
	index = p_replay.replay_index
	replay = replays[index]
	return p_replay.team_number == replay.winner

def player_winrate(name, histories, replays):
	h = histories[name]
	return sum([1 if is_victory(pr, replays) else 0 for pr in h]) / float(len(h))

def total_player_happiness(name, histories, replays):
	if not name in histories:
		return 0
	h = histories[name]
	return sum([player_happiness(pr, replays) for pr in h])

def play(team_1, team_2):
	mmr1 = avg_mmr(team_1)
	mmr2 = avg_mmr(team_2)
	debug(str(mmr1) + " VS " + str(mmr2))
	diff = mmr2 - mmr1
	rnd = numpy.random.normal(0, 100)
	if rnd < diff: 
		return 2
	else:
		return 1


# ENGINE
# -------------------------

def pick_teams(players):
	copy = list(players)
	random.shuffle(copy)
	team_1 = copy[0 : TEAM_SIZE]
	team_2 = copy[TEAM_SIZE : TEAM_SIZE * 2]
	return (team_1, team_2)





# MAIN
# -------------------------

DEBUG = False
NUM_PLAYERS = 100
NUM_GAMES = 100

replays = []
player_histories = {}
players = create_players(NUM_PLAYERS)

print "Player MMRs: " + str(sorted([p.mmr for p in players.values()]))

for i in range(NUM_GAMES):
	teams = pick_teams(players.values())
	winner = play_and_save_replay(teams[0], teams[1], replays, player_histories)

print "Replays: " + str(replays)

for name in player_histories:
	h = player_histories[name]
	player = players[name]
	happiness = sum([player_happiness(pr, replays) for pr in h])
	print "-----"
	print "Player " + name + " (" + str(player.mmr) + " mmr)"
	print str([player_replay_str(pr, replays) for pr in h])
	print "Happiness: " + str(happiness)


active_players = [p for p in players.values() if p.name in player_histories]

happiness_map = dict([(p.name, total_player_happiness(p.name, player_histories, replays)) for p in active_players])
winrate_map = dict([(p.name, player_winrate(p.name, player_histories, replays)) for p in active_players])
total_happiness = sum([sum([player_happiness(pr, replays) for pr in h]) for h in player_histories.values()])
print "Total happiness: " + str(total_happiness)

plot(active_players, winrate_map, "Win-rate")


