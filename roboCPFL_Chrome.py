from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from organizafatura import ambienteUnidade, InsereUnidade, updatefatura, RealizaDow, verificafim, MontaPasta

import time
import shutil
import os
import os.path
from datetime import datetime

# ----------- Variaveis de configuração
path_default = r"C:\Users\benhur.bittencourt\Envs\WebScrapy"
path_dow2 = r"\\server\PUBLICO\Clientes" #directory alternative
path_copy = r'\\192.168.78.3\clientes\Ludfor\mainapp\static\faturas' #pasta de upload do site
path_2Cloud = r"\\192.168.78.3\temp\Log_Robo"

path_dow = (path_default + r"\Dow") #Change default directory for downloads
log_status = (path_default + r"\status.txt")
log_cnpj = (path_default + r"\ult_cnpj.txt")
log_contador = (path_default + r"\contador.txt")
log_ucnaoencontrada = (path_default + r"\uc_lost.txt")
log = (path_default + r"\log.txt")
cnpj_inicial = ""

# ----------- Log
log_conteudo = open(log, 'r') # lê conteudo do log
conteudo = log_conteudo.read() #salva conteudo existente
log_conteudo = open(log, 'w')
datahora = ((datetime.now().strftime('%d-%m-%Y')) + "-" + (datetime.now().strftime('%H%M')))
log_conteudo.write("******************ROBÔ CPFL/" + datahora + "******************\n")

