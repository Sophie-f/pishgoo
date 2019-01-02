import re
from bs4 import BeautifulSoup
import requests
site_request = requests.get('https://bama.ir')
soup = BeautifulSoup(site_request.text,'html.parser')
cars_list = soup.find_all('span', attrs = {'class': 'home-brand-model-title nav-sub-brand-name-show-text'})



def search_car(link, max_num):
    prime_link = link
    count = 0
    page_index = 1
    while count <= max_num:
        request = requests.get('https://bama.ir' + link, allow_redirects = False)
        if request.status_code != 200: 
            break
        soup = BeautifulSoup(request.text, 'html.parser')
        soup_list = soup.find_all('li', attrs = {'itemtype': "http://schema.org/Car"})
        for soup in soup_list:
            new_milage = ''
            milage = soup.find('span', attrs = {'class' :"yellow-background"})
            price = soup.find_all(itemprop = 'price' )
            # we do not consider the car with double price(installment and prepayment and the car without milage) 
            if len(price) != 1 or  milage is None: 
                continue
            # we do not consider the car without definit price( like تماس بگیرید، در توضیحات)
            price = price[0]['content']
            if price == '0':
                continue
                

            count += 1 
            
            if count > max_num:
                break    
            details = soup.find('h2',attrs = {'itemprop': 'name'}).text.split('،')

            for i in range(len(details)):
                details[i] = details[i].strip()

            year = details[0]
            milage_list = milage.next_sibling.strip().split(',')
            for c in milage_list:
                if c == 'صفر':
                    c = '0'
                new_milage += c 
            print('{0:4d} {1:6d}   {2:,}'.format(int(year),int(new_milage), int(price)))  
        page_index += 1            
        link = prime_link+'?page='+str(page_index)


max_num = int(input('Enter maximum number of car: '))
flag = True
while flag:
    name = input('Enter the brand (in persian): ')    
    for car in cars_list:
        if name == car.text.strip():
            opt_car = car
            flag = False
            break
    if flag:        
        print('This brand does not exist.')
tag = opt_car.parent['href']

models_list = []
for car in cars_list:
    link = re.findall(r'({}.*)'.format(tag), car.parent['href'])
    if link != []:
        if link[0] not in models_list:
            models_list.append(link[0])
print("Enter the number of model")
print(1, 'all models')         
for i in range(1, len(models_list)):
    model = re.findall(r'{}/(.*)'.format(tag) ,models_list[i])
    print(i+1, model[0])
m_index = int(input())
opt_model = models_list[m_index-1]

if m_index == 1:
   search_car(opt_model, max_num)
else:       
    versions_list = []
    links = re.findall(r'\"({}/.*?)\"'.format(opt_model), site_request.text)
    for link in links:
        if link not in versions_list:
            versions_list.append(link)
    print('Enter the version index')   
    print(1,'All versions')    

    
    for j in range(0, len(versions_list)):
        print(j+2,re.findall(r'{}/(.*)'.format(opt_model), versions_list[j])[0])
    v_index = int(input()) 
    if v_index == 1:
        search_car(opt_model, max_num) 
    else:        
        search_car(versions_list[v_index-2], max_num)

