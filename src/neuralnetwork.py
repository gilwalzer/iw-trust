# neuralnetwork.py
# Gil Walzer

import pybrain
from pybrain.structure import RecurrentNetwork
from rigorous_analysis import get_analysis

def create_dataset(dim)
    inputdim = dim
    DS = ClassificationDataSet(inputdim, nb_classes=2, class_labels=['Trustworthy', 'Untrustworthy'])
    
    data = get_analysis()
    # @TODO Use the data
    
    return DS
   
def split_dataset(DS, proportion):
    trndata, tstdata = DS.splitWithProportion(proportion)
    return trndata, tstdata
    
def createRNN():
    n = RecurrentNetwork()
    
    n.addInputModule(LinearLayer(2, name='in'))
    n.addModule(SigmoidLayer(3, name='hidden'))
    n.addOutputModule(LinearLayer(1, name="out"))
    n.addConnection(FullConnection(n['in'], n['hidden'], name='c1'))
    n.addConnection(FullConnection(n['hidden', n['out'], name='c2'))
    n.addRecurrentConnection(FullConnection(n['hidden'], n['hidden'], name='c3'))
    
def trainRNN():
    # copy and paste from the github repository
    
rnn = createRNN()
DS = create_dataset(5)

proportion = .75 # train data : total data
trndata, tstdata = split_dataset(proportion)