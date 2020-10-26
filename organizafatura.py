import psycopg2
import os.path
from datetime import date

########### Construct connection string
host = "localhost"
dbname = "ludfor"
user = "ludfor"
password = "Knk4xmLD"
conexao = "host={0} user={1} dbname={2} password={3}".format(host, user, dbname, password)
############

def verificafim(path):
    global conexao

    conn = psycopg2.connect(conexao)
    consulta = conn.cursor()
    consulta.execute("SELECT unidade.id FROM unidade inner join distribuidora on unidade.id_distribuidora = distribuidora.id where ccee_gestao = 1 and ambiente = 1 and fat_cpfl = 0 and distribuidora.descricao like '%RGE%' ")

    log = open(path, 'w')

    for row in consulta:
        log.write(str(row[0]) + "\n")

    log.close()
    conn.close()

    return 0

def updatefatura(tipo,id_unidade):
    global conexao

    conn = psycopg2.connect(conexao)
    insert = conn.cursor()

    if tipo == 0: # altera campo da unidade para identificar que unidade encontra-se no site da CPFL
        sql = "UPDATE unidade SET fat_cpfl = 1 WHERE id = %s"
        val = (id_unidade,)
        insert.execute(sql,val)
    else: # inicio de varedura, zera campo da tabela
        sql = "UPDATE unidade SET fat_cpfl = 0"
        insert.execute(sql)

    conn.commit()
    conn.close()

    return 0

def ambienteUnidade(id_unidade):
    global conexao
    ambiente = -1

    conn = psycopg2.connect(conexao)
    cursor = conn.cursor()
    cursor.execute("SELECT ambiente FROM unidade where unidade_consumidora = " + "'" + id_unidade + "'")

    for row in cursor:
        ambiente = row[0]
        break

    conn.close()
    return ambiente # 0 = cativo 1 = livre

def InsereUnidade(id_unidade,mes,ano):
    global conexao
    id = 0
    data_atual = date.today()

    conn = psycopg2.connect(conexao)
    consulta = conn.cursor()
    consulta.execute("SELECT id FROM unidade where unidade_consumidora = " + "'" + str(id_unidade) + "'")

    for row in consulta:
        id = row[0]
        break

    insert = conn.cursor()
    sql = "INSERT INTO fat_rge VALUES (default, %s, %s, %s, %s, %s,0)"
    val = (id,id_unidade,mes,ano,data_atual,)
    insert.execute(sql,val)
    conn.commit()
    conn.close()

def RealizaDow(id_unidade,mes,ano):
    global conexao
    result = False
    id = 0

    if ano == '0000': # algumas empresas no site ficam com o mes e ano de referencia em branco
        return False

    conn = psycopg2.connect(conexao)
    gestao = conn.cursor()

    data_filtro = (str(ano) + "-" + str(mes) + "-01")  

    print(data_filtro)

    #somente unidades que possuam gestão CCEE (ambiente livre), com distribuidra rge e rge sul e data de migração menor ou igual ao mes referencia
    sql = ("SELECT unidade.id, ccee_data_migracao FROM unidade inner join distribuidora on unidade.id_distribuidora = distribuidora.id "
        " where unidade.unidade_consumidora = '" + str(id_unidade) + "' and ccee_gestao = 1 and ambiente = 1 and distribuidora.descricao like '%RGE%' "
        " and unidade.ccee_data_migracao <= '" + data_filtro + "'") 
    gestao.execute(sql)

    for row in gestao:
        id = row[0]
        result = True
        break

    # insere na tabela unidade informação referenta a UC estar no site da CPFL, caso de ter vencido a procuração
    if id > 0:
        updatefatura(0,id)

        sql = ("SELECT unidade.id FROM fat_rge left join unidade on fat_rge.id_unidade = unidade.id where (unidade.unidade_consumidora = %s or fat_rge.unidade_consumidora = %s) and fat_rge.mes = %s and fat_rge.ano = %s ")
        val = (id_unidade,id_unidade,mes,ano,)
        consulta = conn.cursor()
        consulta.execute(sql,val)
        # verifica se o download da UC atual já não foi realizado para o mÊs e ano informado
        for row in consulta:
            result = False
            break
        
    conn.close()

    return result # True realiza download

def MontaPasta(unidade_consumidora,path,ano,mes,ano2):
    global conexao

    sql = (" SELECT empresa.descricao, unidade.nome, distribuidora.descricao, unidade.id, unidade.ambiente "
                    " FROM unidade inner join empresa on unidade.id_empresa = empresa.id "
                    " inner join distribuidora on unidade.id_distribuidora = distribuidora.id where unidade_consumidora = '" + unidade_consumidora + "'")

    conn = psycopg2.connect(conexao)
    consulta = conn.cursor()
    consulta.execute(sql)

    id_unidade = 0
    for row in consulta:
        if row[4] == 1: #ambiente livre
            path = (path + '/' + row[0] + "/" + unidade_consumidora + '_' + row[1].replace(" ","_") + '_ML/Faturas/Faturas_' + row[2] + "/Faturas_" + ano)
        else: #ambiente cativo
            path = (path + '/' + row[0] + "/" + unidade_consumidora + '_' + row[1].replace(" ","_") + '_ML/Faturas/Faturas_' + row[2] + "/Faturas_" + ano)

        arquivo_renomeado = (mes + ano2 + "_Fatura_" + row[2] + "_" + row[0].replace(" ","_") + "_" + row[1].replace(" ","_") + ".pdf")

        id_unidade = row[3]
        break

    print("-----------------organiza fatura-----------------")
    print("path:" + path)
    print("arquivo:" + arquivo_renomeado)

    if id_unidade > 0:
        if os.path.isdir(path):
            if (os.path.isfile(path + "/" + arquivo_renomeado)): # arquivo já existe na pasta
                return "1"
            else:
                return (path + "/" + arquivo_renomeado)
        else:
            print("caminho não localizado, uc não localizada!")
            return "0"
    else:
        print("caminho não localizado, uc não localizada!")
        return "0"
