# main.py 
# Gil Walzer

import parse_vendors, debug, sys
from rigorous_analysis import Analyzer, Analysis
from neuralnetwork import MyNN

def handle_args(args):
	analyses = []
	if len(sys.argv) is 1 or len(sys.argv) > 4:
		sys.stderr.write("\ncommands:\tpython main.py [sample (optional count)] \n\t\tpython main.py [json (v or a)]")
		sys.exit(1)

	elif len(sys.argv) is 2:
		if sys.argv[1] == "sample":
			# default sample count is 10
			vendors = debug.parse_sample()		

			debug.write_vendors_json(vendors, "GwernSampleJSON")


			analyzer = Analyzer()
			analyses = []
			for each in vendors:
				analysis = analyzer.analyze(each)
				analyses.append(analysis)

			debug.write_analyses_json(analyses, "GwernSampleJSONAnalyses")

		else:
			# write the vendors that were parsed
			vendors = debug.parse_all()
			debug.write_vendors_json(vendors, "GwernJSON")

			vendors = debug.read_unanalyzed_vendors_json("GwernJSON")

			analyzer = Analyzer()
			analyses = []
			for each in vendors:
				analysis = analyzer.analyze(each)
				analyses.append(analysis)

			debug.write_analyses_json(analyses, "GwernJSONAnalyses")
			analyses = debug.read_analyses_json("GwernJSONAnalyses")

	elif len(sys.argv) is 3:
		if sys.argv[1] == "sample":
			sample_count = int(sys.argv[2]) 
			vendors = debug.parse_sample(sample_count)

			debug.write_vendors_json(vendors, "GwernSampleJSON")

			analyzer = Analyzer()
			analyses = []
			for each in vendors:
				analysis = analyzer.analyze(each)
				analyses.append(analysis)

			debug.write_analyses_json(analyses, "GwernSampleJSONAnalyses")

		elif sys.argv[1] == "json":
			sys.stderr.write("\nReading from json.")
				 
			if sys.argv[2] == "v":
				sys.stderr.write("\nReading vendors.\n")
				analyzer = Analyzer()
				vendors = debug.read_vendors_json("GwernSampleJSON")
				#debug.write_vendors_json(vendors, "GwernSampleJSON")

				analyses = []
				for each in vendors:
					analysis = analyzer.analyze(each)
					analyses.append(analysis)

				debug.write_analyses_json(analyses, "GwernJSONAnalyses")

			elif sys.argv[2] == "a":
				sys.stderr.write("\nReading analyses.\n")
				analyses = debug.read_analyses_json("GwernJSONAnalyses")

	return analyses

analyses = handle_args(sys.argv)
sys.stderr.write("\nGot " + str(len(analyses)) + " analyses.\n")

sys.stderr.write("\nLoaded analysis files.\n")

nn = MyNN(27, .75)
#rnn.rnn.reset()
for analysis in analyses:
	nn.add_sample_to_dataset(analysis)

sys.stderr.write("\nAdded analyses to dataset.\n")

nn.convert()
print nn.DS
print "\n\n\n"
print "Training data: ", nn.trndata
print "\n\n\n"
print "Testing data: ", nn.tstdata
print "\n\n\n"

print "original parameters are: \n",
nn.print_connections()

sys.stderr.write("\nBeginning training.\n")
nn.train()
sys.stderr.write("\nFinished.\n")

iv = (0,1000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
nn.activate(iv)