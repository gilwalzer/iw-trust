#autotest.py

"""
Two goals in this module:

Two data sets
input= all vars
output= trustworthy or not

1. Automate, through terms variation and MSE minimization, control group:

NN1 with input vector composed with the following variables:
	in_vector_1 = rank, feedback, fans, transactions, tpm, avg_review

    with output 0 if results-sum-average = 0, 1 if results-sum-average = 1, 2 if results-sum-average = 2 where results-sum-average = aggregate
	Train on Tower training sample, Validate with non-Tower training sample

Now we have a control group to determine if a given analysis is trustworthy.
(Most likely higher rank, better reviews etc. will be more trustworthy)

2. Automate, through terms variation and MSE minimization, experimental groups:

NN2 with input vectors composed in the following way:
	For n from 1 to 14:
		For each possible combination of n attributes: in_vector_2 = those n attributes.

	    with output 0 if results-sum-average = 0, 1 if results-sum-average = 1, 2 if results-sum-average = 2 where results-sum-average = aggregate
		Train on Tower training sample, Validate with non-Tower training sample

		Find MSE between this result and corresponding result from 1)

3. Once this is done:
	Run experiment!
	Activate each profile on NN in 1), 2), find MSE


Design choice: Come up with some way of measuring trust according to 

"""

"""
Traindata 1:
"""
#from neuralnetworksimple import MyNN
from neuralnetworkhard import MyNN
import trust, debug, count_survey, test_with_threading
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

	if "verbose" in keyword_args:
		verbose = keyword_args["verbose"]
	else:
		verbose = False

	for analysis in analyses[:100]:
	    #print analysis.vendor_id, survey_data
	    
	    nn.add_sample_to_dataset(analysis, evaluate_method, survey_data=survey_data, control_nn=control_nn)

	nn.convert()
	error_train, error_test = nn.train(verbose=verbose)

	#print error_test, error_train
	return error_train, error_test, nn
	
""" create all possible combinations of attributes on which to test neural network """ 
def generate_all_experimental_args(**kwargs):
	all_attributes = ["feedback", "months", "rank", "fans", "transactions", "word_count", "sentence_count", "np_count", "verb_count",
	            "avg_num_of_clauses", "avg_sentence_length", "avg_word_length", "avg_length_np", "pausality",
	            "uncertainty_count", "other_ref", "modal_count", "lex_d", "con_d", "self_ref", "group_ref", "e",
	            "ppos", "pneg", "pneu", "pcom", "rpos", "rneg", "rneu", "rcom"]
	testing_attributes = ["word_count", "sentence_count", "np_count", "verb_count", "avg_num_of_clauses", 
				"avg_sentence_length", "pausality",
	            "uncertainty_count", "other_ref", "modal_count", "lex_d", "con_d", "self_ref", "group_ref",
	            "pcom", "rcom"]
	most_attributes = ["feedback", "rank", "fans", "transactions", "word_count", "sentence_count", "np_count", "verb_count", "avg_num_of_clauses", "avg_sentence_length", "avg_word_length", "avg_length_np", "pausality", "uncertainty_count", "other_ref", "modal_count", "lex_d", "con_d", "self_ref", "group_ref", "pcom", "rcom"]
        
	if "min" in kwargs:
		min_iter = kwargs["min"]
	else:
		min_iter = 5
	if "max" in kwargs:
		max_iter = kwargs["max"]
	else:
		max_iter = 5

	if "include_numerical" in kwargs:
		return [most_attributes, all_attributes]

	experimental_args = []
	for i in range(min_iter, max_iter + 1):
		combs = itertools.combinations(testing_attributes, i)
		for each in combs:
			experimental_args.append(each)

	return experimental_args
	# pass

""" returns both training and testing analyses and experiment analyses (two distinct sets)"""
def get_analyses(fnames):
	train_test_analyses = []
	all_fnames = []
	for fnamelist in fnames:
		for fname in fnamelist:
			all_fnames.append(fname)

	train_test_analyses = debug.read_analyses_by_ids("GwernJSONAnalyses", all_fnames)
	experimental_analyses = debug.read_analyses_except_ids("GwernJSONAnalyses", set(all_fnames))

	return (train_test_analyses, experimental_analyses)

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
				if exp_act_results[k] > .6:
					exp_class = k

			for k in range(len(con_act_results)):
				if con_act_results[k] > .6:
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

def print_activations(activations):
	tups = []
	for tup in activations:
		tups.append(list(tup[0]))

	return tups

