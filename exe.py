import subprocess

arquivo = open(r'C:\WebScrapy\status.txt', 'r')
status = arquivo.readline()

print(status)

if (status == "erro" or status == "finalizou"):
    activate_this = r'C:\Users\sistema\Envs\WebScrapy\Scripts\python'
    script_file = r"C:\WebScrapy\roboCPFL_Chrome.py"

    subprocess.Popen([activate_this, script_file])