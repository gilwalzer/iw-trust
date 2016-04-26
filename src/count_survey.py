# count_survey.py

import debug, pdb

def get_filenames():
	fs = [[],[]]
	p = get_survey_results()
	#pdb.set_trace()
	for a in p[-2]:
		fs[0].append(a)
	for a in p[-1]:
		fs[1].append(a)
	return fs

def get_survey_results():
	data_survey_1, data_survey_2 = [], []
	with open("../../SurveyData/survey1.csv", "r") as inFile:
		lines = inFile.read().split("\r\n")
		data_survey_1 = []
		for line in lines:
			line = line.replace("point,", "point")
			line = line.replace("reference,", "reference")
			line = line.replace("early,", "early")
			line = line.replace("Actually,", "Actually")
			data_survey_1.append(line.split(','))


	with open("../../SurveyData/survey2.csv", "r") as inFile:
		lines = inFile.read().split("\r\n")
		data_survey_2 = []
		for line in lines:
			line = line.replace("point,", "point")
			line = line.replace("reference,", "reference")
			line = line.replace("early,", "early")
			line = line.replace("Actually,", "Actually")
			data_survey_2.append(line.split(","))

	# list filenames
	with open("../../SurveyData/surveydudes1", "r") as inFile:
		survey_unames_1 = inFile.read().split("\n")

	with open("../../SurveyData/surveydudes2", "r") as inFile:
		survey_unames_2 = inFile.read().split("\n")
		
	survey_1_filenames = debug.get_ids_for_usernames(survey_unames_1)
	survey_2_filenames = debug.get_ids_for_usernames(survey_unames_2)

	"""
	print survey_1_filenames, survey_2_filenames
	print "\n\n\n\n\n\n"
	print data_survey_1, data_survey_2
	"""

	tally_1, tally_2 = [0.0]*30, [0.0]*30
	seen_1, seen_2 = [0.0]*30, [0.0]*30
	ratio1, ratio2 = [None]*30, [None]*30

	for j in range(1, len(data_survey_1)):
		for i in range(1, 31):

			if "consider" in data_survey_1[j][i]:
				tally_1[i-1] += 2
			elif "sure" in data_survey_1[j][i]:
				tally_1[i-1] += 1
			elif "buying" in data_survey_1[j][i]:
				tally_1[i-1] += 0
			
			if len(data_survey_1[j][i]) > 0 or "Actually" in data_survey_1[j][i]:
				seen_1[i-1] += 1

	for i in range(1, 31):
		if seen_1[i-1] is not 0:
			ratio1[i-1] = tally_1[i-1]/seen_1[i-1]

	for j in range(1, len(data_survey_2)):
		for i in range(1, 31):

			if "consider" in data_survey_2[j][i]:
				tally_2[i-1] += 2
			elif "sure" in data_survey_2[j][i]:
				tally_2[i-1] += 1
			elif "buying" in data_survey_2[j][i]:
				tally_2[i-1] += 0
			
			if len(data_survey_2[j][i]) > 0 and not ("blurry" in data_survey_2[j][i] or "Actually" in data_survey_2[j][i]):
				seen_2[i-1] += 1

	for i in range(1, 31):		
		if seen_2[i-1] is not 0:
			ratio2[i-1] = tally_2[i-1]/seen_2[i-1]

	result = (seen_1, seen_2, ratio1, ratio2, survey_1_filenames, survey_2_filenames)
	#print result, " is result \n"
	#print tally_1, tally_2, "\n\n", seen_1, seen_2, "\n\n", ratio1, ratio2
	return result

def get_survey_data(seen_threshold, trust_class_thresholds):
	(seen_train, seen_test, ratio_train, ratio_test, survey_ids_train, survey_ids_test) = get_survey_results()

	seens = [seen_train, seen_test]
	ratios = [ratio_train, ratio_test] 
	ids = [survey_ids_train, survey_ids_test]

	data = [{},{}]

	# first train then test
	for k in range(0, 2):

		for i in range(0, len(seens[k])):
			seen = seens[k][i]
			ratio = ratios[k][i]

			if seen >= seen_threshold:
		
				trust_class = 0
				for j in range(len(trust_class_thresholds)):
					if ratio > trust_class_thresholds[j]:
						trust_class += 1


				data[k][ids[k][i]] = {"seen":seen, "ratio":ratio, "trust":trust_class} 
	
	return data

print get_survey_results()