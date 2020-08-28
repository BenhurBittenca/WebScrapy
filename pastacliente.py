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

def updatefatura(uc,mes,ano,id,download):
    data_atual = str(date.today())
    global conexao

    conn = pyodbc.connect(conexao)
    insert = conn.cursor()

    if download == 9: # quando fatura foi baixada de forma manual e colocada na pasta do cliente
        sql = "INSERT INTO fat_rge VALUES (?, ?, ?, ?, ?,1)"
        val = (id,uc,mes,ano,data_atual)
    else:
        sql = "UPDATE fat_rge SET pastacliente = 1 WHERE unidade_consumidora = ? and mes = ? and ano = ?"
        val = (uc,mes,ano)

    insert.execute(sql,val)
    conn.commit()
    conn.close()

###############################################

# mes e ano atual
data_atual = str(date.today())
mes_default = int(int(data_atual[5:7]))
if mes_default == 1:
    ano_default = int(int(data_atual[:4])-1)
    mes_default = 12
else:
    ano_default = int(data_atual[:4])
    mes_default = (mes_default-1)

conn = pyodbc.connect(conexao)
consulta = conn.cursor()
sql = (" SELECT empresa.descricao, unidade.razao_social, unidade.unidade_consumidora, distribuidora.descricao, unidade.nome, unidade.id, "
                 " isnull((select pastacliente from fat_rge where unidade.id = fat_rge.id_unidade and fat_rge.mes = ? and fat_rge.ano = ?),9)"
                 " FROM ludfor.dbo.unidade inner join empresa on unidade.id_empresa = empresa.id "
                 " inner join distribuidora on unidade.id_distribuidora = distribuidora.id where ccee_gestao = 1 and ambiente = 1 and distribuidora.descricao like '%rge%' ")
val = (mes_default,ano_default)

consulta.execute(sql,val)

for row in consulta:
    existe = (BuscaPasta("//server/PUBLICO/Clientes/",row[0],row[1],row[2],row[3],row[4].strip(),ano_default,mes_default))
    if row[2] == '3081326661':
        print(existe)
    if existe:
        updatefatura(row[2],mes_default,ano_default,row[5],row[6])

conn.close()
