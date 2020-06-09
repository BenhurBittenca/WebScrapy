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
