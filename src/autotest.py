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
import trust, debug, count_survey
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
	
""" create all possible combinations of attributes on which to test neural network """ 
def generate_all_experimental_args():
	all_attributes = ["feedback", "months", "rank", "fans", "transactions", "word_count", "sentence_count", "np_count", "verb_count",
	            "avg_num_of_clauses", "avg_sentence_length", "avg_word_length", "avg_length_np", "pausality",
	            "uncertainty_count", "other_ref", "modal_count", "lex_d", "con_d", "self_ref", "group_ref", "e",
	            "ppos", "pneg", "pneu", "pcom", "rpos", "rneg", "rneu", "rcom"]
	testing_attributes = ["word_count", "sentence_count", "np_count", "verb_count", "avg_num_of_clauses", 
				"avg_sentence_length", "pausality",
	            "uncertainty_count", "other_ref", "modal_count", "lex_d", "con_d", "self_ref", "group_ref",
	            "pcom", "rcom"]

	experimental_args = []
	min_iter = 5
	max_iter = 5
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

def evaluate_on_exps(name, trial_exp_attrs, otherdata):
	
	(control_activations, control_nn, train_test_analyses, experimental_analyses, survey_data, start) = otherdata

	keep_experiments = []#Queue.PriorityQueue()
	backup_keep_experiments = []
	i = 1
	j = 1
	#temp_experiments = Queue.PriorityQueue()
		
	avg_mse_50_experiments = 50

	total_experiments = len(trial_exp_attrs)

	for exp in trial_exp_attrs:

		#current1 = time.time()
		#sys.stderr.write("About to test built train.\n")

		err_test, err_train, experimental_nn = build_train_nn(train_test_analyses, exp, trust.get_from_control_nn, survey_data=survey_data, control_nn=control_nn)
		#pdb.set_trace()
		#current2 = time.time()
		#sys.stderr.write("Just finished, that took " + str(current2-current1) +" .\n")
	
		
		#current1 = time.time()
		#sys.stderr.write("About to test experimental_activations.\n")
	
		trial_experimental_activations = experimental_nn.activate_on_test(experimental_analyses[0:50])
		#current2 = time.time()
		#sys.stderr.write("Just finished, that took " + str(current2-current1) +" .\n")
		
		# test the first 50 activations. If it is below the current mse sum for 50 activations, average it with the previous
		# and then continue to test the remaining activations.
		#urrent1 = time.time()
		#sys.stderr.write("About to test mse50.\n")
		mse_50 = experiment(trial_experimental_activations, control_activations[0:50], iterations=1) 
		#current2 = time.time()
		#sys.stderr.write("Just finished, that took " + str(current2-current1) +" .\n")

		#sys.stderr.write("Measured mse of " + str(mse_50) + " compared to avg mse of " +  str(avg_mse_50_experiments) + "\n")		
		if mse_50 < avg_mse_50_experiments:

			sys.stderr.write("Thread " + name + ": " + str(exp) + " " + str(mse_50)+ "\n")
			avg_mse_50_experiments = (mse_50 + 0.0+ (i-1)*avg_mse_50_experiments) / i 

			experimental_activations = experimental_nn.activate_on_test(experimental_analyses)

			# print experimental_activations, control_activations, "\n", len(experimental_activations), len(control_activations)
			#current1 = time.time()
			#sys.stderr.write("About to test mse 1k.\n")
		
			mse = experiment(experimental_activations, control_activations, iterations=1)
			if mse < 400: # 6000:
				sys.stderr.write("Thread " + name + ": " + str(exp) + " " + str(mse)+ "\n")
				backup_keep_experiments.append((mse, exp, experimental_nn))
				if mse < 300: #3000:
					#print "\n\n\n\n\n", "found activation that had a mse of less than 1000!\n"
					tups = print_activations(experimental_activations)
					debug.write_each_attr_results("GwernAttrResults", exp, mse, tups)
					keep_experiments.append((mse, exp))
			#current2 = time.time()
			#sys.stderr.write("Just finished, that took " + str(current2-current1) +" .\n")

			# batch them 500 at a time
			#if (i % 3) is 0:
				#sys.stderr.write("Gone through " + str(i) + " out of total_experiments.\n")
			
		#temp_experiments.put((mse, exp, experimental_nn))
				
			if (i % 20) is 0:
				#temp_experiments.put((mse, exp, experimental_nn))
				current = time.time()
				sys.stderr.write("Thread " + name + ": " + str(current-start) + " seconds have elapsed since beginning of program.")
				sys.stderr.write("Thread " + name + ": So far, done full testing on " + str(i) + " possible combinations of attributes out of " + str(total_experiments) +  ".\n")
				"""
				for m in range(0, 5):
					if not temp_experiments.empty():
						each = temp_experiments.get()
						keep_experiments.put(each)
					else:
						break
				temp_experiments = Queue.PriorityQueue()
				"""
			i+=1
		#else:			
		if (j % 500) is 0:
			current = time.time()
			sys.stderr.write("Thread " + name + ": " + str(current-start) + " seconds have elapsed since beginning of program.")
			sys.stderr.write("Thread " + name + ": Rejected " + str(j - i) + " out of " + str(j) +  ".\n")

			debug.write_intermediate_results("GwernIntermediateResults", j,  name, keep_experiments)

		j+=1

	sorted_keep = sorted(keep_experiments)
	debug.write_final_results("GwernFinalResults", name, sorted_keep)
	
	sorted_backup_keep = sorted(backup_keep_experiments)
	debug.write_final_results("GwernFinalResults", name, sorted_backup_keep)
	sys.stderr.write("Thread " + name + ": Printed all experiments.\n")

def main():

	start = time.time()

	""" get list of all analyses """
	train_test_analyses, experimental_analyses = get_analyses(count_survey.get_filenames())

	control_nn, fnames, survey_data = initialize(train_test_analyses)
	control_activations = control_nn.activate_on_test(experimental_analyses)
	
	#print print_activations(control_activations)
	experimental_attrs = generate_all_experimental_args()

	#print all_attrs
	#print len(all_attrs)
	total_experiments = len(experimental_attrs)

	trial_exp_attrs = experimental_attrs#[-100:-1]
	#print experimental_attrs[-4000:-3995]
		
	""" open up a new thread for each slice of the experimental attrs """
	
	#"""
	for i in range(0, ( (total_experiments-1)/1000) + 1):
		name = "thread_" + str(i)

		sys.stderr.write("Starting thread " + name + "\n")
		thread.start_new_thread(evaluate_on_exps, (name, trial_exp_attrs[i*1000:min((i+1)*1000, total_experiments)],
		 (control_activations, control_nn, train_test_analyses, experimental_analyses, survey_data, start)))
	#"""
	evaluate_on_exps("Thread 5", trial_exp_attrs, (control_activations, control_nn, train_test_analyses, experimental_analyses, survey_data, start))

if __name__ == "__main__":
	main()
	sys.stderr.write("Finished program.\n")