def evaluate_on_exps(name, trial_exp_attrs, otherdata, **kwargs):
	
	(control_activations, control_nn, train_test_analyses, experimental_analyses, survey_data, start) = otherdata

	if "iterations" in kwargs:
		iterations = kwargs["iterations"]
	else:
		iterations = 0

	if "verbose" in kwargs:
		verbose = kwargs["verbose"]
	else:
		verbose = False

	if "optimize" in kwargs:
		optimize = kwargs["optimize"]
	else:
		optimize = False

	best_experiments = []
	all_experiments = []
	i = 1
	j = 1
	#temp_experiments = Queue.PriorityQueue()
		
	#vg_mse_50_experiments = 50

	total_experiments = len(trial_exp_attrs)

	for exp in trial_exp_attrs:

		#current1 = time.time()
		#sys.stderr.write("About to test built train.\n")
		mse_sum = 0.0
		iters = 0
		for iteration in range(iterations):
			err_test, err_train, experimental_nn = build_train_nn(train_test_analyses, exp, trust.get_from_control_nn, survey_data=survey_data, control_nn=control_nn, verbose=verbose)
	
			experimental_activations = experimental_nn.activate_on_test(experimental_analyses)

			# if optimize flag is set:
			# test the first 50 activations. If it is below the current mse sum for 50 activations, average it with the previous
			# and then continue to test the remaining activations.
			if optimize:
				mse_50 = experiment(experimental_activations[:50], control_activations[:50], iterations=1) 
			
				if mse_50 < .36*50:

					#sys.stderr.write("Thread " + name + ": " + str(exp) + " " + str(mse_50)+ "\n")
					#avg_mse_50_experiments = (mse_50 + 0.0+ (i-1)*avg_mse_50_experiments) / i 

					#experimental_activations = experimental_nn.activate_on_test(experimental_analyses)

					# print experimental_activations, control_activations, "\n", len(experimental_activations), len(control_activations)
					#current1 = time.time()
					#sys.stderr.write("About to test mse 1k.\n")
				
					mse = experiment(experimental_activations, control_activations, iterations=1)
					mse_sum += mse
					iters += 1

			# if optimize flag is not set, test all activations
			else: 
				mse = experiment(experimental_activations, control_activations, iterations=1)
				mse_sum += mse
				iters += 1

		mse_avg = 1000000
		if iters > 0:
			mse_avg = mse_sum / iters
			if (i % 50) is 0:
				sys.stderr.write("Thread " + name + ": " + str(exp) + " " + str(mse_avg)+ "\n")
			
		if mse_avg < 400: # 6000:
			sys.stderr.write("Thread " + name + ": " + str(exp) + " " + str(mse_avg)+ "\n")
			best_experiments.append((mse_avg, exp, experimental_nn))
		all_experiments.append((mse_avg, exp, experimental_nn))

		if (i % 20) is 0:
			#temp_experiments.put((mse, exp, experimental_nn))
			current = time.time()
			sys.stderr.write("Thread " + name + ": " + str(current-start) + " seconds have elapsed since beginning of program.")
			sys.stderr.write("Thread " + name + ": So far, done full testing on " + str(i) + " possible combinations of attributes out of " + str(total_experiments) +  ".\n")
		
				
		i+=1
			
	sorted_best = sorted(best_experiments)
	
	print "\n\n\n\n------------------BEST----------------\n\n\n", sorted_best
	debug.write_final_results("GwernFinalResults_sorted_", name, sorted_best)
	
	sorted_all = sorted(all_experiments)
	print "\n\n\n\n------------------ALL----------------\n\n\n", sorted_all

	#debug.write_final_results("GwernFinalResults", name, sorted_backup_keep)
	sys.stderr.write("Thread " + name + ": Printed all experiments.\n")

def main():

	start = time.time()

	""" get list of all analyses """
	train_test_analyses, experimental_analyses = get_analyses(count_survey.get_filenames())

	control_nn, fnames, survey_data = initialize(train_test_analyses)
	control_activations = control_nn.activate_on_test(experimental_analyses)
	
	#print print_activations(control_activations)

	""" arguments to this function: sizes of attribute lists """
	experimental_attrs = generate_all_experimental_args(min=14, max=16)
	all_attrs = generate_all_experimental_args(include_numerical=True)

	#print all_attrs
	#print len(all_attrs)
	#total_experiments = len(experimental_attrs)

	#trial_exp_attrs = experimental_attrs#[-100:-1]
	#print experimental_attrs[-4000:-3995]
	otherdata = (control_activations, control_nn, train_test_analyses, experimental_analyses, survey_data, start)

	threading = False

	if threading:
		""" open up a new thread for each slice of the experimental attrs """
		test_with_threading.test(name, experimental_attrs, otherdata)
	else:
		print "\nExperimenting with combinatorial experimental nets, 10 iterations, unoptimized.\n"
		evaluate_on_exps("Unthreaded", experimental_attrs, otherdata, iterations=10)

		print "\nExperimenting with combinatorial experimental nets, 10 iterations, optimized.\n"
		evaluate_on_exps("Unthreaded", experimental_attrs, otherdata, iterations=10, optimize=True)
		
		print "\nExperimenting with expanded nets, 10 iterations, unoptimized.\n"
		evaluate_on_exps("Unthreaded", all_attrs, otherdata, iterations=200, verbose=True)

		print "\nExperimenting with expanded nets, 10 iterations, optimized.\n"
		evaluate_on_exps("Unthreaded", all_attrs, otherdata, iterations=200, verbose=True, optimize=True11)

if __name__ == "__main__":
	main()
	sys.stderr.write("Finished program.\n")