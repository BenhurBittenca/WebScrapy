from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()  # Or Chrome(), or Ie(), or Opera()
driver.get("https://sintegre.ons.org.br/sites/9/38/Documents/images/operacao_integrada/meteorologia/global/GEFS_precipitacao14d.zip")

time.sleep(10)

username = driver.find_element_by_id("username")
password = driver.find_element_by_id("password")

username.send_keys("mesa@pluralenergia.com.br")
password.send_keys("pluralenergialudfor123*")

print("campos preenchidos")

time.sleep(10)

driver.find_element_by_name("submit.Signin").click()

print("submit")
