import os
import requests
import httplib2
from bs4 import BeautifulSoup

def downloadRecipes(chefName, category, categoryURL, path):
    urlSource = 'https://hhollatz.de/Rezepte/Profi_k/'
    urlCategory = urlSource + categoryURL
    http = httplib2.Http()
    status, response = http.request(urlCategory)
    soup = BeautifulSoup(response, features='lxml')
    recipes = soup.find_all('a')
    recipeLinkList = []
    recipeNameList = []
    for link in recipes:
        if link.has_attr('href'):
            recipeLinkList.append(link['href'])
            recipeNameList.append(link.get_text())
    counterBeilagen = 1
    if 'weiter' in recipeNameList:
        #-- if WEITER = TRUE
        counterAdditionalPage = 0
        for _ in range(4):
            urlSourceAddPage = 'https://hhollatz.de/Rezepte/Profi_k/'
            urlCategoryAddPage = urlSourceAddPage + categoryURL.split('.')[-2] + '_' + str(counterAdditionalPage) + '.html'
            http = httplib2.Http()
            status, response = http.request(urlCategoryAddPage)
            soup = BeautifulSoup(response, features='lxml')
            recipesAddPage = soup.find_all('a')
            for link in recipesAddPage:
                if link.has_attr('href'):
                    recipeLinkList.append(link['href'])
                    recipeNameList.append(link.get_text())
            counterAdditionalPage += 1
    for _ in range(len(recipeLinkList)-1):
        urlSource = 'https://hhollatz.de/Rezepte/Profi/' + category + '/pdf/'
        urlWP = recipeLinkList[counterBeilagen].split('/')[-1]
        url = urlSource + urlWP
        chefNameURL = chefName.split(' ')[0] + '_' + chefName.split(' ')[-1]
        name = recipeNameList[counterBeilagen]
        myfile = requests.get(url)
        for _ in recipeLinkList:
            if (category or chefNameURL) in urlWP:
                continue
            else: 
                open(path + chefName + '/' + category + '/' + name + '.pdf', 'wb').write(myfile.content)
        counterBeilagen += 1
    print('--- Download ' + chefName + ': ' + category + ' completed ---')

def mkDirCategories(chefName, chefURL, path):
    urlSource = 'https://hhollatz.de/Rezepte/' + chefURL
    http = httplib2.Http()
    status, response = http.request(urlSource)
    soup = BeautifulSoup(response, features='lxml')
    recipes = soup.find_all('a')
    categoryLinkList = []
    categoryNameList = []
    for link in recipes:
        if link.has_attr('href'):
            categoryLinkList.append(link['href'])
            categoryNameList.append(link.get_text())
    counterCategories = 1
    for _ in range(len(categoryLinkList)-1):
        category = categoryNameList[counterCategories]
        categoryURL = categoryLinkList[counterCategories]
        pathComplete = path + chefName + '/' + category + '/'
        if not os.path.exists(pathComplete):
            os.makedirs(pathComplete)
        downloadRecipes(chefName, category, categoryURL, path)
        counterCategories += 1
    print('--- Download Chef: ' + chefName + ' completed! ----')

def mkDirChefs(path):
    urlSource = "https://hhollatz.de/Rezepte/Profi.html"
    http = httplib2.Http()
    status, response = http.request(urlSource)
    soup = BeautifulSoup(response, features='lxml')
    recipes = soup.find_all('a')
    chefLinkList = []
    chefNameList = []
    for link in recipes:
        if link.has_attr('href'):
            chefLinkList.append(link['href'])
            chefNameList.append(link.get_text())
    counterChefs = 26
    for _ in range(len(chefLinkList)-1):
        chefName = chefNameList[counterChefs]
        chefURL = chefLinkList[counterChefs]
        print('--- Download Chef: ' + chefName + ' started! ----')
        pathComplete = path + chefName  #make input??
        if not os.path.exists(pathComplete):
            os.makedirs(pathComplete)
        mkDirCategories(chefName, chefURL, path)
        progress = round(((25 - counterChefs) / (len(chefLinkList) - 26)*100),2)
        print('--- Progress: ' + str(progress) + '% ---')
        counterChefs += 1
    print('!!!--- Download Completed ----!!!')


def executer():
    print('Please consider: Just recipes from professional Chefs will be downloaded')
    path = input('Please enter path to store the recipes: ')
    mkDirChefs(path)

#'/Users/riedy/Documents/edX/Python/Rezepte/Files/'
executer()