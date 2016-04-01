# iw_debug.py
# Gil Walzer

import parse_vendors
import os, json, codecs

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
                
def print_vendor_usernames(vendors, classifier):
    
    filepath = "../../Deep Web Data/" + classifier + "/"
    try:
        os.stat(filepath)
    except:
        os.mkdir(filepath) 

    filepath_full = filepath + ".txt"
    for vendor in vendors:
        with codecs.open(filepath_full, "w+", "utf-8") as outFile:
            outFile.write(vendor.id + " " + vendor.username + "\n")
              
def parse_sample():
    sample = parse_vendors.parse_vendors(sample=10)
    return sample
    
def print_vendor(vendor):
    print vendor.profile, vendor.reviews
