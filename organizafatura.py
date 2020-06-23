import pyodbc

def ambienteUnidade(id_unidade):
    ambiente = -1

    conn = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};'
                          'Server=BENHURBITTENCOU;'
                          'Database=ludfor;'
                          'Trusted_Connection=yes;')

    cursor = conn.cursor()
    cursor.execute("SELECT ambiente FROM ludfor.dbo.unidade where unidade_consumidora = " + "'" + id_unidade + "'")

    for row in cursor:
        ambiente = row[0]
        break

    conn.close()
    return ambiente # 0 = cativo 1 = livre

def InsereUnidade(id_unidade,mes,ano):
    id = 0

    conn = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};'
                          'Server=BENHURBITTENCOU;'
                          'Database=ludfor;'
                          'Trusted_Connection=yes;')

    consulta = conn.cursor()
    consulta.execute("SELECT id FROM ludfor.dbo.unidade where unidade_consumidora = " + "'" + id_unidade + "'")

    for row in consulta:
        id = row[0]
        break

    insert = conn.cursor()
    sql = "INSERT INTO fat_rge VALUES (?, ?, ?, ?, ?)"
    val = (id,id_unidade,mes,ano,1)
    insert.execute(sql,val)
    conn.commit()
    conn.close()

def ExisteFatura(id_unidade,mes,ano):
    result = 0

    conn = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};'
                          'Server=BENHURBITTENCOU;'
                          'Database=ludfor;'
                          'Trusted_Connection=yes;')

    consulta = conn.cursor()
    sql = ("SELECT unidade.id FROM ludfor.dbo.fat_rge left join unidade on fat_rge.id_unidade = unidade.id where (unidade.unidade_consumidora = ? or fat_rge.unidade_consumidora = ?) and fat_rge.mes = ? and fat_rge.ano = ? ")
    val = (id_unidade,id_unidade,mes,ano)
    consulta.execute(sql,val)

    for row in consulta:
        result = row[0]
        break

    conn.close()

    return result
