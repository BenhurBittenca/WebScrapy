from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import os
import os.path

# ----------- Variaveis de configuração
path_dow = r"C:\Users\benhur.bittencourt\Envs\webscrapy\Dow" #Change default directory for downloads
txt = open('Error.txt', 'w')

# ----------- Limpa arquivo padrão caso exista na pasta

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

for buttons in soup.find_all('img'):

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
            month = mes_referencia[0:2]
            year = mes_referencia[5:7]
            element3 = browser.find_element_by_xpath('//a[@href="consultadebito/consultadebito.aspx"]') # botão 2º via
            browser.execute_script("arguments[0].click();", element3)


            # ----------- seleção de fatura
            print("-----------------seleção de fatura-----------------")
            if len(browser.find_elements_by_id('ctl00_ContentPlaceHolder1_grdFaturas')) > 0:
                fatura = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdFaturas') # grade de faturas
                html = fatura.get_attribute("innerHTML")
                soup_fatura = BeautifulSoup(html, "html.parser")

                for buttons_fatura in soup_fatura.find_all('input'):
                    id_fatura = buttons_fatura.get('id')
                    element = browser.find_element_by_id(id_fatura)
                    browser.execute_script("arguments[0].click();", element)

                    try:
                        # ----------- Download
                        print("-----------------Download-----------------")

                        if os.path.exists((path_dow + "/gerarconta.aspx")): # remove arquivo caso tenha ficado de outro download
                            os.remove((path_dow + "/gerarconta.aspx"))

                        idunidade = browser.find_element_by_id('ctl00_ContentPlaceHolder1_dadoscliente1_lblINSTALACAO').text # busca unidade consumidora da empresa (id)
                        element = browser.find_element_by_id('ctl00_ContentPlaceHolder1_btnGERARFATURA') # botão download fatura

                        browser.execute_script("arguments[0].click();", element)
                        time.sleep(20)
                        os.rename((path_dow + "/gerarconta.aspx"),(path_dow + "/" + str(month) + str(year) + "_" + idunidade + ".pdf")) # renomeia arquivo
                    except:
                        txt.write('Download Erro! Unidade: ' + unidade + "\n")
                        print("**Erro download**")

                    browser.switch_to.window (browser.window_handles [1]) # seleciona aba do download
                    time.sleep(5)
                    browser.close() # fecha aba download
                    browser.switch_to.window (browser.window_handles [0]) #seleciona aba principal
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
txt.close()
browser.close()

'''
element1 = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdBPS_ctl03_imgExcluir')
browser.execute_script("arguments[0].click();", element1)
print("-----------------Seleção da cliente-----------------")
# ----------- seleção de instalação
element2 = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdUcs_ctl02_imgSelecionar')
browser.execute_script("arguments[0].click();", element2)
print("-----------------Seleção da instalação-----------------")
# ----------- seleção da segunda via
element3 = browser.find_element_by_xpath('//a[@href="consultadebito/consultadebito.aspx"]')
browser.execute_script("arguments[0].click();", element3)
print("-----------------Seleção segunda via-----------------")
# ----------- seleção de fatura
element4 = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdFaturas_ctl02_rbIDFAT')
browser.execute_script("arguments[0].click();", element4)
print("-----------------Seleção de fatuera-----------------")
# ----------- Download
element5 = browser.find_element_by_id('ctl00_ContentPlaceHolder1_btnGERARFATURA')
browser.execute_script("arguments[0].click();", element5)
print("-----------------Download-----------------")
time.sleep(10)
browser.quit()
'''
