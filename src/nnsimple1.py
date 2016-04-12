# neuralnetwork.py
# Gil Walzer

import pybrain
from pybrain.structure          import RecurrentNetwork, LinearLayer, SigmoidLayer, FullConnection
from pybrain.structure.modules   import LSTMLayer, SoftmaxLayer
from pybrain.datasets           import ClassificationDataSet
from pybrain.supervised         import BackpropTrainer
from pybrain.tools.shortcuts     import buildNetwork

import random, debug,sys, rigorous_analysis
from rigorous_analysis import Analysis

class MyNN:
    def __init__(self, inputdim, proportion):
        self.nb_classes = 1 # hard coded, change later
        # self.inputdim = inputdim
        self.inputdim = 10
        self.scale = {}
        self.scaled = False

        self.proportion = proportion
        self.DS, self.trndata, self.tstdata = self.create_dataset()  #inputdim)   
        self.nn = self.create()
    
    def create_dataset(self):

        DS = ClassificationDataSet(self.inputdim, nb_classes=1,
            class_labels=["Trustworthy", "Untrustworthy"])

        trndata = ClassificationDataSet(self.inputdim, nb_classes=1,
            class_labels=["Trustworthy", "Untrustworthy"])

        tstdata = ClassificationDataSet(self.inputdim, nb_classes=1,
            class_labels=["Trustworthy", "Untrustworthy"])

        #'Trustworthy 4', 'A bit tw 3', 'sm tw 2', 'a bit utw 1', 'Untrustworthy 0'])
        
        #DS._convertToOneOfMany(bounds=(0, 1))
        
        return DS, trndata, tstdata

    def set_scale(self, analyses):
    
        attrs = Analysis.flat_attributes       
        scale = {}
        for attr in attrs:
            scale[attr] = None

        for analysis in analyses:
            fdict, ftuple = analysis.flatten() 
            for attr in attrs:
                t = fdict[attr]
                if type(t) is str or type(t) is unicode: 
                    try:
                        t = float(t)
                    except ValueError:
                        if "rank" in attr:
                            t = 100.0
                        if "transactions" in attr:
                            t = 0
                        if "fans" in attr:
                            t = 0

                if t > scale[attr]:
                    scale[attr] = t

        self.scale = scale
        self.scaled = True

    def scale_parameters(self, params):

        attrs = Analysis.flat_attributes
        if not self.scaled:
            return params

        new_params = {}
        for attr in attrs:
            parm = params[attr]
            try:
                new_param = 1.0*parm/self.scale[attr]
            except TypeError:
                if type(parm) is unicode:
                    #print attr, ",", parm, type(parm)
                    try:
                        parm = float(parm)
                    except ValueError:
                        if "rank" in attr:
                            parm = 100.0 

            new_param = parm/self.scale[attr]
            new_params[attr] = new_param

        return new_params

    def add_sample_to_dataset(self, analysis):

        params_dict, params_tuple = analysis.flatten()
        params = self.scale_parameters(params_dict)
        
        months = params["months"]
        if months is 0:
            months = 1

        tpm = params["transactions"] * 1.0 / months
        trustworthy = 0
        if (tpm > 5): #or fans > 100):
            trustworthy = 1
        #trustworthy = random.randint(0, 1)

        input_v = (params["word_count"], params["sentence_count"], params["np_count"], params["avg_sentence_length"], 
            params["modal_count"], params["con_d"], params["group_ref"], params["e"], params["pcom"], params["rcom"])

        self.DS.addSample(input_v, (trustworthy))
        i = random.random()
        if i > self.proportion:
            self.tstdata.addSample(input_v, (trustworthy))
        else:
            self.trndata.addSample(input_v, (trustworthy))

    def convert(self):
        self.tstdata._convertToOneOfMany(bounds=(0, 1))
        self.trndata._convertToOneOfMany(bounds=(0, 1))
        self.DS._convertToOneOfMany(bounds=(0, 1))

    def create(self):

        print "Creating: ", self.inputdim, self.nb_classes

        # construct LSTM network - note the missing output bias
        nn = buildNetwork( self.inputdim, 5, self.nb_classes, hiddenclass=LSTMLayer, outclass=SoftmaxLayer, outputbias=False, recurrent=True)
        """
        n.addInputModule(LinearLayer(27, name='in'))
        n.addModule(SigmoidLayer(3, name='hidden'))
        n.addOutputModule(LinearLayer(1, name="out"))
        n.addConnection(FullConnection(n['in'], n['hidden'], name='c1'))
        n.addConnection(FullConnection(n['hidden'], n['out'], name='c2'))
        n.addRecurrentConnection(FullConnection(n['hidden'], n['hidden'], name='c3'))
        """
        return nn


    # adapted from stackOverflow
    def print_connections(self):
        for mod in self.nn.modules:
            for conn in self.nn.connections[mod]:
                print conn
                for cc in range(len(conn.params)):
                    print conn.whichBuffers(cc), conn.params[cc]

    def train(self):
        """t = BackpropTrainer(self.rnn, dataset=self.trndata, learningrate = 0.1, momentum = 0.0, verbose = True)
        for i in range(1000):
            t.trainEpochs(5)

        """
        print self.nn.outdim, " nn | ", self.trndata.outdim, " trndata "
        trainer = BackpropTrainer(self.nn, self.trndata, learningrate = 0.0005, momentum = 0.99)
        b1, b2 = trainer.trainUntilConvergence(verbose=True,
                              trainingData=self.trndata,
                              validationData=self.tstdata,
                              maxEpochs=10)
        print b1, b2
        print "new parameters are: "
        self.print_connections()

    def activate_on_test(self, count):
        if count > len(self.tstdata):
            count = len(self.tstdata - 1)

        for inp, target in self.tstdata:
            self.activate(inp)

    def activate(self, input_v):
        print self.nn.activate(input_v)

def main():
    analyses = debug.read_analyses_json("GwernJSONAnalyses")
    sys.stderr.write("\nGot " + str(len(analyses)) + " analyses.\n")

    sys.stderr.write("\nLoaded analysis files.\n")

    nn = MyNN(10, .75)
    #rnn.rnn.reset()
    nn.set_scale(analyses)
    for analysis in analyses[:-1]:
        nn.add_sample_to_dataset(analysis)

    last = analyses[-1]
    sys.stderr.write("\nAdded analyses to dataset.\n")

    #nn.convert()
    """print nn.DS
    print "\n\n\n"
    print "Training data: ", nn.trndata
    print "\n\n\n"
    print "Testing data: ", nn.tstdata
    print "\n\n\n"

    print "original parameters are: \n",
    nn.print_connections()
    """
    sys.stderr.write("\nBeginning training.\n")
    nn.train()
    sys.stderr.write("\nFinished.\n")

    nn.activate_on_test(100)
    print "activating: ", nn.activate(last), debug.print_analyses([last])

if __name__ == "__main__":
    main()