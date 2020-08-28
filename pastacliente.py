import pyodbc
import os.path
from datetime import date

path = r'C:\Users\benhur.bittencourt\Envs\WebScrapy\pastacliente.txt'
conexao = ('Driver={ODBC Driver 13 for SQL Server};'
                      'Server=BENHURBITTENCOU;'
                      'Database=ludfor;'
                      'Trusted_Connection=yes;')

def BuscaPasta(path,empresa,razao,uc,distribuidora,nome,ano,mes):
    # monta descrição arquivo da pasta
    empresa = str(empresa)
    distri = str(distribuidora)
    distri = (distri.replace("-", ""))
    path = (path + '/' + empresa + "/" + uc + '_' + nome.replace(" ","_") + '_ML/Faturas/Faturas_' + distri + "/Faturas_" + str(ano))

    # monta descrição arquivo
    ano = str(ano)
    if int(mes) < 10:
        mes = "0" + str(mes)
    ano = ano[2:4]

    file = format("/" + mes + ano + "_Fatura_" + distri + "_" + empresa.replace(" ","_") + "_" + nome.replace(" ","_") + ".pdf")

    existe = os.path.isfile(path + file)

    return existe

def updatefatura(uc,mes,ano):
    global conexao

    conn = pyodbc.connect(conexao)
    insert = conn.cursor()

    sql = "UPDATE fat_rge SET pastacliente = 1 WHERE unidade_consumidora = ? and mes = ? and ano = ?"
    val = (uc,mes,ano)
    insert.execute(sql,val)

    conn.commit()
    conn.close()

conn = pyodbc.connect(conexao)
consulta = conn.cursor()
consulta.execute(" SELECT empresa.descricao, unidade.razao_social, unidade.unidade_consumidora, distribuidora.descricao, unidade.nome"
                 " FROM ludfor.dbo.unidade inner join empresa on unidade.id_empresa = empresa.id "
                 " inner join distribuidora on unidade.id_distribuidora = distribuidora.id where ccee_gestao = 1 and ambiente = 1 and distribuidora.descricao like '%rge%' ")

# mes e ano atual
data_atual = str(date.today())
mes_default = int(int(data_atual[5:7]))
if mes_default == 1:
    ano_default = int(int(data_atual[:4])-1)
    mes_default = 12
else:
    ano_default = int(data_atual[:4])
    mes_default = (mes_default-1)

for row in consulta:
    existe = (BuscaPasta("//server/PUBLICO/Clientes/",row[0],row[1],row[2],row[3],row[4].strip(),ano_default,mes_default))
    if existe:
        updatefatura(row[2],mes_default,ano_default)

conn.close()
