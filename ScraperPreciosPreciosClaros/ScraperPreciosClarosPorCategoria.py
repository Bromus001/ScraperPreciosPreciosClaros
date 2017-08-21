from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
from datetime import datetime
import json
import sys
import os



#
# PRECIOS
#


mRootFolder = os.path.dirname(os.path.realpath('__file__'))
print ('Current folder is {}'.format(mRootFolder))

mContinue = 1
mErrCount = 0
mAlreadyProcessed = dict()
mPage = 1

driver = webdriver.Chrome(executable_path='C:\Bromus\Software\chromedriver.exe')
driver.get("https://www.preciosclaros.gob.ar/#!/buscar-productos")
mLocalizationButton = driver.find_element_by_id("la_plata")
mLocalizationButton.click()


while (mContinue == 1):

    print ("Iniciando navegacion al sitio ...")
    
    sleep(5)
    
    try:

        mInput = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH  , "//input[contains(@class, 'showSuggester')] "))
        )

        sleep(10)

        mPendingCategories = os.path.join(mRootFolder, 'data/pending_categories.txt')
        with open(mPendingCategories) as f:
            for mLine in f:
                mCategoryId = mLine

        print ("procesando categoria {}".format(mCategoryId))        

        mCategories = driver.find_elements_by_xpath("//div[contains(@class, 'buscador-categorias')]/div")

        mCategory = mCategories[int(mCategoryId)].find_element_by_xpath(".//div[@class='item-categoria']")

        mCategory.click()

        mFoundProducts = []

        mProducts = []
        
        mFileName = os.path.join(mRootFolder, 'data/' + 'precios_claros_precios_' +  datetime.now().strftime("%Y%m%d-%H%M%S") + '.txt')


        while (mPage > 0):

            sleep(5)

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH  , "//div[contains(@class, 'contenedor-filtro-vista')] "))
            )

            mTotalProductsDiv = driver.find_elements_by_xpath("//div[@class= 'caja-producto-mosaico']")

            mTotalFound = len(mTotalProductsDiv)

            mFoundProducts = []

            print ("Encontrados {} productos".format(mTotalFound))
            
            for mIndex in range(0, mTotalFound):

                sleep(2)

                mProductDiv = driver.find_elements_by_xpath("//div[@class= 'caja-producto-mosaico']")[mIndex]        

                mDetailButton = mProductDiv.find_element_by_xpath(".//div[contains(@class, 'nombre-producto')]")

                if (not mDetailButton.is_displayed()):
                    continue

                mProductName = mProductDiv.find_element_by_xpath(".//div[contains(@class, 'nombre-producto') and contains(@class, 'ng-binding')]").get_attribute("innerText")
                mProductSku = mProductDiv.find_element_by_xpath(".//div[contains(@class, 'ean') and contains(@class, 'ng-binding')]").get_attribute("innerText")

                mFoundProducts.append(mProductSku)

                if (mProductSku in mAlreadyProcessed):
                    print("Producto {} ya procesado".format(mProductName))
                    continue
                else:
                    mAlreadyProcessed[mProductSku] = mProductName

                print("Procesando producto " + mProductName.strip())

                mDetailButton.click()

                mOk = 0

                try:
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH  , "//table[contains(@class, 'tabla-comparativa') and contains(@class, 'detalle-producto-tabla')]"))
                    )

                except TimeoutException:
                    mOk = -1

                if (mOk == 0):

                    mStoreRows = driver.find_elements_by_xpath("//table[contains(@class, 'tabla-comparativa') and contains(@class, 'detalle-producto-tabla')]/tbody/tr")

                    for mStoreRow in mStoreRows:

                        if (mStoreRow.is_displayed()):
                            mStoreName = mStoreRow.find_element_by_xpath(".//p[contains(@class, 'nombre')]").get_attribute("innerText")
                            mStoreAddress = mStoreRow.find_element_by_xpath(".//p[contains(@class, 'direccion')]").get_attribute("innerText")
                            mStoreCity = mStoreRow.find_element_by_xpath(".//p[contains(@class, 'ciudad')]").get_attribute("innerText")
                            #mStoreDistance = mStoreRow.find_element_by_xpath(".//td[contains(@class, 'detalle-distancia')]").get_attribute("innerText")
                            mStoreListPrice = mStoreRow.find_element_by_xpath(".//span[contains(@class, 'precio-lista')]").get_attribute("innerText")
                            mStoreProm1Price = mStoreRow.find_element_by_xpath(".//span[contains(@class, 'precio-promo-1')]/span").get_attribute("innerText")
                            mStoreProm1Label = mStoreRow.find_element_by_xpath(".//span[contains(@class, 'precio-promo-1')]/span").get_attribute("title")
                            mStoreProm2Price = mStoreRow.find_element_by_xpath(".//span[contains(@class, 'precio-promo-2')]/span").get_attribute("innerText")
                            mStoreProm2Label = mStoreRow.find_element_by_xpath(".//span[contains(@class, 'precio-promo-2')]/span").get_attribute("title")      
                            #mStoreImage = mStoreRow.find_element_by_xpath(".//div[@class = 'contenedor-imagen']/img").get_attribute("src") 

                            mLine = '|'.join((mProductSku
                                                , mStoreName.strip()
                                                , mStoreAddress.strip()
                                                , mStoreCity.strip()
                                                , str(mStoreListPrice).strip().replace("$","").replace(",",".").replace(" ","")
                                                , str(mStoreProm1Price).strip().replace("$","").replace(",",".").replace(" ","")
                                                , mStoreProm1Label.strip()
                                                , str(mStoreProm2Price).strip().replace("$","").replace(",",".").replace(" ","")
                                                , mStoreProm2Label.strip()))+ "\n"


                            mFile = open(mFileName, u'a')   
                            mFile.write(mLine)
                            mFile.close

                mBackButton = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH  , "//div[contains(@class, 'contenedor-back')]"))
                )

                mBackButton.click()

                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH  , "//div[contains(@class, 'contenedor-filtro-vista')] "))
                )


            if (mTotalFound == 50):
                mPage = mPage + 1
                driver.find_element_by_xpath("//ul[contains(@class, 'pagination')]/li[last()]/a").click()
            else:
                mPage = -1


        mContinue = 0
        
    except:
        mErrCount +=1
        
        print ("Unexpected num {} error: {}".format(mErrCount, sys.exc_info()[0]))

        if (mErrCount > 200):
            mContinue = 0
        else:            
            driver.get("https://www.preciosclaros.gob.ar/#!/buscar-productos")

        continue


print("Listo")
driver.close()

