import pickle
import joblib

def normalize_data(data, mean, std_dev):
	normalized_data = []
	for row in data:
		normalized_row = [(value - mean_val) / std_dev_val for value, mean_val, std_dev_val in zip(row, mean, std_dev)]
		normalized_data.append(normalized_row)
	return normalized_data

def get_prediction(A2B, B2A):
	win = [0, 0]

	#X_new = new_data.drop(['team','o_team','rpts'], axis=1).values
	X_new = []
	X_new.append(A2B)
	X_new.append(B2A)
	#print(X_new)
	#fga, fgm/fga, 3pa, 3pm/3pa, fta, ftm/fta, oreb, dreb, ast, stl, blk, tov, pf, pts,
	#ofga, ofgm/ofga, o3pa, o3pm/o3pa, ofta, oftm/ofta, ooreb, odreb, oast, ostl, oblk, otov, opf, opts

	X_mean = [88.39160163,0.4691566,34.74355277,0.358117068,22.74509671,0.779780964,10.45417374,33.44219545,25.21398032,7.457193756,4.765778758,13.91180862,19.80035629,113.105531,
			88.38642687,0.46910078,34.7454600,0.358451646,22.74518154,0.779506787,10.45800814,33.44051578,25.21029861,7.455683746,4.762385477,13.91633865,19.79823549,113.109586]

	X_sd = [2.439006311,0.01530458,3.424561418,0.015386437,1.735023345,0.027195505,1.332207023,1.500484451,1.847091633,0.75481485,0.764560297,1.039700491,1.126560177,3.986389531,
			2.384173955,0.01465793,2.189261314,0.013195162,1.815516495,0.014772793,0.773392698,1.412183348,1.356452541,0.66379353,0.635807323,1.140935442,0.923095969,4.329821695]

	X_new = normalize_data(X_new, X_mean, X_sd)

	for i in range(10):
		loaded_model = joblib.load('pickles/model' + str(i) + '.pkl')
		if i == 0:
			new_predictions = loaded_model.predict(X_new)
			for j in range(len(new_predictions)):
				if (j % 2 == 1):
					if (new_predictions[j-1] > new_predictions[j]):
						win[j-1] = win[j-1] + 1
					else:
						win[j] = win[j] + 1
		else:
			predict = loaded_model.predict(X_new)
			new_predictions = new_predictions + predict
			for j in range(len(predict)):
				if (j % 2 == 1):
					if (predict[j-1] > predict[j]):
						win[j-1] = win[j-1] + 1
					else:
						win[j] = win[j] + 1

	new_predictions = new_predictions / 10

	result = [new_predictions[0], new_predictions[1]]

	return result
