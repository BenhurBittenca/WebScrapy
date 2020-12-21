import psycopg2
import os.path
from datetime import date

########### Construct connection string
host = "192.168.78.2"
dbname = "ludfor"
user = "ludfor"
password = "Knk4xmLD"
conexao = "host={0} user={1} dbname={2} password={3}".format(host, user, dbname, password)
############

def tipodearquivo(arquivo):
    tparquivo = ''
    if "lp1" in arquivo.lower():
        tparquivo = 'LP1'
    elif "lp2" in arquivo.lower():
        tparquivo = 'LP2'
    elif "lp3" in arquivo.lower():
        tparquivo = 'LP3'
    elif "lp4" in arquivo.lower():
        tparquivo = 'LP4'
    elif "lp5" in arquivo.lower():
        tparquivo = 'LP5'
    elif "cp1" in arquivo.lower():
        tparquivo = 'CP1'
    elif "cp2" in arquivo.lower():
        tparquivo = 'CP2'
    elif "cp3" in arquivo.lower():
        tparquivo = 'CP3'
    elif "cp4" in arquivo.lower():
        tparquivo = 'CP4'
    elif "cp5" in arquivo.lower():
        tparquivo = 'CP5'     
    elif "c1" in arquivo.lower():
        tparquivo = 'C1'
    elif "c2" in arquivo.lower():
        tparquivo = 'C2'
    elif "c3" in arquivo.lower():
        tparquivo = 'C3'
    elif "c4" in arquivo.lower():
        tparquivo = 'C4'
    elif "c5" in arquivo.lower():
        tparquivo = 'C5'    
    
    return tparquivo

def inserefatunidade(path,arquivo,mes,ano,id_unidade,tipo):
    caminho_completo = ('faturas' + '/' + path + '/' + arquivo)

    sql = "SELECT ID FROM unidades_faturas WHERE caminho = %s"
    val = (caminho_completo,)
    conn2 = psycopg2.connect(conexao)
    consulta2 = conn2.cursor()
    consulta2.execute(sql,val)

    existe = False
    for row2 in consulta2:
        existe = True
        break
    
    conn2.close()

    if not existe:
        tparquivo = tipodearquivo(arquivo)

        sql = "INSERT INTO unidades_faturas VALUES (default,%s, %s, %s, %s, %s, %s)"
        val = (mes,ano,caminho_completo,tipo,tparquivo,id_unidade,)

        conn2 = psycopg2.connect(conexao)
        insert = conn2.cursor()
        insert.execute(sql,val)
        conn2.commit()
        conn2.close()

def verificafim(path):
    global conexao

    data_atual = str(date.today())

    conn = psycopg2.connect(conexao)
    consulta = conn.cursor()
    consulta.execute("SELECT unidade.id FROM unidades_consumidoras as uc "        
        " inner join distribuidora on uc.id_distribuidora = distribuidora.id "
        " inner join modalidade on uc.id_modalidade = modalidade.id "
        #" where distribuidora.descricao_ludfor like '%RGE%' and fat_cpfl = 0 and ((ambiente = 1 and ccee_gestao = 1 and unidade.ccee_data_migracao <= '" + data_atual + "')"
        " where distribuidora.descricao_ludfor like '%RGE%' and fat_cpfl = 0 and ((ambiente = 1 and ccee_gestao = 1)"
        " or (ambiente = 0 and modalidade.descricao <> 'Baixa tensão' and id_empresa <> 514))")

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
        sql = "UPDATE unidades_consumidoras SET fat_cpfl = 1 WHERE id = %s"
        val = (id_unidade,)
        insert.execute(sql,val)
    else: # inicio de varedura, zera campo da tabela
        sql = "UPDATE unidades_consumidoras SET fat_cpfl = 0"
        insert.execute(sql)

    conn.commit()
    conn.close()

    return 0

