# main.py 
# Gil Walzer

import parse_vendors, debug, sys
from rigorous_analysis import Analyzer, Analysis
from neuralnetwork import MyRNN

analyses = None
vendors = None
if len(sys.argv) is 1 or len(sys.argv) > 4:
	sys.stderr.write("\ncommands:\tpython main.py [sample (optional count)] \n\t\tpython main.py [json (v or a)]")
	sys.exit(1)

elif len(sys.argv) is 2:
	if sys.argv[1] == "sample":
		# default sample count is 10
		vendors = debug.parse_sample()		
	else:
		vendors = debug.parse_all()

	debug.write_vendors_json(vendors, "GwernSampleJSON")

	analyzer = Analyzer()
	analyses = []
	for each in vendors:
		analysis = analyzer.analyze(each)
		analyses.append(analysis)

	debug.write_analyses_json(analyses, "GwernSampleJSONAnalyses")

elif len(sys.argv) is 3:
	if sys.argv[1] == "sample":
		sample_count = int(sys.argv[2]) 
		vendors = debug.parse_sample(sample_count)

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

			debug.write_analyses_json(analyses, "GwernSampleJSONAnalyses")

		elif sys.argv[2] == "a":
			sys.stderr.write("\nReading analyses.\n")
			analyses = debug.read_analyses_json("GwernSampleJSONAnalyses")

rnn = MyRNN(27)
for analysis in analyses:
	rnn.add_sample_to_dataset(analysis)