from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# ----------- CONFIGURAÇÕES DO NAVEGADOR
options = webdriver.ChromeOptions()
options.add_experimental_option(
    'prefs',
        {
            "download.default_directory": r"C:\Users\benhur.bittencourt\Envs\webscrapy\Dow", #Change default directory for downloads
            "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
        }
    )

browser = webdriver.Chrome(chrome_options=options)
browser.get("https://www.cpflempresas.com.br/")

username = '010.295.140-38'
password = 'Lud1995'

# ----------- input usuário e senha
browser.execute_script(f'var element = document.getElementById("ctl00_ContentPlaceHolder1_loginmenu1_txtUSUARIO"); element.value = "{username}";')
browser.execute_script(f'var element = document.getElementById("ctl00_ContentPlaceHolder1_loginmenu1_txtSENHA"); element.value = "{password}";')
print("-----------------Carregando formulário-----------------")
# ----------- Logar na pagina
element = browser.find_element_by_id('ctl00_ContentPlaceHolder1_loginmenu1_btnLOGIN')
browser.execute_script("arguments[0].click();", element)
print("-----------------Submit-----------------")
# ----------- seleção de cliente
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
