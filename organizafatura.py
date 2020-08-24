import pyodbc
from datetime import date

conexao = ('Driver={ODBC Driver 13 for SQL Server};'
                      'Server=BENHURBITTENCOU;'
                      'Database=ludfor;'
                      'Trusted_Connection=yes;')

def verificafim(path):
    global conexao

    conn = pyodbc.connect(conexao)
    consulta = conn.cursor()
    consulta.execute("SELECT unidade.id FROM ludfor.dbo.unidade inner join distribuidora on unidade.id_distribuidora = distribuidora.id where ccee_gestao = 1 and ambiente = 1 and fat_cpfl = 0 and distribuidora.descricao like '%rge%' ")

    log = open(path, 'w')

    for row in consulta:
        log.write(str(row[0]) + "\n")        

    log.close()
    conn.close()

    return 0

def updatefatura(tipo,id_unidade):
    global conexao

    conn = pyodbc.connect(conexao)
    insert = conn.cursor()

    if tipo == 0: # altera campo da unidade para identificar que unidade encontra-se no site da CPFL
        sql = "UPDATE unidade SET fat_cpfl = 1 WHERE id = ?"
        val = (id_unidade)
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

    conn = pyodbc.connect(conexao)
    cursor = conn.cursor()
    cursor.execute("SELECT ambiente FROM ludfor.dbo.unidade where unidade_consumidora = " + "'" + id_unidade + "'")

    for row in cursor:
        ambiente = row[0]
        break

    conn.close()
    return ambiente # 0 = cativo 1 = livre

def InsereUnidade(id_unidade,mes,ano):
    global conexao
    id = 0
    data_atual = date.today()

    conn = pyodbc.connect(conexao)
    consulta = conn.cursor()
    consulta.execute("SELECT id FROM ludfor.dbo.unidade where unidade_consumidora = " + "'" + id_unidade + "'")

    for row in consulta:
        id = row[0]
        break

    insert = conn.cursor()
    sql = "INSERT INTO fat_rge VALUES (?, ?, ?, ?, ?)"
    val = (id,id_unidade,mes,ano,data_atual)
    insert.execute(sql,val)
    conn.commit()
    conn.close()

def RealizaDow(id_unidade,mes,ano):
    global conexao
    result = False
    ccee_gestao = 0
    id = 0

    conn = pyodbc.connect(conexao)
    gestao = conn.cursor()
    sql = ("SELECT unidade.id FROM ludfor.dbo.unidade inner join distribuidora on unidade.id_distribuidora = distribuidora.id where (unidade.unidade_consumidora = ?) and ccee_gestao = 1 and ambiente = 1 and distribuidora.descricao like '%rge%' ") #somente unidades que possuam gestão CCEE (ambiente livre), com distribuidra rge e rge sul
    val = (id_unidade)
    gestao.execute(sql,val)

    for row in gestao:
        id = row[0]
        result = True
        break

    if id > 0:
        # insere na tabela unidade informação referenta a UC estar no site da CPFL, caso de ter vencido a procuração
        updatefatura(0,id)

        consulta = conn.cursor()
        sql = ("SELECT unidade.id FROM ludfor.dbo.fat_rge left join unidade on fat_rge.id_unidade = unidade.id where (unidade.unidade_consumidora = ? or fat_rge.unidade_consumidora = ?) and fat_rge.mes = ? and fat_rge.ano = ? ")
        val = (id_unidade,id_unidade,mes,ano)
        consulta.execute(sql,val)
        # verifica se o download da UC atual já não foi realizado para o mÊs e ano informado
        for row in consulta:
            result = False
            break

    conn.close()

    return result # True realiza download
