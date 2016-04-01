# rigorous_analysis.py
# Rigorous Analysis!
# Gil Walzer

import nltk, re, tokenize

from spacycaller import SpacyCaller
from parse_vendors import Vendor
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment

class Analyzer:
    def __init__(self):
        self.spacy = SpacyCaller()
        
    def analyze(self, vendor):
        tokens = self.spacy.spacy_analyze_vendor(vendor)
        
        quantity = quantity_analysis(tokens)
        complexity = complexity_analysis(tokens)
        
        rsa = review_sentiment_analysis(vendor)
        
def pos_tag(text):
    tags = nltk.pos_tag(tokens)
    return tags
    
def get_content_words(tokens):
    content_POS_list = ["FW", "JJ", "JJR", "JJS", "NN", "MD", "NNP", "NNPS", "NNS", "RB", "RBR", "RP", "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "SYM"]
    
    content_words = []
    for token in tokens:
        pos = token.tag_
        if pos in content_POS_list:
            content_words.append(token)
            
    return content_words
    
# actually takes any iterable
def count_unique(tokens):
    s = set()
    for token in tokens:
        s.put(token)
        
    return len(s)
    
def review_sentiment_analysis(vendor):
    review_list = vendor.reviews
    rating_sum = 0.0
    num_ratings = 0.0
    
    if len(review_list) is 0:
        return None
    
    sent_sum = {"pos":0.0, "neg":0.0, "neu":0.0, "compound":0.0}
    for review in review_list:
        message = review[1]
        rating = review[0]

        vs = vaderSentiment(message)
        
        if not (vs["neu"] is 1.0 and vs["compound"] is 0.0):
            for key in vs.keys():
                sent_sum[key] += float(vs[key])
                
            rating_sum += float(rating)
            num_ratings += 1
        
    for key in sent_sum_keys():
        sent_sum[key] = sent_sum[key] / num_ratings
        
    return (rating_sum/num_ratings, sent_sum)    
    
def pos_counts(tokens):
    verb_count, noun_count, adj_count, adv_count, modal_count = 0
    for token in list(tokens):
        if "MD" in token.tag_:
            modal_count += 1
        elif "JJ" in token.tag_:
            adj_count += 1
        elif "RB" in token.tag_:
            adv_count += 1
        elif "NOUN" in token.pos_:
            noun_count += 1
            
        elif "VERB" in token.pos_:    
            verb_count += 1
            
    return (verb_count, noun_count, adj_count, adv_count, modal_count)

def quantity_analysis(tokens):
    word_count = len(tokens)
    
    nc = list(tokens.noun_chunks)
    noun_phrase_count = len(nc)
    
    sents = list(tokens.sents)
    sentence_count = len(sents)
    
    return (word_count, noun_phrase_count, sentence_count)
    
def complexity_analysis(tokens):
    (verb_count, noun_count, adj_count, adv_count, modal_count) = pos_counts(tokens)
    (word_count, noun_phrase_count, sentence_count) = quantity_analysis(tokens)
    
    clause_count = 0
    for token in list(tokens):
        if ("VERB" in token.pos_):
            if token is token.head:
                clause_count += 1
            else:
                children = list(token.children)
                for child in children:
                    if "IN" in child.tag_ or "WDT" in child.tag_ or "WP" in child.tag_:
                        clause_count += 1
                        
    avg_num_of_clauses = clause_count * 1.0 / sentence_count
    avg_sentence_length = word_count*1.0 / sentence_count
    character_count = 0
    for token in list(tokens):
        character_count += len(token)
    avg_word_length = character_count*1.0/word_count
    
    words_in_nc_count = 0.0
    nc = list(tokens.noun_chunks)
    for noun_chunk in nc:
        words_in_nc_count += len(noun_chunk)
        
    avg_length_np = words_in_nc_count / noun_phrase_count
    
    punct_count = 0.0
    for token in tokens:
        if "PUNCT" in token.pos_
            punct_count += 1
    
    pausality = punct_count / sentence_count
    
    complexity = (avg_num_of_clauses, avg_sentence_length, avg_word_length, avg_length_np, pausality)
    
    return complexity
    
def uncertainty_analysis(tokens):
    ["appear", "Appear",
    "seem", "Seem",
    "suggest", "Suggest",
    "indicat", "Indicat",
    "assum", "Assum",        
    "imply", "implie", "Imply", "Implie",
    "hope", "Hope", "hoping", "Hoping",
    "Think so", "think so"]
    
    txt = tokens.text
    uncertainty_count = 0
    for word in uncertain_words:
        uncertainty_count += txt.count(word)
        
    other_reference_words = 
       [" he ", "He ", " she ", "She ",
        " him.", " him,", " him ", "himself",
        " her.", " her,", " her ", "herself",
        "It ", " it ", " it.", " it ", " itself ",
        " they", "They", "Them", "them",
        ]                
    
    other_reference_count = 0
    for word in other_reference_words:
        other_reference_count += txt.count(word)
        
    return (uncertainty_count, other_reference_count)
    
    def nonimmediacy_analysis(tokens):
    
    self_ref = ["I ", " i ", " me.", " me!", " me,", " me ", "Me "]
    self_ref_count = 0
    for word in self_ref:
        self_ref_count += tokens.text.count(word)
        
    group_ref = ["We ", " we ", " us ", " us,", " us.", " Us ", " Us.", " us!", " Us!"]
    group_ref_count = 0
    for word in group_ref:
        group_ref_count += tokens.text.count(word)
    
    return (self_ref_count, group_ref_count)
    
def emotiveness_analysis(counts):
    (verb_count, noun_count, adj_count, adv_count, modal_count) = counts
    return (adj_count + adv_count*1.0) / (noun_count + verb_count)
    
def diversity_analysis(tokens):
    num_tokens = len(tokens)
    unique_tokens = count_unique(tokens)
    
    contents = get_content_words(tokens)
    unique_contents = count_unique(contents)
    

            