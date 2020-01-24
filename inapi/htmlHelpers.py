from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def deleteElement(xpath, driver):
    element = driver.find_element_by_xpath(xpath)
    driver.execute_script("""
    var element = arguments[0];
    element.parentNode.removeChild(element);
    """, element)

def textifyElements(elements):
    texts = ''
    if len(elements) == 1:
        texts = elements[0].text
    else:
        for element in elements:
            texts += (element.text) + " "
    return texts

def newDriver():
    binaryLocation = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    driverLocation = "./chromedriver"
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1066,2000")
    options.binary_location = binaryLocation
    return webdriver.Chrome(driverLocation, options=options)

def displayElement(driver, element):
    driver.execute_script("arguments[0].style = '';", element) 

def waitLoading(driver):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="loadingImg"]')))

class SearchWindow:
    def __init__(self):
        self.driver = newDriver()
        self.driver.get('https://ion.inapi.cl/Patente/ConsultaAvanzadaPatentes.aspx')
        self.btnBuscar = self.driver.find_element_by_xpath('//*[@id="BtnBuscar"]')
        self.tBoxFechaInicio = self.driver.find_element_by_xpath('//*[@id="txtFechaPresentacion1"]')
        self.tBoxFechaFin = self.driver.find_element_by_xpath('//*[@id="txtFechaPresentacion2"]')
        deleteElement('/html/body/div[5]/header', self.driver)
        deleteElement('/html/body/div[5]/div[3]', self.driver)