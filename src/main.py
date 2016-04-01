# main.py 
# Gil Walzer

import parse_vendors, debug, neuralnetwork
from rigorous_analysis import Analyzer

print "start"
analyzer = Analyzer()
vendors = debug.parse_sample()
#debug.write_vendors_files(vendors, "Gwern Sample Profiles")
analyses = []
for each in vendors[0:1]:
	analysis = analyzer.analyze(each)
	analyses.append(analysis)


