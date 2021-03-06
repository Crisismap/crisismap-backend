# -*- coding: utf-8 -*-
# This script figures out the most relevant location to the news articles.
 
from scanex_storage import ScanexDBStorage;
#from location_extraction import LocationExtraction;
from location_extraction_abbyy import LocationExtractionAbbyy;
import sys;

reload(sys);
sys.setdefaultencoding('utf-8');

## Initialize utility classes
#le = LocationExtraction();
le = LocationExtractionAbbyy();
dbScanex = ScanexDBStorage();

dbScanex.ConnectMaps();

# Load news that had not yet been localized from the database.
news = dbScanex.LoadUnlocalizedNewsFromDB();

# For each article, determine candidate locations
for article in news:
  try:
    print 'article id: ', article["id"]#, article["guid"].encode('utf-8', 'ignore');
    ## Append title and description
    articleTxt = article["title"] + ". " + article["description"];
    ## Extract location from the joint text
    [locations, debugOutput, allPhrases] = le.GetCandidateLocations(articleTxt, True, True);
    ## Record location and debug output to the database.
    dbScanex.StoreArticleLocations(article,locations,debugOutput,allPhrases);
    ## Extract location from the joint text via ScanexGeocoder
    [locations, debugOutput, allPhrases] = le.GetCandidateLocations(articleTxt, True, False);
    ## Record location and debug output to the database.
    dbScanex.StoreArticleLocationsScanexTest(article,locations,debugOutput,allPhrases);
  except Exception, e:
    print "Error processing news: ", str(e)#.encode('utf-8');

  
## Close database
dbScanex.Close();