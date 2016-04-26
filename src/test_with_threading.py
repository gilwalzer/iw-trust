# test_with_threading.py

import threading, sys

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

def test(name, trial_exp_attrs, (control_activations, control_nn, train_test_analyses, experimental_analyses, survey_data, start)):
	#"""
	for i in range(0, ( (total_experiments-1)/1000) + 1):
		name = "thread_" + str(i)

		sys.stderr.write("Starting thread " + name + "\n")
		thread.start_new_thread(evaluate_on_exps, (name, trial_exp_attrs[i*1000:min((i+1)*1000, total_experiments)],
		 (control_activations, control_nn, train_test_analyses, experimental_analyses, survey_data, start)))
	#"""
	evaluate_on_exps("Thread 5", trial_exp_attrs, (control_activations, control_nn, train_test_analyses, experimental_analyses, survey_data, start))