def ambienteUnidade(id_unidade):
    global conexao
    ambiente = -1

    conn = psycopg2.connect(conexao)
    cursor = conn.cursor()
    cursor.execute("SELECT ambiente FROM unidades_consumidoras where unidade_consumidora = " + "'" + id_unidade + "'")

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
    consulta.execute("SELECT id FROM unidades_consumidoras where unidade_consumidora = " + "'" + str(id_unidade) + "'")

    for row in consulta:
        id = row[0]
        break

    insert = conn.cursor()
    sql = "INSERT INTO fat_rge VALUES (default, %s, %s, %s, %s, 0, %s)"
    val = (id_unidade,mes,ano,data_atual,id,)
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

    #somente unidades livre (com gestão CCEE) ou cativo (menos baixa tensão), com distribuidra rge e rge sul e data de migração menor ou igual ao mes referencia (se ambiente livre)
    sql = ("SELECT uc.id, uc.ambiente FROM unidade "
        " inner join unidades_consumidoras as uc on uc.id_unidade = unidade.id "
        " inner join distribuidora on uc.id_distribuidora = distribuidora.id "
        " inner join modalidade on uc.id_modalidade = modalidade.id "
        #" where uc.unidade_consumidora = '" + str(id_unidade) + "' and ((ambiente = 1 and ccee_gestao = 1 and uc.ccee_data_migracao <= '" + data_filtro + "')" 
        " where uc.unidade_consumidora = '" + str(id_unidade) + "' and ((ambiente = 1 and ccee_gestao = 1)" 
        " or (ambiente = 0 and modalidade.descricao <> 'Baixa tensão')) and distribuidora.descricao_ludfor like '%RGE%' ")       
    gestao.execute(sql)

    for row in gestao:
        print("ambiente: " + str(row[1]))    
        id = row[0]
        result = True
        break

    print(result)

    # insere na tabela unidade informação referenta a UC estar no site da CPFL, caso de ter vencido a procuração
    if id > 0:
        updatefatura(0,id)

        sql = ("SELECT uc.id FROM fat_rge left join unidades_consumidoras as uc on fat_rge.id_unidade_consumidora = uc.id where (uc.unidade_consumidora = %s or fat_rge.unidade_consumidora = %s) and fat_rge.mes = %s and fat_rge.ano = %s ")
        val = (id_unidade,id_unidade,mes,ano,)
        consulta = conn.cursor()
        consulta.execute(sql,val)
        # verifica se o download da UC atual já não foi realizado para o mÊs e ano informado
        for row in consulta:
            result = False
            break

        print(result)
        
    conn.close()

    return result # True realiza download

def MontaPasta(unidade_consumidora,path,path2,ano,mes,ano2):
    global conexao

    sql = (" SELECT empresa.descricao, unidade.nome, distribuidora.descricao_ludfor, uc.id, uc.ambiente "
                    " FROM unidade inner join empresa on unidade.id_empresa = empresa.id inner join unidades_consumidoras as uc on uc.id_unidade = unidade.id "
                    " inner join distribuidora on UC.id_distribuidora = distribuidora.id where unidade_consumidora = '" + unidade_consumidora + "'")

    conn = psycopg2.connect(conexao)
    consulta = conn.cursor()
    consulta.execute(sql)

    id_unidade = 0
    for row in consulta:
        caminho = ''
        arquivo = ''

        if row[4] == 1: #ambiente livre
            path = (path + '/' + row[0] + "/" + unidade_consumidora + '_' + row[1].replace(" ","_") + '_ML/Faturas/Faturas_' + row[2] + "/Faturas_" + ano)
            caminho = (row[0] + "/" + unidade_consumidora + '_' + row[1].replace(" ","_") + '_ML/Faturas/Faturas_' + row[2] + "/Faturas_" + ano)
        else: #ambiente cativo
            path = (path + '/' + row[0] + "/" + unidade_consumidora + '_' + row[1].replace(" ","_") + '/Faturas/Faturas_' + row[2] + "/Faturas_" + ano)
            caminho = (row[0] + "/" + unidade_consumidora + '_' + row[1].replace(" ","_") + '/Faturas/Faturas_' + row[2] + "/Faturas_" + ano)

        arquivo_renomeado = (mes + ano2 + "_Fatura_" + row[2] + "_" + row[0].replace(" ","_") + "_" + row[1].replace(" ","_") + ".pdf")

        id_unidade = row[3]
        break

    print("-----------------organiza fatura-----------------")
    print("path: " + path)
    print("arquivo: " + arquivo_renomeado)    

    if id_unidade > 0:
        if os.path.isdir(path):
            if (os.path.isfile(path + "/" + arquivo_renomeado)): # arquivo já existe na pasta
                return ("1","")                
            else:
                inserefatunidade(caminho,arquivo_renomeado,mes,ano,id_unidade,0)
                if not(os.path.isdir(path2 + "/" + caminho)):
                    print("Pasta servidor 2Cloud não localizada, criando!")
                    os.makedirs((path2 + "/" + caminho))
                
                return ((path + "/" + arquivo_renomeado), (path2 + "/" + caminho + "/" + arquivo_renomeado))
        else:
            print("caminho não localizado, uc não localizada!")
            return ("0","")
    else:
        print("Uc não localizada!")
        return ("0","")

