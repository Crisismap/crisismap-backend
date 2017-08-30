# -*- coding: utf-8 -*-
import os
import psycopg2
from bs4 import BeautifulSoup
import re;


class db_manager(object):
  def connect(self):
    self.db = psycopg2.connect("host=192.168.14.189 port=9999 user=postgres password=postgres dbname=maps")
  def close(self):
    self.db.close()
  
  def load_news_locations(self):
    cur = self.db.cursor();
    cur.execute("SELECT id,guid,debug_output FROM test.news_rss");
    news = cur.fetchall();
    cur.close();
    
    allArticles = []; 
    for article in news:
      allArticles.append({"rss_id" : article[0],"guid":article[1],"debug_output":article[2]});  
    return allArticles
    
  def get_latest_news_article(self):
    cur = self.db.cursor();
    cur.execute("SELECT id,pub_date,guid,title,type,link,description FROM test.news_rss ORDER BY id DESC LIMIT 1");
    news = cur.fetchall();
    cur.close();
    
    allArticles = []; 
    for article in news:
      allArticles.append({"id" : article[0],"pub_date":article[1],"guid":article[2],"title":article[3],"type":article[4],"link":article[5],"description":article[6]});  
    return allArticles[0]

  def custom_strip_tags(self, value):
    soup = BeautifulSoup(value);
    allFontTags = soup.find_all("font",{"size":"-1"});
    if(len(allFontTags) > 0):
      content = soup.find_all("font",{"size":"-1"})[1];
    else:
      content = value;  
    result = re.sub(r'<[^>]*?>', ' ', unicode(content))
    return unicode(result)
    
  def insert_news(self, news_type, entry, str_date, localized):
    cur = self.db.cursor()
    descr = self.custom_strip_tags(entry.description).replace("'", "''")#.encode('utf-8')
    #print s.encode('utf-8')
    #s = str(s)
    #print s
    sql = "INSERT INTO test.news_rss(guid, title, link, description, pub_date, type, is_localized, debug_output, phrases) VALUES ('%s','%s','%s','%s','%s','%s',%s,NULL,NULL) ON CONFLICT(guid) DO NOTHING" % (entry.guid, entry.title.replace("'", "''"), entry.link, descr, str_date, news_type, localized)
    #print sql
    #sql = u"IF (SELECT COUNT(1) FROM NewsRSS WHERE guid = '{guid}') = 0 INSERT INTO NewsRSS VALUES ('{guid}','{title}','{link}','{descr}','{str_date}','{type}',{loc},'',NULL,NULL)".format(guid = entry.guid, title = entry.title.replace("'", "''"), link=entry.link, descr = descr, str_date = str_date, type = type, loc = localized)
    #print sql
    #sqlCmd = "IF (SELECT COUNT(1) FROM NewsRSS WHERE guid = '"+entry.guid+ "') = 0 INSERT INTO NewsRSS Values ('"+entry.guid+"','"+entry.title.replace("'", "''")+"','"+entry.link+"','"+s.replace("'", "''")+"','"+str_date+"','"+type+"',{0},'',NULL,NULL)".format(localized)
    cur.execute(sql)
    self.db.commit()
    
  def LoadUnclassifiedNews(self, type):
    cur = self.db.cursor();
    cur.execute("SELECT /*TOP 50*/ news_location_id,Title,Description FROM NewsLocations where class is null and type = '" + type + "'");
    news = cur.fetchall();
    cur.close();
    allArticles = [];
    for article in news:
      allArticles.append({"id" : article[0],"title":article[1],"body":article[2]});  
    return allArticles;

  def UpdateNewsClass(self, id, newsClass):
    cur = self.db.cursor();
    cur.execute("UPDATE NewsLocations SET [class] = " + str(newsClass) + " WHERE news_location_id = " + str(id));
    cur.close();

  def LoadUnclassifiedFireNews(self):
    cur = self.db.cursor();
    cur.execute("SELECT id,Title,Description FROM FireNewsLocations where class is null");
    news = cur.fetchall();
    cur.close();
    allArticles = [];
    for article in news:
      allArticles.append({"id" : article[0],"title":article[1],"body":article[2]});  
    return allArticles;
    
  def UpdateFireNewsClass(self, id, fireClass):
    cur = self.db.cursor();
    sql = "UPDATE FireNewsLocations SET [class] = " + str(fireClass) + " WHERE id = " + str(id)
    #print(sql)
    cur.execute(sql);
    cur.close();
    
    
  def LoadUnlocalizedNewsFromDB(self):
    cur = self.db.cursor();
    cur.execute("SELECT /*TOP 1*/ id,pubDate,guid,title,type,link,description FROM NewsRSS WHERE isLocalized = 0 ORDER BY id DESC");
    news = cur.fetchall();
    cur.close();
    
    allArticles = []; 
    for article in news:
      #print article#[0]
      #print article[2].encode('cp1251', 'ignore')
      #return []
      allArticles.append({"id" : article[0],"pubDate":article[1],"guid":article[2],"title":article[3],"type":article[4],"link":article[5],"description":article[6]});  
    return allArticles

  def LoadLastNews(self, since_date):
    cur = self.db.cursor();
    #cur.execute("SELECT news_location_id,Title,Description FROM NewsLocations where pub_date > convert(datetime, '" + since_date + "', 20) ORDER BY news_location_id DESC")
    cur.execute("SELECT news_location_id,Title,Description FROM NewsLocations where pub_date > convert(datetime, '" + since_date + "', 20)")
    news = cur.fetchall()
    cur.close()
    allArticles = []
    for article in news:
      allArticles.append({"id" : article[0],"title":article[1],"body":article[2]})
    return allArticles

  def UpdateNewsClusters(self, data):
    cur = self.db.cursor()
    #chucks = 0
    chunk_size = 0
    sql = "DECLARE @clusters AS TABLE([num] INT, [id] INT, [c_id] INT);" + os.linesep
    i = 0
    for row in data:
      if (chunk_size == 0):
        sql += "INSERT INTO @clusters([num], [id], [c_id]) VALUES" + os.linesep
      elif (chunk_size > 0):
        sql += ","
      sql += "(" + str(i) + "," + str(row[0]) + "," + str(row[1]) + ")"
      chunk_size += 1
      i += 1
      if (chunk_size == 1000):
        chunk_size = 0
        sql += ";" + os.linesep
      #print sql
    sql += ";" + os.linesep
    sql += "UPDATE dest SET [cluster_id] = src.[c_id] FROM [dbo].[NewsLocations] dest INNER JOIN @clusters src ON dest.[news_location_id] = src.[id]"
    #sql += "MERGE [dbo].[NewsLocations] AS dest  USING (SELECT [id], [c_id] FROM @clusters) AS src ON (dest.[news_location_id] = src.[id])" + os.linesep
    #sql += "WHEN MATCHED THEN UPDATE SET [cluster_id] = src.[c_id]" + os.linesep
    #sql += "WHEN NOT MATCHED BY TARGET THEN INSERT"
    return sql

  def StoreArticleLocationsScanexTest(self,article,locations,debugOutput,allPhrases):
    for coords in locations:
      cur = self.db.cursor();
      sqlCommand = u"INSERT INTO NewsLocationsScanexTest (rss_id,URL,Title,Description,guid,lat,long,pub_date,type,phrases) VALUES ("+str(article["id"])+",'"+article["link"]+"','"+article["title"].replace("'", "''")+"','"+article["description"].replace("'", "''")+"','"+article["guid"]+"',"+str(float(coords[1]))+","+str(float(coords[0]))+",'"+article["pubDate"]+"','"+article["type"]+"','"+allPhrases.replace("'", "''")+"')";
      cur.execute(sqlCommand);
      cur.close();

  def StoreArticleLocations(self,article,locations,debugOutput,allPhrases):
    cur = self.db.cursor();
    sqlCommand = u"UPDATE NewsRSS SET isLocalized = 1,debug_output = '" + debugOutput + "',phrases='" + allPhrases.replace("'", "''") + "' WHERE guid = '"+article["guid"] + "'"
    #print sqlCommand.encode('ascii', 'ignore');
    cur.execute(sqlCommand);
    cur.close();
    
    for coords in locations:
      cur = self.db.cursor();
      sqlCommand = u"INSERT INTO test.news_locations(rss_id,url,title,description,guid,lat,long,pub_date,type,phrases) VALUES ("+str(article["id"])+",'"+article["link"]+"','"+article["title"].replace("'", "''")+"','"+article["description"].replace("'", "''")+"','"+article["guid"]+"',"+str(float(coords[1]))+","+str(float(coords[0]))+",'"+article["pubDate"]+"','"+article["type"]+"','"+allPhrases.replace("'", "''")+"')";
      #print sqlCommand.encode('ascii', 'ignore');
      cur.execute(sqlCommand);
      cur.close();
      
      #cur = self.db.cursor();
      #cur.execute("SELECT news_location_id FROM NewsLocations WHERE guid = '"+article["guid"] + "' AND lat = '" + coords[1] + "' AND long = '" + coords[0] +"'");
      #newLocationId = cur.fetchall()[0][0];
      #print newLocationId;
      #cur.close();
      
      
      #sqlCommand = "INSERT INTO NewsLayer (news_location_id,lat,long,pub_date,title,URL) VALUES ("+str(newLocationId)+","+str(float(coords[1]))+","+str(float(coords[0]))+",'"+article["pubDate"]+"','"+article["title"]+"','"+article["link"]+"')";
      #print sqlCommand
      #cur = self.db.cursor();
      #cur.execute(sqlCommand);
      #cur.close();
      
if __name__ == '__main__':
  db = ScanexDBStorage()
  db.ConnectMaps()
  print db.LoadLastNews('2016-08-05')