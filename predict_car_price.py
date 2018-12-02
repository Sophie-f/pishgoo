import re
from bs4 import BeautifulSoup
import mysql.connector
import requests
from sklearn import tree


def make_table_in_data_base():
    cnx = mysql.connector.connect(user = '', password ='', host='127.0.0.1', database = 'car' )
    cursor = cnx.cursor()
    query = 'CREATE TABLE all_cars(name varchar(50),year int, milage int, price bigint, id int ); ALTER TABLE all_cars ADD CONSTRAINT uc_all_cars UNIQUE(id);'
    cursor.execute(query, multi = True)
    cnx.close()

def choose_car_name():
    site_request = requests.get('https://bama.ir')
    soup = BeautifulSoup(site_request.text,'html.parser')
    cars_list = soup.find_all('span', attrs = {'class': 'home-brand-model-title nav-sub-brand-name-show-text'})
    full_name = ''
    flag = True
    while flag:
        name = input('Enter the brand (in persion): ')    
        for car in cars_list:
            if name == car.text.strip():
                full_name += (name +',')
                opt_car = car
                flag = False
                break
        if flag:        
            print('This brand does not exist.')
    tag = opt_car.parent['href']

    models_list = []
    persion_model_list =[]
    for car in cars_list:
        link = re.findall(r'({}.*)'.format(tag), car.parent['href'])
        if link != []:
            if link[0] not in models_list:
                models_list.append(link[0])
                persion_model_list.append(car.text.strip())
    print("Enter the model index")
    
    for i in range(1, len(models_list)):
        model = re.findall(r'{}/(.*)'.format(tag), models_list[i])
        print(i, model[0])
    m_index = int(input())
    opt_model = models_list[m_index]
    full_name += persion_model_list[m_index]
        
    versions_list = []
    links = re.findall(r'\"({}/.*?)\"'.format(opt_model), site_request.text)
    for link in links:
        if link not in versions_list:
            versions_list.append(link)

    if versions_list != []:    
        print('Enter the version index')       
        for j in range(0, len(versions_list)):
            print(j+1,re.findall(r'{}/(.*)'.format(opt_model), versions_list[j])[0])
        opt_version = versions_list[int(input())-1]
        full_name += (','+ soup.find('a' , attrs = {'href': opt_version } ).contents[1].contents[0].strip()) 
    else:
        opt_version = opt_model      
    print('you piced out:' ,full_name)
    return 'https://bama.ir'+opt_version , full_name

def search_car_data(link, full_name):
    def insert_data_to_database(full_name, year, milage, price, car_id):
        flag = False
        cnx = mysql.connector.connect(user = '', password ='', host='127.0.0.1', database = 'car' )
        cursor = cnx.cursor()
        query = 'INSERT INTO all_cars value(\'{}\',{},{},{},{})'.format(full_name, int(year) , int(milage) , int(price), int(car_id[0]))
        try:
            cursor.execute(query)
            flag = True
        except mysql.connector.errors.IntegrityError:
            pass
        cnx.commit()
        cnx.close()
        return flag

    prime_link = link
    count = 0
    page_index = 1
    number_of_car = 500
    while count < number_of_car:
        request = requests.get(link, allow_redirects = False)
        if request.status_code != 200: 
            break
        soup = BeautifulSoup(request.text, 'html.parser')
        soup_list = soup.find_all('li', attrs = {'itemtype': "http://schema.org/Car"})
        for soup in soup_list:
            new_milage = ''
            milage = soup.find('span', attrs = {'class' :"yellow-background"})
            price = soup.find_all(itemprop = 'price' )    
            #we do not consider the car with double price(installment and prepayment or the car without milage) 
            if len(price) != 1 or  milage is None: 
                continue
            # we do not consider the car without definit price( like تماس بگیرید، در توضیحات)
            price = price[0]['content']
            if price == '0':
                continue
                    
            milage_list = milage.next_sibling.strip().split(',')
            for c in milage_list:
                if c == 'صفر':
                    c = '0'
                new_milage += c

            id_soup = soup.find('a', attrs = {'class': 'cartitle cartitle-desktop'})
            car_id = re.findall(r'car/details-.*-(.*)/', id_soup['href'])
            
            details = soup.find('h2',attrs = {'itemprop': 'name'}).text.split('،')
            year = details[0].strip()

            if insert_data_to_database(full_name, year, new_milage, price, car_id):
                count += 1   

        page_index += 1            
        link = prime_link+'?page='+str(page_index)

def read_analyse_data(name):
    cnx = mysql.connector.connect(user = '', password ='', host='127.0.0.1', database = 'car' )
    cursor = cnx.cursor()
    x = []
    y = []
    query = 'SELECT year, milage, price FROM all_cars where name = \'{}\''.format(name)
    cursor.execute(query)
    flag = False
    for year, milage, price  in cursor:
        x.append([year,milage])
        y.append(price)
        flag = True
    if flag:
        clf = tree.DecisionTreeRegressor()
        clf = clf.fit(x, y)
        year_data = input('Enetr the year, examples: 1397 or 2018 : ')
        milage_data = input('Enter the milage (kilometer): ')
        answer = clf.predict([[year_data , milage_data]])
        print('The price is {:,} toman'.format(answer[0],grouping = True))
    else:
        print('Your car does not exist in the database.')
    cnx.close()  


if input('do you have table in database? y/n ') != 'y':
    make_table_in_data_base()
link, full_name = choose_car_name()
search_car_data(link, full_name)
read_analyse_data(full_name)