try:
    # ----------- Verifica status do ultimo processo
    txt_status = open(log_status, 'r')
    status = txt_status.readline()
    if status == "finalizou":
        updatefatura(1,0) # limpa campos de referencia das unidades
    elif status == "erro":
        txt_cnpj = open(log_cnpj, 'r')
        cnpj_inicial = txt_cnpj.readline()

    txt_status = open(log_status, 'w')
    txt_status.write('em execução')
    txt_status.close()
    shutil.copy(log_status, path_2Cloud) # copia log para pasta TEMP da 2Cloud

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
    password = 'lud321'

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

        if ((cnpj_inicial == cnpjs[rows] or cnpj_inicial == "") and (cnpjs[rows] != '87556650001330')): # ignora o cnpj da bertolini S.A 87556650001330
            txt_contador = open(log_contador, 'w')
            txt_contador.write(format(rows) + '-' + format(len(soup.find_all('img'))))
            txt_contador.close()

            txt_cnpj = open(log_cnpj, 'w')
            txt_cnpj.write(cnpjs[rows])
            txt_cnpj.close()

            cnpj_inicial = ""

            id = buttons.get('id')
            element = browser.find_element_by_id(id)
            browser.execute_script("arguments[0].click();", element)

            # ----------- seleção de instalação
            print("-----------------seleção de instalação-----------------")
            if len(browser.find_elements_by_id('ctl00_ContentPlaceHolder1_grdUcs')) > 0:
                unidade = browser.find_element_by_id('ctl00_ContentPlaceHolder1_lblNOME').text
            
                log_conteudo.write("--------------------------------------------------------------\n")
                log_conteudo.write("Unidade: " + unidade + "\n")
                print("Unidade: " + unidade)

                instalacao = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdUcs')
                html = instalacao.get_attribute("innerHTML")
                soup_intalacao = BeautifulSoup(html, "html.parser")

                for buttons_instalacao in soup_intalacao.find_all('img'):
                    print("-----------------instalação-----------------")

                    id_instalacao = buttons_instalacao.get('id')
                    element = browser.find_element_by_id(id_instalacao)
                    browser.execute_script("arguments[0].click();", element)

                    idunidade = browser.find_element_by_id('ctl00_ContentPlaceHolder1_dadoscliente1_lblINSTALACAO').text # busca unidade consumidora da empresa (id)
                    mes_referencia = browser.find_element_by_id('ctl00_ContentPlaceHolder1_lblMESREFERENCIA').text # mÊs de referencia para montar descrição do arquivo
                    month = mes_referencia[0:2] # ex 06
                    year = mes_referencia[5:7] # ex 20
                    year2 = mes_referencia[3:7] # ex: 2020

                    log_conteudo.write("UC: " + idunidade + "\n")
                    print("UC:" + idunidade)

                    if (RealizaDow(idunidade,month,year2)): # verifica se UC é de uma unidade LIVRE OU CATIVO, GESTÃO CCEE SIM (SE LIVRE), RGE ou RGE-SUL
                        # ----------- seleção da segunda via
                        print("-----------------seleção de 2º via-----------------")
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

                            log_conteudo.write("Referência: " + month + "-" + year + "\n")                                            

                            for buttons_fatura in soup_fatura.find_all('input'):
                                id_fatura = buttons_fatura.get('id')
                                element = browser.find_element_by_id(id_fatura)
                                browser.execute_script("arguments[0].click();", element) # marca o primeiro checkbox da grade

                                # ----------- Download
                                print("-----------------Download-----------------")

                                if os.path.exists((path_dow + r"\gerarconta.aspx")): # remove arquivo caso tenha ficado de outro download
                                    os.remove((path_dow + r"\gerarconta.aspx"))

                                element = browser.find_element_by_id('ctl00_ContentPlaceHolder1_btnGERARFATURA') # botão download fatura
                                browser.execute_script("arguments[0].click();", element)
                                time.sleep(20)

                                arquivo = (path_dow + "/" + str(month) + str(year) + "_" + idunidade + ".pdf")
                                caminho_cliente, path_copy = (MontaPasta(idunidade,path_dow2,path_copy,year2,month,year))

                                print("Caminho do Cliente:" + caminho_cliente)

                                if caminho_cliente == '0':
                                    shutil.move((path_dow + r"\gerarconta.aspx"),arquivo)
                                    shutil.copy(arquivo, (path_dow + "/Pastanaolocalizada"))
                                    log_conteudo.write("Pasta do cliente não localizada!\n")
                                elif caminho_cliente == '1':
                                    shutil.move((path_dow + r"\gerarconta.aspx"),arquivo)
                                    shutil.copy(arquivo, (path_dow + "/Arquivojaexistente"))                                    
                                    log_conteudo.write("Arquivo já encontra-se na pasta!\n")
                                else:
                                    shutil.move((path_dow + r"\gerarconta.aspx"),arquivo)
                                    shutil.copy(arquivo, caminho_cliente)
                                    shutil.copy(caminho_cliente, path_copy)

                                    log_conteudo.write("Arquivo movido para: " + caminho_cliente + "\n")
                                
                                print(caminho_cliente)
                                print(path_copy)
                                input("aguarde!!")

                                insere = (InsereUnidade(idunidade,month,year2)) # insere registro na tabela fat_rge para consulta de API

                                browser.switch_to.window (browser.window_handles [1]) # seleciona aba do download
                                time.sleep(5)
                                browser.close() # fecha aba download
                                browser.switch_to.window (browser.window_handles [0]) #seleciona aba principal

                                break # sai do laço, faz download de uma única fatura (último mês)
                        else:
                            log_conteudo.write("Sem faturas para download\n")
                            print("Sem faturas para download")

                        # ----------- retorna para a seleção de instalação
                        print("-----------------Retorna seleção de instalação-----------------")
                        element = browser.find_element_by_id('ctl00_ContentPlaceHolder1_barranavegacao1_btnSELECIONAUC') # seleciona outro cliente
                        browser.execute_script("arguments[0].click();", element)

                    else:
                        log_conteudo.write("Não realiza Downaload\n")

                        print("Não realiza download")
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

            # copia log para pasta TEMP da 2Cloud
            shutil.copy(log_contador, path_2Cloud)         
            shutil.copy(log, path_2Cloud)       

    print("-----------------Fim de processo-----------------")

    txt_status = open(log_status, 'w')
    txt_status.write('finalizou')
    txt_status.close()

    log_conteudo.write(str(conteudo)) # apenda conteúdo do log já existente
    log_conteudo.close()

    # copia log para pasta TEMP da 2Cloud
    shutil.copy(log_status, path_2Cloud) 
    shutil.copy(log_contador, path_2Cloud)         
    shutil.copy(log, path_2Cloud)

    browser.close()
    (verificafim(log_ucnaoencontrada)) # armazena em um txt as uc da lista de download que NÃO foram encontradas no site (procuração vencida)
    shutil.copy(log_ucnaoencontrada, path_2Cloud)
except Exception as e:
    print("*************errrrrrrror*************")
    txt_status = open(log_status, 'w')
    txt_status.write('erro')
    txt_status.close()

    log_conteudo.write("*************error*************\n")
    log_conteudo.write(str(e) + "\n")
    log_conteudo.write(str(conteudo)) # apenda conteúdo do log já existente
    log_conteudo.close()

    # copia log para pasta TEMP da 2Cloud
    shutil.copy(log_status, path_2Cloud) 
    shutil.copy(log_contador, path_2Cloud)         
    shutil.copy(log, path_2Cloud)
