#trust.py

import count_survey

""" Each method in this class takes in an analysis and determines if it is trustworthy or not."""

def evaluate_trust_stupid(analysis, nb_classes):
	months = float(analysis.months)
		
	if months < 1:
	    months = 1

	t = float(analysis.transactions)
	tpm = t / months

	trustworthy = 0
	#print type(analysis.transactions), analysis.transactions
	if nb_classes is 2:

		if (tpm > 20): #or fans > 100):
		    trustworthy = 1
	
	elif nb_classes is 3:
		if (tpm > 30):
			trustworthy = 2
		elif tpm > 15:
			trustworthy = 1
	#print trustworthy
	#trustworthy = random.randint(0, 1)

	return trustworthy

def get_from_survey_data(analysis, **kwargs):

	if "survey_data" in kwargs:
		survey_data = kwargs["survey_data"]
	else:
		survey_data = None

	#print survey_data
	for each in survey_data:
		if analysis.vendor_id in each:
			return each[analysis.vendor_id]["trust"] 
	#	return survey_data[analysis.id]["trust_class"]
	return -1

def get_from_control_nn(analysis, **kwargs):

	if "control_nn" in kwargs:
		control_nn = kwargs["control_nn"]
	
	if "nb_classes" in kwargs:
		nb_classes = kwargs["nb_classes"]
		
	params_dict, params_tuple = analysis.flatten()
	params = control_nn.scale_parameters(params_dict)

	input_v = control_nn.make_input_vector_from_scaled(params)

	activation_result = control_nn.activate(input_v)

	anal_class = 0
	for k in range(len(activation_result)):
		if activation_result[k] > .6:
			anal_class = k

	return anal_class

        #print input_v
#def get_from_data(analysis):
#evaluate_trust_on_data(None)#