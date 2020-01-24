from pymongo import MongoClient
from datetime import datetime
from selenium import webdriver
from tbselenium.tbdriver import TorBrowserDriver
from lxml.html import fromstring
from proxies import Proxies
import requests
import json
import logging
import random

client = MongoClient('mongodb://localhost:27017')
db = client.inapi
patentes = db.patentes
proxies = Proxies()
logging.getLogger().addHandler(logging.StreamHandler())
logging.basicConfig(level=logging.ERROR, filename='inapi.log', format='%(levelname)s | %(asctime)s: %(message)s')
logging.basicConfig(level=logging.INFO, filename='inapi.log', format='%(levelname)s | %(asctime)s: %(message)s')
logging.info('Inicia escanner')


def newDriver():
    driverLocation = "./chromedriver"
    proxy = random.choice(proxies.proxies)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    # options.add_argument('--proxy-server=' + proxy)
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    driver = webdriver.Chrome(driverLocation, options=options)
    driver.get('https://ion.inapi.cl/Patente/ConsultaAvanzadaPatentes.aspx')
    return driver, proxy


def scanCodigos(dates):
    log = 'scanCodigos(\'' + dates[0] + '\', \'' + dates[1] + '\')'
    print(log)
    driver, proxy = newDriver()
    try:
        responseCodigos = json.loads(getCodigos(driver, dates)['d'])
        codigos = list(map(lambda p: p['nrosolicitud'], responseCodigos['Patentes'])) if responseCodigos else []
        return codigos
    except Exception as e:
        print(e)
        logging.error(log)
        if not proxies.proxyOk(proxy):
            proxies.changeProxies()
        return False
    finally:
        driver.quit()


def getCodigos(driver, dates):
    return driver.execute_script('''
            var objDatos = new Object();
            var params = new Object();
            objDatos.nrosolicitud = $('#txtNroSolicitud').val();
            objDatos.titulo = $('#txtTitulo').val();
            objDatos.resumen = $('#txtResumen').val();
            objDatos.solicitante = $('#txtSolicitante').val();
            objDatos.paissolicitante = $('#txtPaisSolicitante option:selected').text();
            objDatos.inventor = $('#txtInventor').val();
            objDatos.cip = $('#txtCip').val();
            objDatos.registro = $('#txtNroRegistro').val();
            objDatos.paisprioridad = $('#txtPaisPrioridad option:selected').text();
            objDatos.nroprioridad = $('#txtNroPrioridad').val();
            objDatos.fechapresentacion1 = \'''' + dates[0] + '''\';
            objDatos.fechapresentacion2 = \'''' + dates[1] + '''\';
            objDatos.fechaprioridad1 = $('#txtFechaPrioridad1').val();
            objDatos.fechaprioridad2 = $('#txtFechaPrioridad2').val();
            objDatos.tipopatente = $('#txtTipoPatente').val();
            params.d = objDatos;
            params.Hash = htmlEncode($('#hdnHash').val());
            params.IDW = htmlEncode($('#hdnIDW').val());

            return $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: "ConsultaAvanzadaPatentes.aspx/Busqueda",
                data: JSON.stringify(params),
                dataType: "json",

                success: function (response, textStatus) {
                    return response
                }
            })
        ''')


def scanPatente(nroPatente):
    log='scanPatente(\'' + nroPatente + '\')'
    print(log)
    driver, proxy=newDriver()
    try:
        patente=json.loads(getPatente(driver, nroPatente)['d'])['Patentes']
        return patente
    except Exception as e:
        print(e)
        if not proxies.proxyOk(proxy):
            proxies.changeProxies()
        logging.error(log)
        return False
    finally:
        driver.quit()

def getPatente(driver, nroPatente):
    return driver.execute_script('''
            var params = new Object();
            params.Sol_Nro = ''' + nroPatente + ''';
            params.Ori = "1";
            params.Hash = htmlEncode($("#hdnHash").val());
            params.IDW = htmlEncode($("#hdnIDW").val());
            return $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: "ConsultaAvanzadaPatentes.aspx/GetCaratula",
                data: JSON.stringify(params),
                dataType: "json",
                async: true,
                cache: false,
                success: function (data, textStatus) {
                    return data;
                }
            })
        ''')

def saveCodigos(dates):
    codigos=scanCodigos(dates)
    for codigo in codigos:
        codigo={'_id': codigo, 'lastUpdated': datetime.utcnow()}
        log='saveCodigos(\'' + codigo['_id'] + '\')'
        print(log)
        try:
            patentes.update_one(
                {'_id': codigo['_id']},
                {'$set': codigo},
                True
            )
        except Exception as e:
            print(e)
            logging.error(log)


def savePatente(nroPatente):
    patente = scanPatente(nroPatente)
    patente['_id'] = patente['sol_nro']
    patente['lastUpdated'] = datetime.utcnow()
    log = 'savePatente(\'' + patente['_id'] + '\')'
    print(log)
    try:
        patentes.update_one(
            {'_id': patente['_id']},
            {'$set': patente},
            True
        )
    except Exception as e:
        print(e)
        logging.error(log)


def getPatentesCodes():
    return patentes.find().distinct('_id')


def getNeverScanned():
    return patentes.find({'Clasificacion': {'$ne': ''}}).distinct('_id')
