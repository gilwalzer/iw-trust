#test_all_attrs.py
from neuralnetworkhard import MyNN
import trust, debug, count_survey, autotest

import itertools, pdb, time, sys, Queue, thread, threading

def initialize(analyses):

	# seen_threshold: how many respondents have to have seen this datapoint for it to be useful?
	seen_threshold = 5

	# class_thresholds: what are the bars set for calling a data point trustworthy?
	# 0 to .9: untrustworthy
	# .9 to 2: trustworthy 
	#class_thresholds = [1]

	# or:
	# 0 to .6: untrustworthy
	# .6 to 1.2: somewhat trustworthy
	# 1.2 to 2: trustworthy
	class_thresholds = [.6, 1.2]

	survey_data = count_survey.get_survey_data(seen_threshold, class_thresholds)

	fnames = count_survey.get_filenames()
	#pdb.set_trace()
	#print fnames, survey_data
	# Make NN first attrs, on train 
	evaluate_method = trust.get_from_survey_data

	initial_attrs = ["rank", "feedback", "transactions", "fans"]
	err_train, err_test, nn = build_train_nn(analyses, initial_attrs, evaluate_method, survey_data=survey_data)
	#print nn

	return nn, fnames , survey_data

def build_train_nn(analyses, attrs, evaluate_method, **keyword_args):
	inputdim = len(attrs)
	nb_classes = 3

	#nn = MyNN(inputdim, nb_classes, .75)   
	nn = MyNN(inputdim, nb_classes, .75)   
	
	nn.set_attrs(attrs)

	nn.set_scale(analyses[:50])

	if "survey_data" in keyword_args:
		survey_data = keyword_args["survey_data"]
	else:
		survey_data = None

	if "control_nn" in keyword_args:
		control_nn = keyword_args["control_nn"]
	else:
		control_nn = None

	for analysis in analyses[:100]:
	    #print analysis.vendor_id, survey_data
	    
	    nn.add_sample_to_dataset(analysis, evaluate_method, survey_data=survey_data, control_nn=control_nn)

	nn.convert()
	error_train, error_test = nn.train()

	#print error_test, error_train
	return error_train, error_test, nn

def get_testing_attributes():

	all_attributes = ["feedback", "months", "rank", "fans", "transactions", "word_count", "sentence_count", "np_count", "verb_count",
	            "avg_num_of_clauses", "avg_sentence_length", "avg_word_length", "avg_length_np", "pausality",
	            "uncertainty_count", "other_ref", "modal_count", "lex_d", "con_d", "self_ref", "group_ref", "e",
	            "ppos", "pneg", "pneu", "pcom", "rpos", "rneg", "rneu", "rcom"]
	testing_attributes = ["word_count", "sentence_count", "np_count", "verb_count", "avg_num_of_clauses", 
				"avg_sentence_length", "pausality",
	            "uncertainty_count", "other_ref", "modal_count", "lex_d", "con_d", "self_ref", "group_ref",
	            "pcom", "rcom"]

	t_a = ["word_count", "modal_count", "other_ref", "lex_d", "con_d", "group_ref", "avg_sentence_length", "sentence_count"]
	return t_a

""" determine the mean squared error between control neural network and experimental """ 
""" experimental analyses must be the same those in the control activations """
def experiment(experimental_activations, control_activations, **kwargs):
	#print experimental_activations, control_activations, 
	#print "\n", len(experimental_activations), len(control_activations)
		
	assert(len(experimental_activations) == len(control_activations))

	if "iterations" not in kwargs:
		iterations = 3
	else:
		iterations = kwargs["iterations"]

	if "verbose" not in kwargs:
		verbose = False
	else:
		verbose = kwargs["verbose"]

	num_analyses = len(experimental_activations)
	
	mse_sum = 0	
	for i in range(num_analyses):
		exp_act_results = experimental_activations[i][0]
		#print exp_act_results
		#pdb.set_trace()
		con_act_results = control_activations[i][0]

		mses = 0

		for j in range(iterations):
			exp_class = -3
			con_class = -3

			for k in range(len(exp_act_results)):
				if exp_act_results[k] > .5:
					exp_class = k

			for k in range(len(con_act_results)):
				if con_act_results[k] > .5:
					con_class = k

			if verbose:
				print max(exp_act_results), max(con_act_results)
				print exp_class, con_class
			
			# if both analyses are identified identically, or neither is identified:
			if con_class is exp_class:
				mse = 0
			
			else:
				mse = 1
			"""
			elif (con_class - exp_class)*(con_class - exp_class) is 1:
				mse = 1
			elif (con_class - exp_class)*(con_class - exp_class) is 4: 
				mse = 4

			# if one the classes could not be successfully identified 
			else:
				mse = 9
			"""
			mses += mse

		mses = mses / iterations
		mse_sum += mses

	return mse_sum

def main():
	start = time.time()


	""" get list of all analyses """
	train_test_analyses, experimental_analyses = autotest.get_analyses(count_survey.get_filenames())

	mse_sum = 0
	mse_low_sum = 0
	mse_low_count = 0
	iters = 500
	for i in range(iters):
		control_nn, fnames, survey_data = autotest.initialize(train_test_analyses)
		control_activations = control_nn.activate_on_test(experimental_analyses)

		testing_attributes = get_testing_attributes()
		#train_test_analyses, experimental_analyses = autotest.get_analyses(count_survey.get_filenames())
		err_test, err_train, experimental_nn = build_train_nn(train_test_analyses, testing_attributes, trust.get_from_control_nn, survey_data=survey_data, control_nn=control_nn)
		
		a = experimental_nn.activate_on_test(experimental_analyses)
		#print autotest.print_activations(a)

		mse = autotest.experiment(control_activations, a, verbose=False)
		if mse < 300:
			mse_low_sum += mse
			mse_low_count += 1
			print mse
			print autotest.print_activations(a[:5])
		mse_sum += mse
	print mse_sum, mse_sum * 1.0/iters
	print mse_low_sum, mse_low_sum * 1.0/mse_low_count
main()