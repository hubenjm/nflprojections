import numpy as np
import nflgame
import pandas as pd
import progressbar
from functools32 import lru_cache

scoring = {
    'passing_yds' : lambda x : x*.04 +
                        (3. if x >= 300 else 0),
    'passing_tds' : lambda x : x*4., 
    'passing_ints' : lambda x : -1.*x,
    'rushing_yds' : lambda x : x*.1 + (3 if x >= 100 else 0),
    'rushing_tds' : lambda x : x*6.,
    'kickret_tds' : lambda x : x*6.,
    'receiving_tds' : lambda x : x*6.,
    'receiving_yds' : lambda x : x*.1,
    'receiving_rec' : lambda x : x,
    'fumbles_lost' : lambda x : -1*x,
    'passing_twoptm'  : lambda x : 2*x,
    'rushing_twoptm' : lambda x : 2*x,
    'receiving_twoptm' : lambda x : 2*x
}

player_names_list = [nflgame.players[s].name for s in nflgame.players]
player_id_list = [nflgame.players[s].player_id for s in nflgame.players] #used as unique keys for other column data
player_list = [nflgame.players[s] for s in nflgame.players]

def score_player(player):
	"""
	player is assumed to be of type <class 'nflgame.player.GamePlayerStats'>, i.e. associated with a specific game
	"""
	score = 0
	for stat in player._stats:
		if stat in scoring:
			score += scoring[stat](getattr(player,stat))    
	return score

@lru_cache(200) # Define a cache with 200 empty slots
def get_games(year,week):
	g = nflgame.games(year,week=week)
	return nflgame.combine_game_stats(g)

def main():
	player_score_sums = dict.fromkeys(player_id_list)
	player_num_samples = dict.fromkeys(player_id_list)
	player_names = dict.fromkeys(player_id_list)
	player_status = dict.fromkeys(player_id_list)

	#initialize dictionaries
	for s in player_id_list:
		player_score_sums[s] = 0.0
		player_num_samples[s] = 0
		player_names[s] = nflgame.players[s].name
		player_status[s] = nflgame.players[s].status

	current_year, current_week = nflgame.live.current_year_and_week()
	years = range(current_year - 2, current_year + 1)
	weeks = dict.fromkeys(years)
	weeks[current_year] = range(1, current_week+1)
	for y in years[:-1]:
		weeks[y] = range(1,18)

	#set up probabilities for choosing a given season (more weight given to current year, scaled based on how many weeks have passed in season)
	p_current_year = 0.5*float(current_week)/17.0
	p_previous_years = 1.0 - p_current_year

	N = 10000 #number of Monte Carlo samples

	for j in xrange(N):
		year = np.random.choice(years, p = [0.25*p_previous_years, 0.75*p_previous_years, p_current_year])
		if year == current_year:
			week = np.random.randint(1, current_week + 1)
		else:
			week = np.random.randint(1,18)

		for p in get_games(year, week):
			#p is a nflgame.player.GamePlayerStats object
			if p.player is None:
				continue
			else:
				player_score_sums[p.playerid] += score_player(p)
				player_num_samples[p.playerid] += 1

		progressbar.printProgress(j+1, N, prefix = "Monte Carlo sample {}".format(j+1), barLength = 40)

	score_sums = pd.DataFrame(player_score_sums.items(), columns = ["playerid", "sum_scores"])
	num_samples = pd.DataFrame(player_num_samples.items(), columns = ["playerid", "num_samples"])
	ave_player_scores = score_sums.copy()
	ave_player_scores['name'] = ave_player_scores['playerid'].map(player_names) #add player names to data frame
	ave_player_scores['num_samples'] = num_samples['num_samples']
	ave_player_scores['status'] = ave_player_scores['playerid'].map(player_status)

	ave_player_scores.columns = ['playerid', 'ave score', 'name', 'num_samples', 'status']
	ave_player_scores['ave score'] /= num_samples['num_samples']
	ave_player_scores = ave_player_scores[np.isfinite(ave_player_scores['ave score'])]

	ave_player_scores = ave_player_scores.sort_values(by='ave score', ascending = False)
	ave_player_scores = ave_player_scores[ave_player_scores['status'] == "ACT"]
	print ave_player_scores.head(n=50)
	
	

#	#add up and average
#	ave_player_scores = dict.fromkeys(player_id_list)
#	for i in player_id_list:
#		if player_num_samples[i] > 0:
#			ave_player_scores[i] = player_score_sums[i]/player_num_samples[i]
#		else:
#			ave_player_scores[i] = 0

#	print ave_player_scores

			

if __name__ == "__main__":
	main()
