#from toponyms.toponyms import toponyms
from db_manager import db_manager

if __name__ == '__main__':
  db = db_manager()
  db.connect()
  print db.load_news_locations()
  db.close()