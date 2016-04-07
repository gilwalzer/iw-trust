#test.py

from debug import *
from neuralnetwork import *
import random

def get_input_vector():
	a = random.random()*1.5 + .5
	b = random.random()*1.5

	decide = random.random()
	if decide > .5:
		#return ((a, 2), (2))
		return ((2, a), (1))
	else:
		#return ((b, 0), (0))
		return ((0, b), (0))

def print_connections(nn):
    for mod in nn.modules:
        for conn in nn.connections[mod]:
            print conn
            for cc in range(len(conn.params)):
                print conn.whichBuffers(cc), conn.params[cc]

	#c = 1 
def do_stuff():
	#	a = read_analyses_json("GwernJSONAnalyses")

	inputdim = 2
	q = get_input_vector()
	print q[0], q[1]

	DS = ClassificationDataSet(inputdim, nb_classes=2,
	    class_labels=["Good", "Bad"])

	trndata = ClassificationDataSet(inputdim, nb_classes=2,
	    class_labels=["Good", "Bad"])

	tstdata = ClassificationDataSet(inputdim, nb_classes=2,
	    class_labels=["Good", "Bad"])

	for i in range(200):
		input_v = get_input_vector()
		DS.addSample(input_v[0], input_v[1])
		i = random.random()
		if i > .75:
			tstdata.addSample(input_v[0], input_v[1])
		else: 
			trndata.addSample(input_v[0], input_v[1])

	print trndata, "---------------------", tstdata
	tstdata._convertToOneOfMany(bounds=(0, 1))
	trndata._convertToOneOfMany(bounds=(0, 1))
	DS._convertToOneOfMany(bounds=(0, 1))

	nn = buildNetwork(inputdim, 3, 2, hiddenclass=LSTMLayer, outclass=SoftmaxLayer, outputbias=False, recurrent=True)
	    
	trainer = BackpropTrainer(nn, trndata, learningrate = 0.0005, momentum = 0.99)
	b1, b2 = trainer.trainUntilConvergence(verbose=True,
	                      trainingData=trndata,
	                      validationData=tstdata,
	                      maxEpochs=10)
	print b1, b2, "\n", nn._params, "\n"
	print "0:", nn.activate([0,0])
	print "2:", nn.activate([2,2])
	print ".5:", nn.activate([.5,.5])
	print "1.5:", nn.activate([1.5,1.5])
	print "1:", nn.activate([1, 1])
do_stuff()