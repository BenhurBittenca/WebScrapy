from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import time

# ----------- CONFIGURAÇÕES DO NAVEGADOR
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList",2)
profile.set_preference("browser.download.manager.showWhenStarting",False)
profile.set_preference("browser.download.dir", r"C:\Users\benhur.bittencourt\Envs\webscrapy\Dow")
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
profile.set_preference("pdfjs.disabled", True)
profile.set_preference("plugin.scan.Acrobat", "99.0");
profile.set_preference("plugin.scan.plid.all", False);
profile.set_preference("browser.helperApps.alwaysAsk.force", False);

browser = webdriver.Firefox(firefox_profile=profile)

browser.get("https://www.cpflempresas.com.br/")
time.sleep(5)

username = '010.295.140-38'
password = 'Lud1995'

# ----------- input usuário e senha
browser.execute_script(f'var element = document.getElementById("ctl00_ContentPlaceHolder1_loginmenu1_txtUSUARIO"); element.value = "{username}";')
browser.execute_script(f'var element = document.getElementById("ctl00_ContentPlaceHolder1_loginmenu1_txtSENHA"); element.value = "{password}";')
print("-----------------Carregando formulário-----------------")
time.sleep(5)
# ----------- Logar na pagina
element = browser.find_element_by_id('ctl00_ContentPlaceHolder1_loginmenu1_btnLOGIN')
browser.execute_script("arguments[0].click();", element)
print("-----------------Submit-----------------")
time.sleep(5)
# ----------- seleção de cliente
element1 = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdBPS_ctl03_imgExcluir')
browser.execute_script("arguments[0].click();", element1)
print("-----------------Seleção da cliente-----------------")
time.sleep(5)
# ----------- seleção de instalação
element2 = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdUcs_ctl02_imgSelecionar')
browser.execute_script("arguments[0].click();", element2)
print("-----------------Seleção da instalação-----------------")
time.sleep(15)
# ----------- seleção da segunda via
element3 = browser.find_element_by_xpath('//a[@href="consultadebito/consultadebito.aspx"]')
browser.execute_script("arguments[0].click();", element3)
print("-----------------Seleção segunda via-----------------")
time.sleep(5)
# ----------- seleção de fatura
element4 = browser.find_element_by_id('ctl00_ContentPlaceHolder1_grdFaturas_ctl02_rbIDFAT')
browser.execute_script("arguments[0].click();", element4)
print("-----------------Seleção de fatuera-----------------")
time.sleep(5)
# ----------- Download
element5 = browser.find_element_by_id('ctl00_ContentPlaceHolder1_btnGERARFATURA')
browser.execute_script("arguments[0].click();", element5)
print("-----------------Download-----------------")
time.sleep(10)
browser.quit()
