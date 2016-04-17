# iw_debug.py
# Gil Walzer

import parse_vendors, rigorous_analysis
import os, json, codecs

def write_analyses_json(analyses, classifier):
    filepath = "../../Deep Web Data/" + classifier + "/"
    try:
        os.stat(filepath)
    except:
        os.mkdir(filepath) 
    for analysis in analyses:
        filepath_full = filepath + analysis.vendor_id + ".json"
        with codecs.open(filepath_full, 'w+', errors="ignore") as outFile:
            outFile.write(json.dumps(analysis.__dict__).encode("UTF-8"))

def read_analyses_json(classifier):
    filepath = "../../Deep Web Data/" + classifier + "/"
    filenames = os.listdir(filepath)
    
    analyses = []
    
    for filename in filenames:
        
        with codecs.open(filepath + filename, "r", "utf-8", errors="ignore") as analysis_file:
            analysis_data = analysis_file.read()
            analysis = rigorous_analysis.create_Analysis_from_json(analysis_data)
            #print analysis.__dict__
            analyses.append(analysis)

    return analyses

def read_analyses_by_ids(classifier, ids):
    filepath = "../../Deep Web Data/" + classifier + "/"
    analyses = []

    for fid in ids:
        with codecs.open(filepath + fid + ".json", "r", "utf-8", errors="ignore") as analysis_file:
            analysis_data = analysis_file.read()
            analysis = rigorous_analysis.create_Analysis_from_json(analysis_data)
            
            analyses.append(analysis)

    return analyses

def read_analyses_except_ids(classifier, no_ids):
    filepath = "../../Deep Web Data/" + classifier + "/"
    filenames = os.listdir(filepath)
    
    analyses = []
    
    for filename in filenames:
        fid = filename.split(".json")[0]
        if fid not in no_ids:   
            with codecs.open(filepath + filename, "r", "utf-8", errors="ignore") as analysis_file:
                analysis_data = analysis_file.read()
                analysis = rigorous_analysis.create_Analysis_from_json(analysis_data)
                #print analysis.__dict__
                analyses.append(analysis)

    return analyses


def write_vendors_json(vendors, classifier):
    filepath = "../../Deep Web Data/" + classifier + "/"
    try:
        os.stat(filepath)
    except:
        os.mkdir(filepath) 
    for vendor in vendors:
        filepath_full = filepath + vendor.id + ".json"
        with codecs.open(filepath_full, 'w+', errors="ignore") as outFile:
            outFile.write(json.dumps(vendor.__dict__).encode("UTF-8"))

def read_vendors_json(classifier):
    filepath = "../../Deep Web Data/" + classifier + "/"
    filenames = os.listdir(filepath)

    vendors = []
    
    for filename in filenames:
        
        with codecs.open(filepath + filename, "r", "utf-8", errors="ignore") as vendor_file:
            vendor_data = vendor_file.read()
            vendor = parse_vendors.create_Vendor_from_json(vendor_data)
            vendors.append(vendor)

    return vendors

def read_unanalyzed_vendors_json(classifier):

    filepath = "../../Deep Web Data/" + classifier
    filenames = os.listdir(filepath + "/")
    
    analyzed_already = os.listdir(filepath + "Analyses")
    aa_fnames = set(analyzed_already)

    vendors = []
    
    for filename in filenames:
        if filename not in aa_fnames:
            with codecs.open(filepath + filename, "r", "utf-8", errors="ignore") as vendor_file:
                vendor_data = vendor_file.read()
                vendor = parse_vendors.create_Vendor_from_json(vendor_data)
                vendors.append(vendor)

    return vendors

def write_vendors_files(vendors, classifier):

    filepath = "../../Deep Web Data/" + classifier + "/"
    try:
        os.stat(filepath)
    except:
        os.mkdir(filepath) 

    for vendor in vendors:
        filepath_full = filepath + vendor.id + ".txt"
        with codecs.open(filepath_full, 'w+') as outFile:
            outFile.write(vendor.__str__().encode("UTF-8"))

def get_ids_for_usernames(unames):
    vendors = read_vendors_json("GwernJSON")
    all_v = {}
    for v in vendors:
        all_v[v.username] = v.id

    idents = []
    for uname in unames:
        if uname in all_v:
            idents.append(all_v[uname])
        else:
            idents.append(None)

    return idents

def print_vendor_usernames(vendors, directory, filename):
    
    filepath = "../../Deep Web Data/" + directory + "/"
    try:
        os.stat(filepath)
    except:
        os.mkdir(filepath) 

    filepath_full = filepath + filename + ".txt"
    for vendor in vendors:
        with codecs.open(filepath_full, "a", "utf-8") as outFile:
            outFile.write(vendor.id + " " + vendor.username + "\n")
              
def parse_sample(**keyword_parameters):
    if "sample" in keyword_parameters:
        sample_count = keyword_parameters["sample"]
    else:
        sample_count = 11
    sample = parse_vendors.parse_vendors(sample=sample_count)
    return sample

def parse_all():
    return parse_vendors.parse_vendors()

def print_vendor(vendor):
    print vendor.profile, vendor.reviews

def print_analyses(analyses):
    for analysis in analyses:
        print analysis.__dict__