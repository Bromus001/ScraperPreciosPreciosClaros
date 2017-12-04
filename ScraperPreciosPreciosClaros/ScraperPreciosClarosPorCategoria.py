from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
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

#cordoba rosario mendoza ushuaia tucuman bariloche salta la_plata
mLocation = sys.argv[1]
mCategoryId = sys.argv[2]

print('Location is {}'.format(mLocation))
print('Category is {}'.format(mCategoryId))

driver = webdriver.Chrome(executable_path='C:\Bromus\Software\chromedriver.exe')
#driver = webdriver.Edge(executable_path='C:\Bromus\Software\MicrosoftWebDriver.exe')

driver.get("https://www.preciosclaros.gob.ar/#!/buscar-productos")

mLocalizationButton = driver.find_element_by_id(mLocation)

#driver.execute_script("arguments[0].click();", mLocalizationButton)

mLocalizationButton.click()

print ("Iniciando navegacion al sitio ...")
    

mInput = WebDriverWait(driver, 15).until(
    EC.visibility_of_element_located((By.XPATH  , "//input[contains(@class, 'do-hide-menu-on-click')] "))
)

sleep(10)
                
print ("procesando categoria {}".format(mCategoryId))        

mCategories=[]
mErrCount = 0

while (len(mCategories)==0):
    mCategories = driver.find_elements_by_xpath("//div[contains(@class, 'buscador-categorias')]/div")

    if (len(mCategories) < 9):
        print("Error detectando categoria, reintentando")
        mErrCount+=1
        if (mErrCount>5):
            print("No se pudo acceder a la categoria.")
            sys.exit()

        sleep(3)
    
mCategory = mCategories[int(mCategoryId)] #.find_element_by_xpath(".//div[@class='item-categoria']")

driver.execute_script("arguments[0].click();", mCategory)


mFoundProducts = []
mProducts = []
       
mFileName = os.path.join(mRootFolder, 'data/precios_claros_precios_' + mLocation + '_' + mCategoryId + '_' +  datetime.now().strftime("%Y%m%d-%H%M%S") + '.txt')

mMaxPageScraped = -1

WebDriverWait(driver, 15).until(
    EC.visibility_of_element_located((By.XPATH  , "//div[contains(@class, 'contenedor-filtro-vista')] "))
)

mLastPageNumber = driver.find_element_by_xpath("//ul[contains(@class, 'pagination')]/li[last()-1]/a").get_attribute("innerText")
            
mCurrentPageNumber = driver.find_element_by_xpath("//ul[contains(@class, 'pagination')]/li[contains(@class, 'active')]/a").get_attribute("innerText")
        

