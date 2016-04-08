# neuralnetwork.py
# Gil Walzer

import pybrain
from pybrain.structure          import RecurrentNetwork, LinearLayer, SigmoidLayer, FullConnection
from pybrain.structure.modules   import LSTMLayer, SoftmaxLayer
from pybrain.datasets           import ClassificationDataSet
from pybrain.supervised         import BackpropTrainer
from pybrain.tools.shortcuts     import buildNetwork

import random
#from rigorous_analysis import get_analysis

class MyNN:
    def __init__(self, inputdim, proportion):
        self.nb_classes = 2 # hard coded, change later
        self.inputdim = inputdim
        self.proportion = proportion
        self.DS, self.trndata, self.tstdata = self.create_dataset()  #inputdim)   
        self.nn = self.create()
    
    def create_dataset(self):

        DS = ClassificationDataSet(self.inputdim, nb_classes=2,
            class_labels=["Trustworthy", "Untrustworthy"])

        trndata = ClassificationDataSet(self.inputdim, nb_classes=2,
            class_labels=["Trustworthy", "Untrustworthy"])

        tstdata = ClassificationDataSet(self.inputdim, nb_classes=2,
            class_labels=["Trustworthy", "Untrustworthy"])

        #'Trustworthy 4', 'A bit tw 3', 'sm tw 2', 'a bit utw 1', 'Untrustworthy 0'])
        
        #DS._convertToOneOfMany(bounds=(0, 1))
        
        return DS, trndata, tstdata
        
    def add_sample_to_dataset(self, analysis):

        feedback = 0
        months = 1

        try:
            months = int(analysis.months)
            feedback = float(analysis.feedback)

        except ValueError:
            pass

        pc = analysis.pos_counts

        q = analysis.quantity               # 4

        word_count = q[0]
        np_count = q[1]
        sentence_count = q[2]
        verb_count = pc[0]

        c = analysis.complexity             # 5
        avg_num_of_clauses = c[0]
        avg_sentence_length = c[1]
        avg_word_length = c[2]
        avg_length_np = c[3]
        pausality = c[4]

        u = analysis.uncertainty            # 3
        uncertainty_count = u[0]
        other_ref = u[1]
        modal_count = pc[4]

        d = analysis.diversity              # 2
        lex_d = d[0]
        con_d = d[1]

        n = analysis.nonimmediacy           # 2

        self_ref = n[0]*1.0 / word_count
        group_ref = n[1]*1.0 / word_count

        e = analysis.emotiveness            # 1 

        ps = analysis.profile_sentiments    # 5
        ppos = ps["pos"]
        pneg = ps["neg"]
        pneu = ps["neu"]
        pcom = ps["compound"]

        rs, rpos, rneg, rneu, rcom = 0,0,0,0,0
        rs_both = analysis.review_sentiments     # 4
        if rs_both is not None:
            avg_rating = rs_both[0]
            rs = rs_both[1]
            rpos = rs["pos"]
            rneg = rs["neg"]
            rneu = rs["neu"]
            rcom = rs["compound"]
                                                # 23 = total 

        # for now, they are trustworthy if they have over 100 transactions
        transactions = int(analysis.transactions)
        fans = int(analysis.fans)
        
        tpm = transactions * 1.0 / months
        trustworthy = 0
        if (transactions > 100): #or fans > 100):
            trustworthy = 1
           
            """ (tpm > 50 or 
        elif (tpm > 40 or transactions > 240 or fans > 80):
            trustworthy = 3
        elif (tpm > 30 or transactions > 180 or fans > 60):
            trustworthy = 2
        elif (tpm > 20 or transactions > 120 or fans > 40):
            trustworthy = 1
        else: 
            trustworthy = 0
        """
        input_v = (fans, 1, word_count, sentence_count, np_count, verb_count, 
            avg_num_of_clauses, avg_sentence_length, avg_word_length, avg_length_np, pausality,
            uncertainty_count, other_ref, modal_count, lex_d, con_d, self_ref, group_ref, e,
            ppos, pneg, pneu, pcom, rpos, rneg, rneu, rcom)

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

        print "Creating: ", self.trndata.indim, self.nb_classes

        # construct LSTM network - note the missing output bias
        nn = buildNetwork( self.trndata.indim, 5, self.nb_classes, hiddenclass=LSTMLayer, outclass=SoftmaxLayer, outputbias=False, recurrent=True)
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

    def activate(self, input_v):
        print self.nn.activate(input_v)
