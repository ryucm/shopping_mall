import psycopg2
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

con = psycopg2.connect(
    host = 'arjuna.db.elephantsql.com',
    database = 'jufgneai',
    user = 'jufgneai',
    password = 'GSJ9LWjCYj-1kKjmwpH4GaqdWl-ApwS0'
)

period = ['1d','1w','1m','3m','1y']
styles = {
    '001' : 'top',
    '002' : 'outer',
    '003' : 'pants',
    '004' : 'bag',
    '005' : 'shoes',
    '011' : 'accessory',
    '017' : 'sports',
    '018' : 'sneakers'}

cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS rank')
cur.execute('DROP TABLE IF EXISTS list')
cur.execute('''CREATE TABLE IF NOT EXISTS list(
    meterial_id VARCHAR(15) NOT NULL PRIMARY KEY,
    kind VARCHAR(15) NOT NULL)
    ''')

for i in styles.keys():
    cur.execute(f"INSERT INTO list values('{i}','{styles[i]}')")

cur.execute('''CREATE TABLE IF NOT EXISTS rank(
    rank INT NOT NULL,
    brand_name TEXT,
    item_name TEXT NOT NULL,
    kind VARCHAR(15),
    price INT,
    recommend INT NULL,
    period VARCHAR(10),
    FOREIGN KEY(kind) REFERENCES list(meterial_id))
    ''')



for style in tqdm(styles.keys()):
    for date in period:
        auto = 0
        brand_name=[]
        page_num = 1 #크롤링 시작 페이지
        while page_num <= 2:
            url = f'https://search.musinsa.com/category/{style}?d_cat_cd={style}&brand=&rate=&page_kind=search&list_kind=small&sort=sale_high&sub_sort={date}&page={page_num}&display_cnt=90&sale_goods=&group_sale=&ex_soldout=&color=&price1=&price2=&exclusive_yn=&shoeSizeOption=&tags=&campaign_id=&timesale_yn=&q=&includeKeywords=&measure='
            res = requests.get(url)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            item_title = soup.find('div', attrs = {'id' : 'goods_list'}).find_all('div', attrs = {'class':'li_inner'})
            for title in item_title:
                a = map(lambda x: x.strip().replace('[패밀리세일]','').replace('[클리어런스]','').replace('MEMBERSHIP PRICE▼','').replace('무신사 회원가X','').replace(',',''),title.get_text().split('\n'))
                
                bin = []
                for i in a:
                    if i =='리':
                        i = 'Lee'
                    elif i=='청':
                        i = 'Chung'
                    if len(i) > 1:
                        bin.append(i)
                brand_name.append(bin)
            page_num += 1
        
        for i in brand_name:
            if 'SALESPAUSE' in i[0]:
                i.pop(0)
            if ('배송' in i[1]) | ('지연' in i[1]):
                i.pop(1)
            # print(i)
            # print(len(i))
            if '-' in i[3]:
                i.pop(3)
            while len(i) <= 4:
                i.append('0')
            if '타임세일' in i[4]:
                i.pop(4)
            while len(i) <= 4:
                i.append('0')

            auto +=1
            # print(i)
            # print(len(i))
            cur.execute("INSERT INTO rank values('{}','{}','{}','{}','{}','{}','{}')".format(auto,i[0], i[1],style,*re.findall(r'\d+',i[3]), i[4],date))

con.commit()
