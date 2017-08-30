import re
import csv
from collections import namedtuple
import codecs
#from fire_helper01 import check

#============dictionary =======================================================

negs = ['не', 'не был', 'не было', 'не были', 'не была']

#По данным на утро 14 июля, в регионе зарегистрировано 22 очага на общей площади около 282 га
#-за лесных пожаров действует режим ЧС
#из-за лесных пожаров действовал режим чрезвычайной ситуации
fire = re.compile('(?<!из-за лесных )(пожар(ы|а|ов)?|очаг(а|ов)?|пламя)(?!(\w| на пшеничном поле|\sв\sквартире))')
fire1 = re.compile('(пожар(ы|а|ов)?|очаг(а|ов)?)(?!(\w| на пшеничном поле|\sв\sквартире))')
takes_place0 = re.compile('(?<!не )(произош[ёе]?л[аио]?|начал[аио]?ся?|бушу[ею]т|полыха[ею]т|вспыхнул[ио]?|действу[ею]т|зарегистрировали|зафиксировали|начал[ои]? действовать|не могут ликвидировать|не ликвидирован|угрожа[ею]т|возник(?!\w)|участились|туш[аи]т[\W])')
takes_place1 = re.compile('зарегистрирова(но|ны|н)|зафиксирова(но|ны|н)')
#сейчас проблема только с "не было зафиксировано"

liqu = re.compile('(?<!не )ликвидирова(ли|но|ны|н)|потушили|потушен(о|ы)?|останови(ли|но|ны|н)|локализова(ли|но|ны|н)|тушили')
succeed_liqu = re.compile('(?<!не )удалось (ликвидировать|потушить|остановить|локализовать)')
stop = re.compile('не допущено распространение')
burns = re.compile('гор[яи]?т|спалили')
burns_str = 'огонь продолжает пожирать' #'огонь продолжает пожирать лес'
#"пожарной опасности", "противопожарный режим", "лесопожарной обстановки"
#пожарн([оы]й|ая|ую|ы[еx]) - не нужно, а то пожарные, которые просто помогают спасателям, тоже работают на 3
more_abstract = re.compile('жар[аы]|температур[аы] воздуха|пожароопасност[ьи]|пожарн(ой|ая)|пожароопасн([оы]й|ая|ую|ы[еx])|противопожарн([оы]й|ая|ую|ы[еx])|лесопожарн([оы]й|ая|ую|ы[еx])|пожохран[аы]')
#burned = {'горел', 'сгорели'}
nonactual_modifiers = re.compile('(за\sпрошедшую\sнеделю|на\sпрошлой\sнеделе|в минувшие выходные|с\sначала 2014 года|с\sначала\sпожароопасного)')

#"С 15 апреля в крае из-за лесных пожаров действовал режим чрезвычайной ситуации."
#из-за таких примеров нужно всё-таки делать честное согласование

#===============grammar=========================================================================

def find_regexp(string, regex):
    s = re.search(regex, string)
    if s:
        found = s.group(0)
        coordinate = string.find(found)
        return (coordinate, coordinate + len(found))
    else: return (-1, -1)

def checkRight(substring, regex):
    coordinate = find_regexp(substring, regex)
    result = True if coordinate[1] == len(substring) and re.match('\W', substring[coordinate[0]-1]) else False
    return result


def check(string, verb, negs):
    coord = find_regexp(string, verb)
    m = [checkRight(string[:coord[0]-1], neg) for neg in negs]
    if coord != (-1, -1) and not sum(m):
        return True
    else: return False

#==============internals of classification============================================================

class WrongFire(Exception): pass

def classify_sentence(sentence):
    sentence = sentence.lower()
    if re.search('пожар\sв\sквартире', sentence): raise WrongFire
    elif re.search(burns, sentence) or re.search(burns_str, sentence): return 1
    elif re.search(fire, sentence) and (re.search(takes_place0, sentence) or check(sentence, takes_place1, negs)) and not re.search(nonactual_modifiers, sentence): return 1
    elif re.search(fire, sentence) and re.search(liqu, sentence) or re.search(succeed_liqu, sentence) or re.search(stop, sentence): return 2
    elif re.search(fire1, sentence) or re.search(more_abstract, sentence): return 3
    else: return 4

def classify_subtext(string):
    ss = re.split('[\.;]', string)
    scores = sorted([classify_sentence(s) for s in ss])
    first = scores[0]
    return first

#====================interface========================================================================
News = namedtuple('News', 'title body')

def classify_tuple(news_tuple):
        try:
            title  = classify_subtext(news_tuple.title)
            body = classify_subtext(news_tuple.body)
            predict = title if (body == 4 or title in [2, 1]) else body
        except WrongFire: predict = 4
        return predict

#======================testing==============================================================================

def test():
    some_news = [('Очередной лесной пожар произошел в Архангельской области,"По предварительным данным, причиной пожара стала сухая гроза. За период с 10 по 13 июля в регионе возникло семь лесных пожаров, пять из них были ликвидированы на малых площадях. Всего с начала пожароопасного сезона в области зафиксировано 50 «лесных» возгораний общей площадью порядка 300 гектаров."', 1), \
('На Ямале не осталось действующих природных пожаров,"На Ямале не осталось действующих природных пожаров. Однако в целях безопасности действует ограничение на посещение лесов. По данным региональной диспетчерской службы &quot;Леса Ямала&quot;, сегодня, 14 июля, на территории Ямало-Ненецкого автономного округа нет ни одного действующего лесного пожара', 3), \
('Эта новость вообще про бандикутов', 4), \
('Бушует пожар.', 1), \
('Режим пожарной опасности действует в области', 3),\
("Стоит жара", 3), \
('Пожар удалось остановить', 2)]
    for n in some_news:
        assert classify_subtext(n[0]) == n[1]

ScoredNews = namedtuple('ScoredNews', 'score title body')

def read_scored(fname):
    with codecs.open(fname, 'r', encoding = 'utf-8') as fh:
        scored = [ScoredNews(*l.split('\t')) for l in fh]
        return scored

def process():
    for n in read_scored('merged.csv'):#news_test.csv#merged.txt
        score = int(n[0])
        news = News(n[1], n[2])
        predict = classify_tuple(news)
        #if predict != score:
        if 1 > 0:
            log = 'predict = {p}, classified as {cl}, {t}\n'.format(p =  predict, cl = score, t = '')
            print(log)

#===============================================================================================

def main():
    import time
    begin = time.time()

#    test()
    process()

    duration = time.time() - begin
    dif = '{0} minutes {1} seconds'.format(duration//60, round(duration%60, 2))
    print(dif)

if __name__ == '__main__':
    main()

