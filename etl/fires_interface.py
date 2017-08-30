import fire_classifier
import min_cl

def main():
    from scanex_storage import ScanexDBStorage;
    dbScanex = ScanexDBStorage();
    dbScanex.ConnectMaps();
    fireNews = dbScanex.LoadUnclassifiedFireNews();
    #print(fireNews)
    model = min_cl.learn()
    for fn in fireNews:
        predict = min_cl.predict((fn["title"], fn["body"]), model)[0]
        print predict
        #news = fire_classifier.News(fn["title"], fn["body"])
        #predict = fire_classifier.classify_tuple(news)
        #print predict		
        dbScanex.UpdateFireNewsClass(fn["id"], predict)

if __name__ == '__main__':
    main()
