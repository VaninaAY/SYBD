import pandas as pd
import sqlite3
import re


# Перевод XLS файла в db

def from_XLS_to_db(path_to_files, path_to_db):
    # читаем данные из файла xlsx
    df_Vyst_mo = pd.read_excel(path_to_files + '//' +"Vyst_mo.XLS")
    df_VUZ = pd.read_excel(path_to_files + '//' + "VUZ.XLS", engine='xlrd')
    df_grntirub = pd.read_excel(path_to_files + '//' + "grntirub.XLS")

    # создаем базу данных SQLite
    conn = sqlite3.connect(path_to_db)
    # создаем таблицу в базе данных
    df_Vyst_mo.to_sql('НИР', conn, if_exists='replace', index=False)
    df_VUZ.to_sql('ВУЗы', conn, if_exists='replace', index=False)
    df_grntirub.to_sql('ГРНТИ', conn, if_exists='replace', index=False)
    # закрываем соединение с базой данных
    conn.close()


def duplicate_processing(cur):
    uniqueness_check = "SELECT * FROM НИР GROUP BY codvuz, 'type', regnumber HAVING COUNT(*) > 1"
    cur.execute(uniqueness_check)
    not_unique_rows = cur.fetchall()

    name_columns = tuple([d[0] for d in cur.description])

    while not_unique_rows:
        for i, row in enumerate(not_unique_rows):
            delete_uniq = f"DELETE FROM НИР  where codvuz = {row[0]} AND type = '{row[2]}' AND  regnumber = '{row[3]}' AND subject = '{row[4]}'"
            cur.execute(delete_uniq)

            row = list(row)
            row[3] = '0' + row[3]
            for j, value in enumerate(row):
                if value is None:
                    row[j] = 'NULL'

            row = tuple(row)
            insert_unique = f"INSERT INTO НИР {name_columns} VALUES {row}"
            cur.execute(insert_unique)

        cur.execute(uniqueness_check)
        not_unique_rows = cur.fetchall()



def creat_pr(cur):
    create_tbl = '''CREATE TABLE NIR_new (
        codvuz INTEGER,
        z2 TEXT,
        'type' TEXT ,
        regnumber TEXT ,
        subject TEXT ,
        grnti TEXT ,
        bossname TEXT ,
        bosstitle TEXT ,
        exhitype TEXT ,
        vystavki TEXT ,
        exponat TEXT ,
        PRIMARY KEY (codvuz, 'type', regnumber)
    )'''
    cur.execute(create_tbl)

    insert_data = '''INSERT INTO NIR_new SELECT * FROM НИР'''
    cur.execute(insert_data)

    delete_NIR_old = 'DROP TABLE НИР'
    cur.execute(delete_NIR_old)

    rename_new_tbl = 'ALTER TABLE NIR_new RENAME TO НИР'
    cur.execute(rename_new_tbl)


def fill_z2(cur):
    filling_column_z2 = 'UPDATE НИР SET z2 = (SELECT ВУЗы.z2) FROM ВУЗы WHERE НИР.codvuz = ВУЗы.codvuz'
    cur.executescript(filling_column_z2)


def recovery(grnti):
    res_str = ''
    res = re.split(',|;| ', grnti)
    i = 0
    for s in res:
        if s == '':
            continue
        if i != 0:
            res_str += ';'
        res_str += s
        i += 1
    return res_str


def processing_column_grnti(cur):
    cur.execute("SELECT * FROM НИР")
    Vyst_mo = cur.fetchall()

    for row in Vyst_mo:
        grnti = recovery(str(row[5]))
        cur.execute("UPDATE НИР SET grnti = (?) WHERE codvuz=(?) AND regnumber=(?) AND subject=(?)",
                    [grnti, row[0], row[3], row[4]])

def delete_absent_id(cur):
    flag = 0
    while flag == 0:
        cur.execute("select НИР.codvuz from НИР left join ВУЗы on ВУЗы.codvuz = НИР.codvuz where ВУЗы.codvuz is null group by НИР.codvuz")
        uniq_absent_id = cur.fetchall()
        if len(uniq_absent_id) == 0:
            break
        for i, j in enumerate(uniq_absent_id):
            id = j[0]
            new_id = id - 1
            cur.execute(f'''UPDATE НИР SET codvuz = {new_id} WHERE codvuz={id}''')

def rename_columns(cur):
    new_columns_NIR = ['код ВУЗа', 'ВУЗ кратко', 'Форма орг-и', 'рег. номер', 'проект', 'код ГРНТИ',
                       'руководитель', 'должность рук.', 'наличие экспаната', 'выставка', 'название экспаната']
    new_columns_VUZ = ['код ВУЗа', 'ВУЗ', 'ВУЗ полный', 'ВУЗ кратко', 'фед. округ', 'город',
                       'статус', 'номер области', 'область', 'гр_вед', 'проф']
    new_columns_GRNTI = ['код рубрики', 'рубрика']

    new_columns = [new_columns_NIR, new_columns_VUZ, new_columns_GRNTI]
    tbl_names = ['НИР', 'ВУЗы', 'ГРНТИ']

    for num_tbl, tbl in enumerate(tbl_names):
        columns = f"PRAGMA table_info({tbl})"
        cur.execute(columns)
        columns = [out[1] for out in cur.fetchall()]
        # print(columns)
        for num_clm, clm in enumerate(columns):
            rename_column = f"ALTER TABLE {tbl} RENAME COLUMN {clm} TO '{new_columns[num_tbl][num_clm]}'"
            # print(rename_column)
            cur.execute(rename_column)




# Создание базы данных без обработки
path_to_xls_files = r"C:\Users\vanin\Documents\институт\4 курс\7 семестр\СУБД\СУБД лаб FOR STUD\файлы на 2023\по вариантам XLS\v6 выст"
path_to_db = r'C:\Users\vanin\Documents\институт\4 курс\7 семестр\СУБД\project\SYBD.db'
from_XLS_to_db(path_to_xls_files, path_to_db)

# Обработка базы данных
conn = sqlite3.connect(path_to_db)
cur = conn.cursor()

duplicate_processing(cur)
# creat_pr(cur)
processing_column_grnti(cur)
delete_absent_id(cur)
fill_z2(cur)
rename_columns(cur)


cur.close()
conn.commit()
conn.close()