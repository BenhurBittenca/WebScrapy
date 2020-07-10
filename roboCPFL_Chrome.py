from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from organizafatura import ambienteUnidade, InsereUnidade, ExisteFatura

import time
import shutil
import os
import os.path
from datetime import datetime


try:
    # ----------- Variaveis de configuração
    path_dow = r"C:\Users\benhur.bittencourt\Envs\webscrapy\Dow" #Change default directory for downloads
    path_dow2 = r"C:\Users\benhur.bittencourt\Documents\Glauber\Temp" #directory alternative
    log_status = r"C:\Users\benhur.bittencourt\Envs\WebScrapy\status.txt"
    log_cnpj = r"C:\Users\benhur.bittencourt\Envs\WebScrapy\ult_cnpj.txt"
    log = r"C:\Users\benhur.bittencourt\Envs\WebScrapy\log.txt"
    cnpj_inicial = ""

    # ----------- Verifica status do ultimo processo
    txt_status = open(log_status, 'r')
    status = txt_status.readline()
    if status == "erro":
        txt_cnpj = open(log_cnpj, 'r')
        cnpj_inicial = txt_cnpj.readline()

    txt_status = open(log, 'w') #cria arquivo de log
    txt_status = open(log_status, 'w')
    txt_status.write('em execução')
    txt_status.close()

    #----------- Diretórios
    datahora = ((datetime.now().strftime('%d-%m-%Y')) + "-" + (datetime.now().strftime('%H%M')))
    os.makedirs(path_dow2 + "/Livre/" + datahora) # cria diretório com caminho alternativo
    os.makedirs(path_dow2 + "/Cativo/" + datahora) # cria diretório com caminho alternativo
    os.makedirs(path_dow2 + "/Outros/" + datahora) # cria diretório com caminho alternativo

    # ----------- CONFIGURAÇÕES DO NAVEGADOR
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option(
    'prefs',
        {
            "download.default_directory": path_dow,
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
        }
    )

    browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
    browser.get("https://www.cpflempresas.com.br/")

    username = '010.295.140-38'
    password = 'Lud1995'

    # ----------- input usuário e senha
    print("-----------------Carregando formulário-----------------")
    browser.execute_script(f'var element = document.getElementById("ctl00_ContentPlaceHolder1_loginmenu1_txtUSUARIO"); element.value = "{username}";')
    browser.execute_script(f'var element = document.getElementById("ctl00_ContentPlaceHolder1_loginmenu1_txtSENHA"); element.value = "{password}";')

    # ----------- Logar na pagina
    print("-----------------Submit-----------------")
    element = browser.find_element_by_id('ctl00_ContentPlaceHolder1_loginmenu1_btnLOGIN')
    browser.execute_script("arguments[0].click();", element)

    # ----------- seleção de cliente
    print("-----------------seleção de cliente-----------------")
    clientes = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdBPS')
    html = clientes.get_attribute("innerHTML")
    soup = BeautifulSoup(html, "html.parser")


    cont = 0
    cnpjs = []
    for cnpjempresa in soup.find_all('span'):
        cont = (cont + 1)
        if cont == 9:
            cont = 0
            cnpj = str(cnpjempresa)
            cnpj = cnpj[27:41]
            cnpjs.append(cnpj)

    rows = -1
    for buttons in soup.find_all('img'):

        rows = (rows + 1)
        cont = 0

        txt_cnpj = open(log_cnpj, 'w')
        txt_cnpj.write(cnpjs[rows])
        txt_cnpj.close()

        if ((cnpj_inicial == cnpjs[rows] or cnpj_inicial == "") and (cnpjs[rows] != '87556650001330')): # ignora o cnpj da bertolini S.A 87556650001330
            cnpj_inicial = ""

            id = buttons.get('id')
            element = browser.find_element_by_id(id)
            browser.execute_script("arguments[0].click();", element)

            # ----------- seleção de instalação
            print("-----------------seleção de instalação-----------------")
            if len(browser.find_elements_by_id('ctl00_ContentPlaceHolder1_grdUcs')) > 0:
                unidade = browser.find_element_by_id('ctl00_ContentPlaceHolder1_lblNOME').text
                print("Unidade: " + unidade)

                instalacao = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdUcs')
                html = instalacao.get_attribute("innerHTML")
                soup_intalacao = BeautifulSoup(html, "html.parser")

                for buttons_instalacao in soup_intalacao.find_all('img'):
                    id_instalacao = buttons_instalacao.get('id')
                    element = browser.find_element_by_id(id_instalacao)
                    browser.execute_script("arguments[0].click();", element)

                    # ----------- seleção da segunda via
                    print("-----------------seleção de 2º via-----------------")
                    mes_referencia = browser.find_element_by_id('ctl00_ContentPlaceHolder1_lblMESREFERENCIA').text # mÊs de referencia para montar descrição do arquivo
                    month = mes_referencia[0:2] # ex 06
                    year = mes_referencia[5:7] # ex 20
                    year2 = mes_referencia[3:7] # ex: 2020

                    element3 = browser.find_element_by_xpath('//a[@href="consultadebito/consultadebito.aspx"]') # botão 2º via
                    browser.execute_script("arguments[0].click();", element3)

                    # ----------- seleção de fatura
                    print("-----------------seleção de fatura-----------------")
                    if len(browser.find_elements_by_id('ctl00_ContentPlaceHolder1_grdFaturas')) > 0:
                        fatura = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdFaturas') # grade de faturas
                        html = fatura.get_attribute("innerHTML")
                        soup_fatura = BeautifulSoup(html, "html.parser")

                        # busca mes e ano referencia da grade para verificar se está correto o mes_referencia
                        row = -1
                        mes_referencia2 = ""
                        element4 = browser.find_elements_by_class_name('texto14cinza')
                        for mesref in element4:
                            row = (row +1)
                            if (row == 1):
                                mes_referencia = (mesref.text)
                                month_aux = mes_referencia[5:7] # ex 06
                                break

                        if month != month_aux:
                            month = month_aux
                            year = mes_referencia[0:2] # ex 20
                            year2 = mes_referencia[0:4] # ex 2020
                            # loga unidade que tem mes de referencia disponivel antes da fatura está pronta para download
                            txt_status = open(log, 'w')
                            txt_status.write(unidade)
                            txt_status.close()

                        for buttons_fatura in soup_fatura.find_all('input'):
                            id_fatura = buttons_fatura.get('id')
                            element = browser.find_element_by_id(id_fatura)
                            browser.execute_script("arguments[0].click();", element) # marca o primeiro checkbox da grade

                            # ----------- Download
                            print("-----------------Download-----------------")

                            if os.path.exists((path_dow + "/gerarconta.aspx")): # remove arquivo caso tenha ficado de outro download
                                os.remove((path_dow + "/gerarconta.aspx"))

                            idunidade = browser.find_element_by_id('ctl00_ContentPlaceHolder1_dadoscliente1_lblINSTALACAO').text # busca unidade consumidora da empresa (id)

                            if (ExisteFatura(idunidade,month,year2) == 0): # verifica se já não foi realizado download da fatura
                                element = browser.find_element_by_id('ctl00_ContentPlaceHolder1_btnGERARFATURA') # botão download fatura
                                browser.execute_script("arguments[0].click();", element)
                                time.sleep(20)

                                ambiente = (ambienteUnidade(idunidade)) # busca pelo ambiente da unidade
                                if (ambiente == 0): #cativo
                                    print("Ambiente Cativo..")
                                    shutil.move((path_dow + "/gerarconta.aspx"),(path_dow + "/Cativo/" + str(month) + str(year) + "_" + idunidade + ".pdf"))
                                    shutil.copy((path_dow + "/Cativo/" + str(month) + str(year) + "_" + idunidade + ".pdf"), (path_dow2 + "/Cativo/" + datahora)) # move arquivo para outro diretório
                                elif (ambiente == 1): # livre
                                    print("Ambiente Livre..")
                                    shutil.move((path_dow + "/gerarconta.aspx"),(path_dow + "/Livre/" + str(month) + str(year) + "_" + idunidade + ".pdf"))
                                    shutil.copy((path_dow + "/Livre/" + str(month) + str(year) + "_" + idunidade + ".pdf"), (path_dow2 + "/Livre/" + datahora))
                                else: # não localizado, cliente não encontra-se no banco de dados
                                    print("Novo cliente..")
                                    shutil.move((path_dow + "/gerarconta.aspx"),(path_dow + "/Outros/" + str(month) + str(year) + "_" + idunidade + ".pdf"))
                                    shutil.copy((path_dow + "/Outros/" + str(month) + str(year) + "_" + idunidade + ".pdf"), (path_dow2 + "/Outros/" + datahora))

                                insere = (InsereUnidade(idunidade,month,year2)) # insere registro na tabela fat_rge para consulta de API

                                browser.switch_to.window (browser.window_handles [1]) # seleciona aba do download
                                time.sleep(5)
                                browser.close() # fecha aba download
                                browser.switch_to.window (browser.window_handles [0]) #seleciona aba principal
                            else:
                                print("Download já realizado!")

                            break # sai do laço, faz download de uma única fatura (último mês)
                    else:
                        print("Sem faturas para download")

                    # ----------- retorna para a seleção de instalação
                    print("-----------------Retorna seleção de instalação-----------------")
                    element = browser.find_element_by_id('ctl00_ContentPlaceHolder1_barranavegacao1_btnSELECIONAUC') # seleciona outro cliente
                    browser.execute_script("arguments[0].click();", element)

                # ----------- retorna para a seleção de clientes
                print("-----------------Retorna seleção de clientes-----------------")
                element = browser.find_element_by_id('ctl00_ContentPlaceHolder1_btnSELECIONAPN')
                browser.execute_script("arguments[0].click();", element)
            else:
                print("Cliente sem instalação")
                element = browser.find_element_by_id('ctl00_ContentPlaceHolder1_btnOK') # botão selecionar outro cliente
                browser.execute_script("arguments[0].click();", element)

    print("-----------------Fim de processo-----------------")

    txt_status = open(log_status, 'w')
    txt_status.write('finalizou')
    txt_status.close()
    browser.close()
except OSError as err:
    print("*************errrrrrrror*************")
    txt_status = open(log_status, 'w')
    txt_status.write('erro')
    txt_status.close()
