# parse_vendors.py
# Gil Walzer
import codecs, os, re, sqlite3
from HTMLParser import HTMLParser

class Vendor: 
    def __init__(self, username, vendor_id, months, rank, feedback, 
        transactions,fans, profile_scraped_string, reviews_scraped, reviews):
        self.username = username
        self.id = vendor_id
        self.months = months
        self.rank = rank
        self.feedback = feedback
        self.transactions = transactions
        self.fans = fans
        self.profile = profile_scraped_string
        self.reviews_string = reviews_scraped
        self.reviews = reviews
    
    def __str__(self):
       sb = self.id + " " + self.username + "\n" + self.feedback + " " + self.transactions + "\n\n" + self.profile + "\n\n" + self.reviews_string
       return unicode(sb)
       
# May be depreciated
def parse_vendors(**keyword_parameters):
    filepath = "../../Deep Web Data/"
    
    if "filepath" in keyword_parameters:
        filepath = filepath + keyword_parameters['filepath']
    else:
        filepath = filepath + "GwernVP"
       
    if "sample" in keyword_parameters:
        limit = keyword_parameters['sample']
        print limit
        
    filepath = filepath + "/"
    filenames = os.listdir(filepath)
    
    i = 0
    vendors = []
    nonascii_filenames = []
    
    for filename in filenames:
        if i > limit:
            break
        else:
            i += 1
        
        vendor_raw_html = ""
        with codecs.open(filepath + filename, "r", "utf-8") as vendor_file:
            vendor_raw_html = vendor_file.read()
       
        h = HTMLParser()
       
        profile_raw_info = re.split('<div class="h1">|</div><table class="zebra"><tr><th>category</th><th>title<th><th>price', vendor_raw_html)
        profile_raw_info_2 = profile_raw_info[1]

        profile_scraped = re.split("<[^<>]*>", profile_raw_info_2)

        review_raw_info = re.split('<table class="zebra"><tr><th>rating</th><th>review</th><th>freshness</th><th>item</th>', vendor_raw_html)
        reviews = ""
        if len(review_raw_info) > 1:
            review_raw_info_2 = review_raw_info[1]

            review_list = scrape_reviews(review_raw_info_2)
            reviews = review_list_to_string(review_list)
       
        (username, duration, rank, feedback, transactions, fans, profile) = scrape_profile(profile_scraped)

        profile = h.unescape(profile)

        vendor_id = filename.split('.')[0]
        vendor = Vendor(username, vendor_id, duration, rank, feedback, transactions, fans, profile, reviews, review_list)

        vendors.append(vendor)
          
    return vendors

def scrape_reviews(reviews_scraped):
    h = HTMLParser()
    reviews_1 = re.split("</tr><tr>", reviews_scraped)
    reviews_2 = []
    for each in reviews_1:
        each_2 = re.split("<[^>]*>", each)
        for each_3 in each_2:
            reviews_2.append(each_3)
            
    reviews_3 = []
    for each in reviews_2:
        if each is u"":
            pass
        elif "\t" in each:
            pass
        elif "\n" in each:
            pass
        else:
            reviews_3.append(each)
            
    t = 0
    
    review_table = []
    
    #Consolidate the reviews
    for each in reviews_3:
        if "community forums" in each or "wiki" in each or "|" in each or "support" in each:
            break
        if "&nbsp" in reviews_3[t+1]:
            break
        if t % 4 is 0:
            #rating = each.split(" of ")[0]
            try:
                rating = int(each[0])
                message = reviews_3[t + 1]
                
                message = h.unescape(message)
                
                review_table.append((rating, message))
                
            except ValueError:
                #print each
                pass
            except IndexError:
                #print each
                pass
        if each is not '':
            t = t + 1
    return review_table
    
def review_list_to_string(review_list):
    reviews = u""
    for review in review_list:
        reviews = reviews + review[1] + " " + str(review[0]) + "\n"
        h = HTMLParser()
        reviews = h.unescape(reviews)
        
    return reviews
    
def scrape_profile(profile_scraped):
    username, duration, rank, feedback, transactions, fans, profile_scraped_string = "", "", "", "", "", "", ""
    
    prev_item = None
    in_profile = False
    
    #print profile_scraped
    for item in profile_scraped:
        if prev_item is None:
            username = item

        elif "has been a vendor for" in prev_item:
            duration = item
              # print duration
            #     print "prev_item"

        elif "ranked in the" in prev_item:
            split = re.split("[top |%]", item)
            for each in split:
                if each is not "":
                    rank = each
                    #print "breaking"
                    break
                    
        elif "of sellers with" in prev_item: 
            split = item.split("%")
            for each in split:
                if each is not '':
                    feedback = each
                    #print "breaking"
                    break
                    
        elif "transactions" in item:
            transactions = prev_item
        
        elif "fans" in item:
            fans = prev_item
        
        elif ("report this vendor" in prev_item) or (in_profile):
            in_profile = True
            profile_scraped_string = profile_scraped_string + item 
            
        prev_item = item

    months, unit = duration.split(" ")
    if "year" in unit:
        months = str(int(months)*12)
        
    #FIX THIS THING
    re.sub("-----BEGIN PGP PUBLIC KEY BLOCK-----.+-----END PGP PUBLIC KEY BLOCK-----", "", profile_scraped_string)
    
    return (username, duration, rank, feedback, transactions, fans, profile_scraped_string)
