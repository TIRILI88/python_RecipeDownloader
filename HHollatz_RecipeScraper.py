import os
import requests
import httplib2
from bs4 import BeautifulSoup

def addPageRecipes(urlSource, counterAdditionalPage, categoryURL, recipeLinkList, recipeNameList):
    urlCategoryAddPage = urlSource + categoryURL.split('.')[-2] + '_' + str(counterAdditionalPage) + '.html'
    http = httplib2.Http()
    status, response = http.request(urlCategoryAddPage)
    soup = BeautifulSoup(response, features='lxml')
    recipesAddPage = soup.find_all('a')
    for link in recipesAddPage:
        if link.has_attr('href'):
            recipeLinkList.append(link['href'])
            recipeNameList.append(link.get_text())

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
    counterAdditionalPage = 0
    for _ in recipeNameList: 
        if 'weiter' in recipeNameList:
            #find 'weiter' in recipeNameList and remove:
            popIndex = recipeNameList.index('weiter')
            recipeNameList.pop(popIndex)
            recipeLinkList.pop(popIndex)
            #add recipes on additional pages
            addPageRecipes(urlSource, counterAdditionalPage, categoryURL, recipeLinkList, recipeNameList)
            counterAdditionalPage += 1
    for _ in range(len(recipeLinkList)-1):
        urlCategoryRecipe = urlCategory.split('/')[-1]
        urlSource = 'https://hhollatz.de/Rezepte/Profi/' + urlCategoryRecipe.split('.')[0] + '/pdf/'
        urlWP = recipeLinkList[counterBeilagen].split('/')[-1]
        url = urlSource + urlWP
        name = recipeNameList[counterBeilagen]
        myfile = requests.get(url)
        for _ in recipeLinkList:
            if (category or chefName) in urlWP:
                continue
            elif name == 'weiter':
                continue
            else: 
                if not os.path.exists(path + chefName + '/' + category + '/' + name + '.pdf'):
                    open(path + chefName + '/' + category + '/' + name + '.pdf', 'wb').write(myfile.content)
        counterBeilagen += 1
    print('--- Download ' + chefName + ': ' + category + ' completed ---')

def downloadCookBook(chefName, url, category, path): #to download whole cookbooks in category section
    myfile = requests.get(url)
    if not os.path.exists(path + chefName + '/' + category + '.pdf'):
        open(path + chefName + '/' + category + '.pdf', 'wb').write(myfile.content)

def mkDirCategories(chefName, chefURL, path):
    urlSource = 'https://hhollatz.de/Rezepte/' + chefURL
    http = httplib2.Http()
    status, response = http.request(urlSource)
    soup = BeautifulSoup(response, features='lxml')
    recipes = soup.find_all('a')
    categoryLinkList = []   #Creating Category Lists to store the Category Names in
    categoryNameList = []
    for link in recipes:    #adding all Links to Lists
        if link.has_attr('href'):
            categoryLinkList.append(link['href'])
            categoryNameList.append(link.get_text())
    counterCategories = 1
    for _ in range(len(categoryLinkList)-1):    ##Creating folder-structure on path
        category = categoryNameList[counterCategories]
        categoryURL = categoryLinkList[counterCategories]
        pathComplete = path + chefName + '/' + category + '/'
        if chefName in category:    #find chefName in Lists, downloading Cookbook and remove Link and Name from list
            urlCookBook = 'https://hhollatz.de/Rezepte/Profi_k/' + categoryURL
            downloadCookBook(chefName, urlCookBook, category, path)
            categoryNameList.pop(counterCategories)
            categoryLinkList.pop(counterCategories)
        if not os.path.exists(pathComplete):
            os.makedirs(pathComplete)
        downloadRecipes(chefName, category, categoryURL, path) #passing category lists to downloadRecipes Func
        counterCategories += 1
    print('--- Download Chef: ' + chefName + ' completed! ----')

def mkDirChefs(path): #making the Chef directories
    urlSource = "https://hhollatz.de/Rezepte/Profi.html"
    http = httplib2.Http()
    status, response = http.request(urlSource)
    soup = BeautifulSoup(response, features='lxml')
    recipes = soup.find_all('a')
    chefLinkList = [] #creating the lists to store the chefs
    chefNameList = []
    for link in recipes:
        if link.has_attr('href'):
            chefLinkList.append(link['href'])
            chefNameList.append(link.get_text())
    counterChefs = 26 #No. 26 is the first Chef - before are just categories to prevent duplicates
    for _ in range(len(chefLinkList)-1):
        chefName = chefNameList[counterChefs]
        chefURL = chefLinkList[counterChefs]
        print('--- Download Chef: ' + chefName + ' started! ----')
        pathComplete = path + chefName 
        if not os.path.exists(pathComplete):
            os.makedirs(pathComplete)
        mkDirCategories(chefName, chefURL, path) #passing the lists to the categories
        progress = round(((counterChefs - 25) / (len(chefLinkList) - 26)*100),2) #to keep the progress
        print('--- Progress: ' + str(progress) + '% ---')
        counterChefs += 1
    print('!!!--- Download Completed ----!!!')


def executer():
    print('Please consider: Just recipes from professional Chefs will be downloaded')
    path = input('Please enter path to store the recipes: ') #Enter the path for the directories
    mkDirChefs(path)

executer()