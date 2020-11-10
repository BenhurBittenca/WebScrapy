import psycopg2
import os.path
from datetime import date

########### Construct connection string
host = "192.168.78.2"
dbname = "ludfor"
user = "ludfor"
password = "Knk4xmLD"
conexao = "host={0} user={1} dbname={2} password={3}".format(host, user, dbname, password)
path_default = r"C:\WebScrapy" 
############

def BuscaPasta(path,empresa,razao,uc,distribuidora,nome,ano,mes,ambiente,):
    # monta descrição arquivo da pasta
    empresa = str(empresa)
    distri = str(distribuidora)
    distri = (distri.replace("-", ""))

    if ambiente == 0: #cativo
        path = (path + '/' + empresa + "/" + uc + '_' + nome.replace(" ","_") + '/Faturas/Faturas_' + distri + "/Faturas_" + str(ano))
    else: #livre
        path = (path + '/' + empresa + "/" + uc + '_' + nome.replace(" ","_") + '_ML/Faturas/Faturas_' + distri + "/Faturas_" + str(ano))

    # monta descrição arquivo
    ano = str(ano)
    if int(mes) < 10:
        mes = "0" + str(mes)
    ano = ano[2:4]

    file = format("/" + str(mes) + str(ano) + "_Fatura_" + distri + "_" + empresa.replace(" ","_") + "_" + nome.replace(" ","_") + ".pdf")

    existe = os.path.isfile(path + file)

    return existe

def updatefatura(uc,mes,ano,id,download):
    global conexao
    data_atual = str(date.today())

    conn = psycopg2.connect(conexao)
    insert = conn.cursor()

    if download == 9: # quando fatura foi baixada de forma manual e colocada na pasta do cliente
        sql = "INSERT INTO fat_rge VALUES (default, %s, %s, %s, %s, %s,1)"
        val = (id,uc,mes,ano,data_atual,)
    else:
        sql = "UPDATE fat_rge SET pastacliente = 1 WHERE unidade_consumidora = %s and mes = %s and ano = %s"
        val = (uc,mes,ano,)

    insert.execute(sql,val)
    conn.commit()
    conn.close()

###############################################
#verifica status do robo, se estiver em execução não executa
log_status = (path_default + r"\status.txt")
txt_status = open(log_status, 'r')
status = txt_status.readline()

if status != 'em execução':
    contador = 0
    while (contador <= 1): # feito para verificar o mes de referencia e um anterior, ex: faturas do cativo podem estar sendo baixadas no mês posterior ao de referência
        # mes e ano atual   
        data_atual = str(date.today())
        mes_ref = int(int(data_atual[5:7]))
        ano_ref = int(data_atual[:4])
    
        if mes_ref == 1:
            ano_ref_livre = int(int(data_atual[:4])-1)
            mes_ref_livre = 12
        else:
            ano_ref_livre = int(data_atual[:4])
            mes_ref_livre = (mes_ref-1)

        if contador == 1:
            if mes_ref == 1:
                mes_ref = 12
                ano_ref = (ano_ref - 1)
            else:
                mes_ref = mes_ref -1  

            if mes_ref_livre == 1:
                mes_ref_livre = 12
                ano_ref_livre = (ano_ref_livre - 1)
            else:
                mes_ref_livre = mes_ref_livre -1   

        contador = contador + 1   
        print(mes_ref)
        print(ano_ref)    

        conn = psycopg2.connect(conexao)
        consulta = conn.cursor()
        sql = (" SELECT empresa.descricao, unidade.razao_social, unidade.unidade_consumidora, distribuidora.descricao, unidade.nome, unidade.id, unidade.ambiente, "
                " coalesce((select pastacliente from fat_rge where unidade.id = fat_rge.id_unidade "
                " and ((fat_rge.mes = " + str(mes_ref_livre) + " and fat_rge.ano = " + str(ano_ref_livre) + " and unidade.ambiente = 1) or "
                " (fat_rge.mes = " + str(mes_ref) + " and fat_rge.ano = " + str(ano_ref) + " and unidade.ambiente = 0))),9) "
                " FROM unidade inner join empresa on unidade.id_empresa = empresa.id "
                " inner join modalidade on unidade.id_modalidade = modalidade.id "
                " inner join distribuidora on unidade.id_distribuidora = distribuidora.id "
                " where distribuidora.descricao like '%RGE%' "        
                " and ((ccee_gestao = 1 and ambiente = 1 and unidade.ccee_data_migracao <='" + data_atual + "') or "
                " (ambiente = 0 and modalidade.descricao <> 'Baixa tensão' and id_empresa <> 514)) order by unidade.id")

        consulta.execute(sql)

        for row in consulta:
            if row[6] == 0: #cativo
                existe = (BuscaPasta("//server/PUBLICO/Clientes/",row[0],row[1],row[2],row[3],row[4].strip(),ano_ref,mes_ref,row[6]))
            else: #livre
                existe = (BuscaPasta("//server/PUBLICO/Clientes/",row[0],row[1],row[2],row[3],row[4].strip(),ano_ref_livre,mes_ref_livre,row[6]))

            print("Empresa: " + row[0] + " Unidade: " + row[4])
            print()   

            if (existe) and (row[7] != 1):
                if row[6] == 0: #cativo
                    updatefatura(row[2],mes_ref,ano_ref,row[5],row[7])
                else: #livre
                    updatefatura(row[2],mes_ref_livre,ano_ref_livre,row[5],row[7])
    conn.close()
