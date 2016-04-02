# neuralnetwork.py
# Gil Walzer

import pybrain
from pybrain.structure import RecurrentNetwork, LinearLayer, SigmoidLayer, FullConnection
from pybrain.datasets import ClassificationDataSet
#from rigorous_analysis import get_analysis

class MyRNN:
    def __init__(self, inputdim):
        self.inputdim = inputdim
        self.rnn = self.createRNN()
        self.DS = self.create_dataset()  #inputdim)    
        self.trndata = None
        self.tstdata = None

    def create_dataset(self):

        DS = ClassificationDataSet(self.inputdim, nb_classes=2, class_labels=['Trustworthy', 'Untrustworthy'])
        return DS
        
    def add_sample_to_dataset(self, analysis):

        months = int(analysis.months)
        feedback = float(analysis.feedback)

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

        rs_both = analysis.review_sentiments     # 4
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
        
        trustworthy = 0
        if (transactions > 100 or fans > 50):
            trustworthy = 1

        self.DS.addSample((months, feedback, word_count, sentence_count, np_count, verb_count, 
            avg_num_of_clauses, avg_sentence_length, avg_word_length, avg_length_np, pausality,
            uncertainty_count, other_ref, modal_count, lex_d, con_d, self_ref, group_ref, e,
            ppos, pneg, pneu, pcom, rpos, rneg, rneu, rcom), (trustworthy))
        
    def split_dataset(self, proportion):
        
        self.trndata, self.tstdata = self.DS.splitWithProportion(proportion)
        #return trndata, tstdata
        
    def createRNN(self):
        n = RecurrentNetwork()
        
        n.addInputModule(LinearLayer(2, name='in'))
        n.addModule(SigmoidLayer(3, name='hidden'))
        n.addOutputModule(LinearLayer(1, name="out"))
        n.addConnection(FullConnection(n['in'], n['hidden'], name='c1'))
        n.addConnection(FullConnection(n['hidden'], n['out'], name='c2'))
        n.addRecurrentConnection(FullConnection(n['hidden'], n['hidden'], name='c3'))
        
        return n

    def trainRNN(self):
        trainer = RPropMinusTrainer( rnn, dataset=trndata, verbose=True )

        pass