while (int(mCurrentPageNumber) <= int(mLastPageNumber)):

    try:

        print("======================================")
        print("Inicia proceso Pagina {} de {} ".format(mCurrentPageNumber,mLastPageNumber))
        print("======================================")
        
        mTotalProductsDiv = driver.find_elements_by_xpath("//div[(contains(@class, 'producto')) and not (contains(@class, 'no-agrupable'))]/div[contains(@class, 'caja-producto-mosaico')]")

        mTotalFound = len(mTotalProductsDiv)
    
        mRepeatedCount = 0

        print ("Encontrados {} productos".format(mTotalFound))
        
        #mTotalFound = 2

        for mIndex in range(0, mTotalFound):

            print("Categoria {} Pagina {} de {} Producto {} de {}".format(mCategoryId, mCurrentPageNumber,mLastPageNumber, mIndex + 1, mTotalFound))

            try:

                sleep(2)
                mProductDiv = mTotalProductsDiv[mIndex]
                #mProductDiv = driver.find_elements_by_xpath("//div[@class= 'caja-producto-mosaico'][1]")[mIndex]        

                mDetailButton = mProductDiv.find_element_by_xpath(".//div[contains(@class, 'nombre-producto')]")
                
                mProductName = mProductDiv.find_element_by_xpath(".//div[contains(@class, 'nombre-producto') and contains(@class, 'ng-binding')]").get_attribute("innerText")
                mProductImageUrl = mProductDiv.find_element_by_xpath(".//div[@class='contenedor-imagen']/img").get_attribute("src")
                mProductSku = mProductDiv.find_element_by_xpath(".//div[contains(@class, 'ean') and contains(@class, 'ng-binding')]").get_attribute("innerText")

                mFoundProducts.append(mProductSku)

                if (mProductSku in mAlreadyProcessed):
                    print("Producto {} ya procesado".format(mProductName))
                    mRepeatedCount+=1
                    continue
                else:
                    mAlreadyProcessed[mProductSku] = mProductName

                print("Procesando producto " + mProductName.strip())

                driver.execute_script("arguments[0].click();", mDetailButton)


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
                            mStoreLocation = mLocation
                            #mStoreDistance = mStoreRow.find_element_by_xpath(".//td[contains(@class, 'detalle-distancia')]").get_attribute("innerText")
                            mStoreListPrice = mStoreRow.find_element_by_xpath(".//span[contains(@class, 'precio-lista')]").get_attribute("innerText")
                            mStoreProm1Price = mStoreRow.find_element_by_xpath(".//span[contains(@class, 'precio-promo-1')]/span").get_attribute("innerText")
                            mStoreProm1Label = mStoreRow.find_element_by_xpath(".//span[contains(@class, 'precio-promo-1')]/span").get_attribute("title")
                            mStoreProm2Price = mStoreRow.find_element_by_xpath(".//span[contains(@class, 'precio-promo-2')]/span").get_attribute("innerText")
                            mStoreProm2Label = mStoreRow.find_element_by_xpath(".//span[contains(@class, 'precio-promo-2')]/span").get_attribute("title")      
                            #mStoreImage = mStoreRow.find_element_by_xpath(".//div[@class = 'contenedor-imagen']/img").get_attribute("src") 

                            mLine = '|'.join((mProductSku
                                                , mProductName.strip()
                                                , mProductImageUrl.strip()
                                                , mStoreName.strip()
                                                , mStoreAddress.strip()
                                                , mStoreCity.strip()
                                                , mStoreLocation.strip()
                                                , str(mStoreListPrice).strip().replace("$","").replace(",",".").replace(" ","")
                                                , str(mStoreProm1Price).strip().replace("$","").replace(",",".").replace(" ","")
                                                , mStoreProm1Label.strip()
                                                , str(mStoreProm2Price).strip().replace("$","").replace(",",".").replace(" ","")
                                                , mStoreProm2Label.strip()
                                                , mCategoryId.strip()))+ "\n"


                            mFile = open(mFileName, u'a')   
                            mFile.write(mLine)
                            mFile.close


                driver.execute_script("window.history.go(-1)")
                    
                WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.XPATH  , "//div[contains(@class, 'contenedor-filtro-vista')] "))
                )

            except:
                mErrCount +=1
                print("*****************************************")
                print("Error procesando producto {} de {}".format( mIndex + 1, mTotalFound))
                print ("Unexpected num {} error: {}".format(mErrCount, sys.exc_info()[0]))
                print("*****************************************")

                mCurrentPageNumber = mCurrentPageNumber - 1
                driver.execute_script("window.history.go(-1)")

                sleep(5)

                break

        # Fin Iteracion pagina

        print("Finalizada pagina {} de {}".format(mCurrentPageNumber, mLastPageNumber))
        print("======================================")
        print("")

        if (mCurrentPageNumber == mLastPageNumber):
            exit

        mNextPageButton = driver.find_element_by_xpath("//ul[contains(@class, 'pagination')]/li[last()]/a")    

        driver.execute_script("arguments[0].click();", mNextPageButton)

        sleep(10)

        mErrCount = 0
        mPage = mCurrentPageNumber
        while (mPage == mCurrentPageNumber):
            try:
                WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.XPATH  , "//div[contains(@class, 'contenedor-filtro-vista')] "))
                )

                mLastPageNumber = driver.find_element_by_xpath("//ul[contains(@class, 'pagination')]/li[last()-1]/a").get_attribute("innerText")
            
                mCurrentPageNumber = driver.find_element_by_xpath("//ul[contains(@class, 'pagination')]/li[contains(@class, 'active')]/a").get_attribute("innerText")
            except:
                print("Error intentando avanzar de pagina")
                sleep(3)
                mErrCount+=1
                if (mErrCount>5):
                    sys.exit()
                else:
                    continue
    
    except:
        mErrCount +=1
        print("*****************************************")
        print("Error procesando pagina {} de {}".format(mCurrentPageNumber, mLastPageNumber))
        print ("Unexpected num {} error: {}".format(mErrCount, sys.exc_info()[0]))
        print("*****************************************")

        continue

print("======================================")
print("======================================")
print("Finaliza proceso Pagina {} de {} ".format(mCurrentPageNumber,mLastPageNumber))
print("======================================")
print("======================================")

print("Listo")
driver.close()

