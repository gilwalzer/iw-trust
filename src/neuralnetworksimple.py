# neuralnetwork.py
# Gil Walzer

import pybrain
from pybrain.structure          import RecurrentNetwork, LinearLayer, SigmoidLayer, FullConnection
from pybrain.structure.modules   import LSTMLayer, SoftmaxLayer
from pybrain.datasets           import ClassificationDataSet
from pybrain.supervised         import BackpropTrainer
from pybrain.tools.shortcuts     import buildNetwork

import random, debug,sys, rigorous_analysis, trust
from rigorous_analysis import Analysis

class MyNN:
    def __init__(self, inputdim, proportion):
        self.nb_classes = 2 # hard coded, change later
        self.inputdim = inputdim
        
        self.scale = {}
        self.attrs = []
        self.scaled = False

        self.proportion = proportion
        self.DS, self.trndata, self.tstdata = self.create_dataset()  #inputdim)   
        self.nn = self.create()
    
    def set_attrs(self, attrs):
        self.attrs = list(attrs)
        if len(attrs) is not self.inputdim:
            print "You gave wrong number of attributes"

    def create_dataset(self):

        DS = ClassificationDataSet(self.inputdim, nb_classes=self.nb_classes,
            class_labels=["Trustworthy", "Untrustworthy"])

        trndata = ClassificationDataSet(self.inputdim, nb_classes=self.nb_classes,
            class_labels=["Trustworthy", "Untrustworthy"])

        tstdata = ClassificationDataSet(self.inputdim, nb_classes=self.nb_classes,
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

        attrs = self.attrs
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

    """ evaluate method argument is a method from the trust class which returns a value for 
    trustworthy and takes an analysis. It is up to the caller what it does, as long as it is 
    implemented in trust.py. """
    def add_sample_to_dataset(self, analysis, evaluate_method):

        params_dict, params_tuple = analysis.flatten()
        params = self.scale_parameters(params_dict)
        
        trustworthy = evaluate_method(analysis)
        input_v = self.make_input_vector_from_scaled(params)
        
        # input_v = analysis.make_input_vector(self.attrs)
        if input_v[0] is '' or input_v[0] is u'':
            input_v = (100.0, input_v[1], input_v[2], input_v[3])

        #print input_v
        self.DS.addSample(input_v, (trustworthy))
        i = random.random()
        if i > self.proportion:
            self.tstdata.addSample(input_v, (trustworthy))
        else:
            self.trndata.addSample(input_v, (trustworthy))

    def convert(self):
        self.tstdata._convertToOneOfMany(bounds=(0, self.nb_classes - 1))
        self.trndata._convertToOneOfMany(bounds=(0, self.nb_classes - 1))
        self.DS._convertToOneOfMany(bounds=(0, self.nb_classes - 1))

    def create(self):

        print "Creating: ", self.inputdim, self.nb_classes

        hidden_neurons = 5
        # construct LSTM network - note the missing output bias
        nn = buildNetwork( self.inputdim, hidden_neurons, self.nb_classes, hiddenclass=LSTMLayer, outclass=SoftmaxLayer, outputbias=False, recurrent=True)
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
        #print self.nn.outdim, " nn | ", self.trndata.outdim, " trndata "
        trainer = BackpropTrainer(self.nn, self.trndata, learningrate = 0.0005, momentum = 0.99)
        b1, b2 = trainer.trainUntilConvergence(verbose=True,
                              trainingData=self.trndata,
                              validationData=self.tstdata,
                              maxEpochs=10)
        #print b1, b2
        #print "new parameters are: "
        #self.print_connections()

        return b1, b2

    def make_input_vector_from_scaled(self, params):

        attrs = self.attrs
        scaled_input_vector = []
        for attr in attrs: 
            scaled_input_vector.append(params[attr])

        return tuple(scaled_input_vector)

    def activate_on_test(self, analyses, *count):
        act_array = []

        if count > len(analyses):
            count = len(analyses) - 1

        for analysis in analyses:
            inp = analysis.make_input_vector(self.attrs)    
            act = self.activate(inp)

            act_array.append((act, analysis))

        return act_array

    def activate(self, input_v):
        return self.nn.activate(input_v)

def main():
    analyses = debug.read_analyses_json("GwernJSONAnalyses")
    sys.stderr.write("\nGot " + str(len(analyses)) + " analyses.\n")

    sys.stderr.write("\nLoaded analysis files.\n")

    nn = MyNN(4, .75)
    #rnn.rnn.reset()
    
    attrs = ["rank", "fans", "transactions", "feedback"]
    nn.set_attrs(attrs)

    """["word_count", "sentence_count", "np_count", "avg_sentence_length", 
        "modal_count", "con_d", "group_ref", "pcom", "rcom"])
    """
    nn.set_scale(analyses)

    evaluate_method = trust.evaluate_trust_stupid
    for analysis in analyses[:-1]:
        nn.add_sample_to_dataset(analysis, evaluate_method)

    last = analyses[-1]
    sys.stderr.write("\nAdded analyses to dataset.\n")

    nn.convert()

    sys.stderr.write("\nBeginning training.\n")
    nn.train()
    sys.stderr.write("\nFinished.\n")

    aa = nn.activate_on_test(analyses[-20:-1], 20)
    for each in aa:
        print "activated an analysis. There were ", each[1].transactions, " transactions in ", each[1].months, "months, and there is a ", str(float(each[0][1])*100), "% chance that it is trustworthy.\n" ,# each[0], each[1].__dict__, "\n", #debug.print_analyses([last])

if __name__ == "__main__":
    main()