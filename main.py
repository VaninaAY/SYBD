# This is a sample Python script.
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import *
from PyQt6.QtWidgets import QAbstractItemView
import sqlite3
from PyQt6.QtWidgets import *
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import *
import pandas as pd
import openpyxl
import os

# from PyQt6.QtCore import QItemSelectionModel, QItemSelection
from PyQt6.QtCore import QModelIndex, QItemSelection, QItemSelectionModel

def saveSelectedRow():
    name = form.cards_name.text()
    if name == "":
        form.check_card_name.setStyleSheet("color: red;")
        form.check_card_name.setText("Ошибка! Введите имя файла")
        return

    form.check_card_name.setStyleSheet("color: black;")
    form.check_card_name.setText("")

    selected_rows_indexes = getattr(form, 'table_NIR').selectedIndexes()

    if selected_rows_indexes:
        data = []
        row = []
        for i, index in enumerate(selected_rows_indexes):
            if i % 11 == 0 and i != 0:
                data.append(row)
                row = []
            row.append(getattr(form, 'table_NIR').model().data(index))
        data.append(row)

        file_path = f'./cards/{name}.xlsx'

        # Проверка, существует ли файл
        if os.path.exists(file_path):
            # Открытие существующего файла
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active
        else:
            # Создание нового файла
            workbook = openpyxl.Workbook()
            sheet = workbook.active

        # Добавление строк в лист
        for row in data:
            sheet.append(row)

        # Сохранение файла
        workbook.save(file_path)
        form.check_card_name.setStyleSheet("color: black;")
        form.check_card_name.setText("Сохранено")
        QTimer.singleShot(3000, lambda: form.check_card_name.setText(""))

def save_table_to_excel():
    table_name = form.CMB_table_name.currentText()
    excel_path = f'./tables/{table_name}.xlsx'
    if table_name == "":
        return

    conn = sqlite3.connect('SYBD.db')
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    df.to_excel(excel_path, index=False)
    conn.close()

# Подклюючение к базе данных и проверка ее наличия
def connect_db(db_file):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_file)
    if not db.open():
        print("Cannot establish a database connection to {}!".format(db_file))
        return False
    return db



def main_functions():
    show_table('НИР', "table_NIR", NIR_COLUMN_WIDTH)
    show_table('ВУЗы', "table_VUZ", VUZ_COLUMN_WIDTH)
    show_table('ГРНТИ', "table_GRNTI", GRNTI_COLUMN_WIDTH)

    form.table_NIR.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    form.tableGroups.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    form.save_row.clicked.connect(saveSelectedRow)
    form.Button_delete.clicked.connect(lambda: deleteSelectedRow('table_NIR'))
    form.btn_detete_row.clicked.connect(lambda: deleteSelectedRow('tableGroups'))
    form.Button_add.clicked.connect(AddRow)
    form.Button_change.clicked.connect(ChangeRow)
    form_row_add.Button_reset.clicked.connect(nothing)
    form_row_add.Button_add.clicked.connect(nothing)
    window_row_add.closeEvent = close_event
    form.Button_filter.clicked.connect(Filter)
    form.new_filter_button.clicked.connect(Filter_for_table)

    # Заполнения комбобоксов для формы с добавлением строки
    fill_combobox('код ВУЗа', 'ВУЗы', 'comboBox_codvuz', form_row_add)
    fill_combobox('ВУЗ кратко', 'ВУЗы', 'comboBox_z2', form_row_add)
    form_row_add.comboBox_exhitype.addItems([None, 'Есть', 'Нет', 'Планируется'])
    form_row_add.comboBox_type.addItems([None, 'Тематический план', 'НТП'])

    form.comboBox_sort.addItems(['Без сортировки', 'Сортировка по столбцам', 'Сортировка по ключу'])
    form.comboBox_sort.currentIndexChanged.connect(lambda: on_combobox_sort_changed(1))
    form.CMB_sort_table.addItems(['Без сортировки', 'Сортировка по столбцам', 'Сортировка по ключу'])
    form.CMB_sort_table.currentIndexChanged.connect(lambda: on_combobox_sort_changed(0))
    # form.new_table_combobox.currentIndexChanged.connect(change_new_table)
    fill_combobox_table_name()
    form.CMB_table_name.currentIndexChanged.connect(processing_combobox_table_name)
    form.btn_detete_table.clicked.connect(table_delate)
    form.save_filter_table.clicked.connect(save_table_to_excel)

    form_table_delate.cansel.clicked.connect(window_table_delate.close)
    form_table_delate.yes.clicked.connect(drop_table)

# Отображение таблиц
def show_table(tbl_name, widget_name, column_width):
    table = QSqlTableModel()
    table.setTable(tbl_name)
    table.select()
    getattr(form, widget_name).setModel(table)
    for num_column, width in enumerate(column_width):
        getattr(form, widget_name).setColumnWidth(num_column, width)

def table_delate():
    window_table_delate.show()
    form_table_delate.textBrowser.setText(f'Вы действительно хотите удалить таблицу: {form.CMB_table_name.currentText()}')


def drop_table():
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_name)
    db.open()
    query = QSqlQuery()
    value = form.CMB_table_name.currentText()
    form.CMB_table_name.setCurrentIndex(0)
    query.exec(f"DROP TABLE '{value}'")
    window_table_delate.close()
    fill_combobox_table_name()
    fill_combobox_table_name_in_filter()
    form.CMB_table_name.setCurrentIndex(0)
    form_filter.union_new_table.setCurrentIndex(0)
    db.close()

def fill_combobox_table_name():
    query = QSqlQuery()
    query.exec("SELECT name FROM sqlite_master WHERE type='table'")
    distinct_values = [None]
    form.CMB_table_name.clear()
    while query.next():
        distinct_values.append(str(query.value(0)))
    distinct_values.remove('ГРНТИ')
    distinct_values.remove('НИР')
    distinct_values.remove('ВУЗы')
    form.CMB_table_name.clear()
    form.CMB_table_name.addItems(distinct_values)

def fill_combobox_table_name_in_filter():
    query = QSqlQuery()
    query.exec("SELECT name FROM sqlite_master WHERE type='table'")
    distinct_values = [None]
    form_filter.union_new_table.clear()
    while query.next():
        distinct_values.append(str(query.value(0)))
    distinct_values.remove('ГРНТИ')
    distinct_values.remove('НИР')
    distinct_values.remove('ВУЗы')
    form_filter.union_new_table.clear()
    form_filter.union_new_table.addItems(distinct_values)

def processing_combobox_table_name(index):
        # getattr(form_row_add, widget_disabled).setEditable(False)
        # getattr(form_row_add, widget_disabled).setCurrentIndex(index)
        table_name = form.CMB_table_name.itemText(index)
        show_table(table_name, "tableGroups", NIR_COLUMN_WIDTH)
# Функции удаления строки
def deleteRow(Indexes, table):
    for index in Indexes:
        getattr(form, table).model().removeRow(index)
    show_table('НИР', table, NIR_COLUMN_WIDTH)
    window_row_deletion.close()

def deleteSelectedRow(table):
    selected_rows = getattr(form, table).selectionModel().selectedRows()
    selected_rows_indexes = getattr(form, table).selectedIndexes()

    if selected_rows_indexes:
        window_row_deletion.show()

        data = []
        row = []
        for i, index in enumerate(selected_rows_indexes):
            if i % 11 == 0 and i != 0:
                data.append(row)
                row = []
            row.append(getattr(form, table).model().data(index))
        data.append(row)
        print(data)

        text = ''
        for row in data:
            text += f'код ВУЗа = {row[0]},  ВУЗ = {row[1]},  Форма организации = {row[2]}, Регестрационный номер = {row[3]}<br>'

        form_row_deletion.textBrowser_del.setText(text)
        selected_rows_indexes = [index.row() for index in selected_rows]
        form_row_deletion.Button_delete.clicked.connect(lambda: deleteRow(selected_rows_indexes, table))
        form_row_deletion.Button_cancel.clicked.connect(window_row_deletion.close)

    else:
        window_message_select_row.show()
        form_message_select_row.Button_ok.clicked.connect(window_message_select_row.close)

# Обработка combox для кода ВУЗа и краткого названия, чтобы автоматически подтягивались значения
def processing_combobox_codvuz_z2(widget_disabled, widget_chosen):
    def a(index):
        value = getattr(form_row_add, widget_chosen).currentText()
        query = QSqlQuery()
        if widget_chosen == 'comboBox_z2':
            query.exec(f'Select "код ВУЗа" from ВУЗы where "ВУЗ кратко" = "{value}"')
        elif widget_chosen == 'comboBox_codvuz':
            query.exec(f'Select "ВУЗ кратко" from ВУЗы where "код ВУЗа" = {value}')
        query.next()
        result = query.value(0)
        getattr(form_row_add, widget_disabled).setCurrentText(str(result))
    return a

# Заполняем комбо боксы значениями, полученные из БД
def fill_combobox(column, table, widget, form):
    query = QSqlQuery()
    query.exec(f'SELECT DISTINCT "{column}" FROM {table}')
    distinct_values = ['']
    getattr(form, widget).clear()
    while query.next():
        distinct_values.append(str(query.value(0)))
    if widget != 'comboBox_codvuz':
        distinct_values.sort()
    getattr(form, widget).addItems(distinct_values)

# Обработка выставок, запрет редактирования, если выставки нет
def exhibition_processing(index):
    if index == 2:
        form_row_add.lineEdit_vystavki.setReadOnly(True)
        form_row_add.lineEdit_exponat.setReadOnly(True)
        form_row_add.lineEdit_vystavki.clear()
        form_row_add.lineEdit_exponat.clear()
    else:
        form_row_add.lineEdit_vystavki.setReadOnly(False)
        form_row_add.lineEdit_exponat.setReadOnly(False)

def close_form_row_add():
    reset_form_adding_row()
    window_row_add.close()

    form_row_add.Button_add.clicked.disconnect()
    form_row_add.Button_add.clicked.connect(nothing)
    form_row_add.Button_reset.clicked.disconnect()
    form_row_add.Button_reset.clicked.connect(nothing)

def close_event(event):
    close_form_row_add()
    event.accept()

def row_validation(task):
    # проверка, на то что все значения в норме
    lst_combobox = ['comboBox_codvuz', 'comboBox_type', 'comboBox_exhitype']
    error_combobox = ["Не заполнены поля 'код ВУЗа' и 'краткое название ВУЗа'",
                      "Не заполнено поле 'Форма организации'", "Не заполнено поле 'наличие экспаната'"]

    lst_lineEdit_must_be_field = ['lineEdit_regnum', 'lineEdit_grnti1', 'lineEdit_bossname']
    error_lineEdit = ['регестрационный номер','код ГРНТИ','руководитель']

    # Проверка, что комбобокс заполнен
    for num, combobox in enumerate(lst_combobox):
        if getattr(form_row_add, combobox).currentIndex() == 0:
            return False, error_combobox[num]

    if form_row_add.lineEdit_subject.toPlainText() == '':
        return False, "Не заполнено текстовое поле 'наименование проекта'"

    # Проверка, что тектовый редактор заполнены
    for num, lineEdit in enumerate(lst_lineEdit_must_be_field):
        if getattr(form_row_add, lineEdit).text() == '':
            return False, f"Не заполнено текстовое поле '{error_lineEdit[num]}'"

    if form_row_add.comboBox_type.currentText() == 'Тематический план':
        nir_type = 'Е'
    elif form_row_add.comboBox_type.currentText()  == 'НТП':
        nir_type = 'М'

    # Проверка на первичный ключ
    if task == 'insert':
        conn = sqlite3.connect('SYBD.db')
        cursor = conn.cursor()
        query = '''SELECT COUNT(*) FROM НИР WHERE "код ВУЗа"=? AND "Форма орг-и"=? AND "рег. номер"=?'''
        params = (int(form_row_add.comboBox_codvuz.currentText()), nir_type, form_row_add.lineEdit_regnum.text())
        cursor.execute(query, params)
        result = cursor.fetchone()[0]
        if not result == 0:
            cursor.close()
            conn.close()
            return False, 'Такие уникальны данные (код ВУЗа, Форма организации, регистрационный номер) уже есть. Попробуйте сменить регистрационный номер'
        cursor.close()
        conn.close()

    # Проверка последних 2-ух полей с выставкой
    error_vystavki = ['название выставки', 'название экспаната']
    if form_row_add.comboBox_exhitype.currentText() != 'Нет':
        for num, lineEdit in enumerate(['lineEdit_vystavki', 'lineEdit_exponat']):
            if getattr(form_row_add, lineEdit).text() == '':
                return False, f"Не заполнено текстовое поле '{error_vystavki[num]}'"

    # # проверка кода грнти
    cod_grnti1 = form_row_add.lineEdit_grnti1.text()
    cod_grnti2 = form_row_add.lineEdit_grnti2.text()
    if len(cod_grnti1) != 8:
        return False, 'Первое поле ГРНТИ введено не верно'

    if len(cod_grnti2) == 2:
        total_cod_grnti = cod_grnti1
    elif len(cod_grnti2) == 8:
        total_cod_grnti = cod_grnti1 + ';' + cod_grnti2
    else:
        return False, 'Второе поле ГРНТИ введено не верно'
    return True, total_cod_grnti

def insert_row_in_bd(task, num_row):
    flag, text = row_validation(task)
    if flag:
        if form_row_add.comboBox_type.currentText() == 'Тематический план':
            nir_type = 'Е'
        elif form_row_add.comboBox_type.currentText() == 'НТП':
            nir_type = 'М'

        values_new_row = [form_row_add.comboBox_codvuz.currentText(), form_row_add.comboBox_z2.currentText(),
                          nir_type, form_row_add.lineEdit_regnum.text(),
                          form_row_add.lineEdit_subject.toPlainText(), text, form_row_add.lineEdit_bossname.text(),
                          form_row_add.lineEdit_bosstitle.text(), form_row_add.comboBox_exhitype.currentText()[0],
                          form_row_add.lineEdit_vystavki.text(), form_row_add.lineEdit_exponat.text()]

        values_new_row = tuple(values_new_row)
        query = QSqlQuery()
        if task == 'insert':
            query.exec(f'''INSERT INTO НИР VALUES {values_new_row}''')
        elif task == 'update':
            query.exec(
                f"""UPDATE НИР SET "ВУЗ кратко" = "{values_new_row[1]}", проект = "{values_new_row[4]}",  "код ГРНТИ" = "{values_new_row[5]}", 
                                руководитель = "{values_new_row[6]}", "должность рук." = "{values_new_row[7]}",
                                "наличие экспаната" = "{values_new_row[8]}", выставка = "{values_new_row[9]}", "название экспаната" = "{values_new_row[10]}"
                                WHERE "код ВУЗа" = "{values_new_row[0]}"  AND "Форма орг-и" = "{values_new_row[2]}" AND "рег. номер" = "{values_new_row[3]}"
                                """)


            show_table('НИР', "table_NIR", NIR_COLUMN_WIDTH)
            cmb_sort_selected = form.comboBox_sort.currentText()
            form.comboBox_sort.setCurrentText('Без сортировки')
            form.comboBox_sort.setCurrentText(cmb_sort_selected)
        close_form_row_add()

        # Выделение сторки
        form.table_NIR.selectRow(num_row)

    else:
        window_message_add_row.show()
        form_message_add_row.textBrowser_error.setText(text)
        form_message_add_row.Button_ok.clicked.connect(window_message_add_row.close)

# Очищение строк и комбобоксов при нажатии кнопки сброс
def reset_form_adding_row():
    lst_combobox = ['comboBox_codvuz', 'comboBox_z2', 'comboBox_type', 'comboBox_exhitype']
    for combobox in lst_combobox:
        getattr(form_row_add, combobox).setCurrentIndex(0)
    lst_lineEdit = ['lineEdit_regnum', 'lineEdit_grnti1', 'lineEdit_grnti2',
                    'lineEdit_bossname', 'lineEdit_bosstitle', 'lineEdit_vystavki', 'lineEdit_exponat']
    for lineEdit in lst_lineEdit:
        getattr(form_row_add, lineEdit).clear()
    form_row_add.lineEdit_subject.clear()
def AddRow():
    form.comboBox_sort.setCurrentText('Без сортировки')
    window_row_add.show()
    form_row_add.Button_cancel.clicked.connect(close_form_row_add)
    form_row_add.Button_add.clicked.disconnect(nothing)
    form_row_add.Button_add.clicked.connect(lambda: insert_row_in_bd('insert', form.table_NIR.model().rowCount()))
    form_row_add.Button_reset.clicked.disconnect(nothing)
    form_row_add.Button_reset.clicked.connect(reset_form_adding_row)

    form_row_add.comboBox_codvuz.activated.connect(processing_combobox_codvuz_z2('comboBox_z2', 'comboBox_codvuz'))
    form_row_add.comboBox_z2.activated.connect(processing_combobox_codvuz_z2('comboBox_codvuz', 'comboBox_z2'))
    form_row_add.comboBox_exhitype.activated.connect(exhibition_processing)

    # когда появится изменение
    form_row_add.comboBox_codvuz.setEnabled(True)
    form_row_add.comboBox_z2.setEnabled(True)
    form_row_add.comboBox_type.setEnabled(True)
    form_row_add.lineEdit_regnum.setReadOnly(False)

def reset_form_chengin_row():
    form_row_add.comboBox_exhitype.setCurrentIndex(0)
    lst_lineEdit = ['lineEdit_grnti1', 'lineEdit_grnti2',
                    'lineEdit_bossname', 'lineEdit_bosstitle', 'lineEdit_vystavki', 'lineEdit_exponat']
    for lineEdit in lst_lineEdit:
        getattr(form_row_add, lineEdit).clear()
    form_row_add.lineEdit_subject.clear()

def ChangeRow():
    selected_row = form.table_NIR.selectedIndexes()
    if selected_row:
        window_row_add.show()
        form_row_add.Button_cancel.clicked.connect(close_form_row_add)
        form_row_add.Button_add.clicked.disconnect(nothing)
        for index in selected_row:
            row_index = index.row()
        form_row_add.Button_add.clicked.connect(lambda: insert_row_in_bd('update', row_index))
        form_row_add.Button_reset.clicked.disconnect(nothing)
        form_row_add.Button_reset.clicked.connect(reset_form_chengin_row)

        data = []
        for index in selected_row:
            data.append(form.table_NIR.model().data(index))

        form_row_add.comboBox_codvuz.setCurrentText(str(data[0]))
        form_row_add.comboBox_z2.setCurrentText(data[1])

        if data[2] == 'Е':
            nir_type = 'Тематический план'
        elif data[2] == 'М':
            nir_type = 'НТП'
        form_row_add.comboBox_type.setCurrentText(nir_type)

        form_row_add.comboBox_codvuz.setEnabled(False)
        form_row_add.comboBox_z2.setEnabled(False)
        form_row_add.comboBox_type.setEnabled(False)
        form_row_add.lineEdit_regnum.setText(data[3])
        form_row_add.lineEdit_regnum.setReadOnly(True)

        grnti = data[5].split(';')
        if len(grnti) == 1:
            grnti.append('')

        data4_10 = grnti + data[6:8] + data[9:]
        lst_line_EDITOR = ['lineEdit_grnti1', 'lineEdit_grnti2', 'lineEdit_bossname',
                           'lineEdit_bosstitle', 'lineEdit_vystavki', 'lineEdit_exponat']

        for i in range(len(lst_line_EDITOR)):
            getattr(form_row_add, lst_line_EDITOR[i]).setText(data4_10[i])

        form_row_add.lineEdit_subject.setText(data[4])

        if data[8] == 'Е':
            data[8] = 'Есть'
        elif data[8] == 'Н':
            data[8] = 'Нет'
        else:
            data[8] = 'Планируется'
        form_row_add.comboBox_exhitype.setCurrentText(data[8])
        if form_row_add.comboBox_exhitype.currentText() == 'Нет':
            form_row_add.lineEdit_vystavki.setReadOnly(True)
            form_row_add.lineEdit_exponat.setReadOnly(True)
        form_row_add.comboBox_exhitype.activated.connect(exhibition_processing)

    else:
        window_message_select_row.show()
        form_message_select_row.Button_ok.clicked.connect(window_message_select_row.close)

def on_combobox_sort_changed(a):
    if a == 1:
        selected_sort = form.comboBox_sort.currentText()
        selected_table = 'НИР'
        widget = 'table_NIR'
    else:
        selected_sort = form.CMB_sort_table.currentText()
        selected_table = form.CMB_table_name.currentText()
        widget = 'tableGroups'
    if selected_sort == 'Без сортировки':
        getattr(form, widget).setSortingEnabled(False)
        show_table(selected_table, widget, NIR_COLUMN_WIDTH)
    elif selected_sort == 'Сортировка по столбцам':
        show_table(selected_table, widget, NIR_COLUMN_WIDTH)
        getattr(form, widget).setSortingEnabled(True)
    elif selected_sort == 'Сортировка по ключу':
        show_table(selected_table, widget, NIR_COLUMN_WIDTH)
        query = QSqlQuery()
        query.exec(f'SELECT * FROM {selected_table} ORDER BY "код ВУЗа" ASC, "Форма орг-и" ASC, "рег. номер" ASC')
        model = QSqlTableModel()
        model.setQuery(query)
        getattr(form, widget).setModel(model)
        
def nothing():
    pass

# def change_new_table():
#     name = form.new_table_combobox.currentText()
#     if name == "":
#         return
#     show_table(name, "new_table_NIR", NIR_COLUMN_WIDTH)
#
# def fill():
#     query = QSqlQuery()
#     query.exec("SELECT name FROM sqlite_master WHERE type='table';")
#     table_names = []
#     while query.next():
#         table_names.append(query.value(0))
#     for name in table_names:
#         if name != 'НИР' and name != 'ВУЗы' and name != 'ГРНТИ':
#             new_tables.append(name)

#############################################################################################
#############################################################################################
#############################################################################################

def get_filter():
    federal_district = form_filter.federal_district.currentText()
    region = form_filter.region.currentText()
    city = form_filter.city.currentText()
    vyst = form_filter.vyst.currentText()
    VUZ = form_filter.VUZ.currentText()
    grnti = form_filter.grnti.text()

    request = ""

    if federal_district != "":
        request += f'AND "фед. округ" = "{federal_district}" '
    if region != "":
        request += f'AND "область" = "{region}" '
    if city != "":
        request += f'AND "город" = "{city}" '
    if vyst != "":
        if vyst == 'Есть':
            request += f'AND "наличие экспаната" = "Е"'
        if vyst == 'Нет':
            request += f'AND "наличие экспаната" = "Н"'
        if vyst == 'Планируется':
            request += f'AND "наличие экспаната" = "П"'
    if VUZ != "":
        request += f'AND НИР."ВУЗ кратко" = "{VUZ}" '
    if grnti != "":
        request += f'AND ("код ГРНТИ" LIKE "{grnti}%" OR "код ГРНТИ" LIKE "%;{grnti}%") '

    return request

def request_for_filter(table_name):
    conn = sqlite3.connect('SYBD.db')
    cursor = conn.cursor()

    request = get_filter()
    if request == "":
        cursor.execute(f"""SELECT * FROM {table_name} INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = {table_name}.[код ВУЗа]""")
    else:
        request = request.replace("AND", "", 1)
        cursor.execute(f'''SELECT * FROM {table_name} INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = {table_name}.[код ВУЗа] WHERE {request}''')
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return data

def show_filter_table(data):
    tableWidget = QTableWidget()
    tableWidget.setRowCount(len(data))
    tableWidget.setColumnCount(11)
    for i, user in enumerate(data):
        for j, value in enumerate(user):
            item = QTableWidgetItem(str(value))
            tableWidget.setItem(i, j, item)
    tableWidget.setHorizontalHeaderLabels(['код ВУЗа', 'ВУЗ кратко', 'НТП', 'рег. номер', 'проект', 'код ГРНТИ', 'руководитель', 'должность рук.', 'налич. экспаната', 'выставка', 'назван экспаната'])
    window.setCentralWidget(tableWidget)
    window.show()

def filter_Save_func():
    data = request_for_filter("НИР")
    show_filter_table(data)

def save_for_filter(table_name):
    table_name = "НИР"
    try:
        new_table = form_filter.table_name.text()
        if new_table == "":
            form_filter.label_name.setStyleSheet("color: red;")
            form_filter.label_name.setText("Ошибка! Введите имя таблицы")
            return
        query = QSqlQuery(db)
        check_table_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{new_table}'"
        if query.exec(check_table_query):
            if query.first():
                db.close()
                conn = sqlite3.connect('SYBD.db')
                cursor = conn.cursor()
                cursor.execute(f"DROP TABLE '{new_table}'")
                cursor.close()
                conn.close()
                db.open()
        request = get_filter()
        query_str = ""
        if request == "":
            query_str = f'CREATE TABLE "{new_table}" AS SELECT {table_name}.[код ВУЗа], {table_name}.[ВУЗ кратко], {table_name}.[Форма орг-и], {table_name}.[рег. номер], {table_name}.[проект], {table_name}.[код ГРНТИ], {table_name}.[руководитель], {table_name}.[должность рук.], {table_name}.[наличие экспаната], {table_name}.[выставка], {table_name}.[название экспаната] FROM {table_name} INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = {table_name}.[код ВУЗа];'
        else:
            request = request.replace("AND", "", 1)
            query_str = f'CREATE TABLE "{new_table}" AS SELECT {table_name}.[код ВУЗа], {table_name}.[ВУЗ кратко], {table_name}.[Форма орг-и], {table_name}.[рег. номер], {table_name}.[проект], {table_name}.[код ГРНТИ], {table_name}.[руководитель], {table_name}.[должность рук.], {table_name}.[наличие экспаната], {table_name}.[выставка], {table_name}.[название экспаната] FROM {table_name} INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = {table_name}.[код ВУЗа] WHERE {request};'
        query.exec(query_str)
        form_filter.label_name.setStyleSheet("color: black;")
        form_filter.label_name.setText("")
        # new_tables.append(new_table)
        form_filter.label_name.setStyleSheet("color: black;")
        form_filter.label_name.setText("Таблица сохранена")
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")

def filter_cancel_for_main():
    form_filter.button_ok.clicked.disconnect(filter_Save_func)
    form_filter.save.clicked.disconnect(save_for_filter_tmp)
    form_filter.Button_Cancel.clicked.disconnect(filter_cancel_for_main)
    filter_cancel()

def filter_cancel():
    getattr(form_filter, 'federal_district').setCurrentIndex(0)
    getattr(form_filter, 'city').setCurrentIndex(0)
    getattr(form_filter, 'region').setCurrentIndex(0)
    getattr(form_filter, 'VUZ').setCurrentIndex(0)
    getattr(form_filter, 'vyst').setCurrentIndex(0)
    form_filter.table_name.setText("")
    form_filter.grnti.setText("")
    form_filter.label_name.setText("")
    form.setupUi(window)
    main_functions()
    window_filer.close()

def fill_combobox_for_filer(column, widget, request):
    query = QSqlQuery()
    if column == 'ВУЗ кратко':
        query.exec(f'SELECT DISTINCT НИР."{column}" FROM НИР INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = НИР.[код ВУЗа] {request}')
    else:
        query.exec(f'SELECT DISTINCT "{column}" FROM НИР INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = НИР.[код ВУЗа] {request}')
    distinct_values = [None]
    getattr(form_filter, widget).clear()
    while query.next():
        distinct_values.append(str(query.value(0)))
    getattr(form_filter, widget).addItems(distinct_values)

def func_for_region():
    filter_Save_func()
    region = form_filter.region.currentText()
    if region == "":
        return
    conn = sqlite3.connect('SYBD.db')
    cursor = conn.cursor()
    cursor.execute(f'''SELECT DISTINCT "фед. округ" FROM ВУЗы WHERE область = "{region}"''')
    res = cursor.fetchall()
    str_region = str(res[0])
    str_region = str_region[2:len(str_region)-3]
    form_filter.federal_district.setCurrentText(str_region)
    cursor.close()
    conn.close()
    req = f'WHERE "область" = "{region}"'
    fill_combobox_for_filer('город', 'city', req)
    fill_combobox_for_filer('ВУЗ кратко', 'VUZ', req)
    form_filter.region.setCurrentText(region)

def func_for_city():
    filter_Save_func()
    city = form_filter.city.currentText()
    if city == "":
        return
    conn = sqlite3.connect('SYBD.db')
    cursor = conn.cursor()
    city = form_filter.city.currentText()
    cursor.execute(f'''SELECT DISTINCT "область" FROM ВУЗы WHERE город = "{city}"''')
    res = cursor.fetchall()
    str_region = str(res[0])
    str_region = str_region[2:len(str_region)-3]
    form_filter.region.setCurrentText(str_region)
    form_filter.city.setCurrentText(city)
    cursor.close()
    conn.close()
    req = f'WHERE "город" = "{city}"'
    fill_combobox_for_filer('ВУЗ кратко', 'VUZ', req)

def func_for_federal_district():
    filter_Save_func()
    fed = form_filter.federal_district.currentText()
    if fed != "":
        req = f'WHERE "фед. округ" = "{fed}"'
        fill_combobox_for_filer('область', 'region', req)
        fill_combobox_for_filer('город', 'city', req)
        fill_combobox_for_filer('ВУЗ кратко', 'VUZ', req)
    else:
        fill_combobox_for_filer('фед. округ', 'federal_district', "")
        fill_combobox_for_filer('область', 'region', '')
        fill_combobox_for_filer('город', 'city', '')
        fill_combobox_for_filer('ВУЗ кратко', 'VUZ', '')

def func_for_VUZ():
    VUZ = form_filter.VUZ.currentText()
    if VUZ == "":
        return
    conn = sqlite3.connect('SYBD.db')
    cursor = conn.cursor()
    cursor.execute(f'''SELECT DISTINCT "город" FROM ВУЗы WHERE "ВУЗ кратко" = "{VUZ}"''')
    res = cursor.fetchall()
    str_city = str(res[0])
    str_city = str_city[2:len(str_city)-3]
    form_filter.city.setCurrentText(str_city)
    cursor.close()
    conn.close()
    filter_Save_func()
    form_filter.VUZ.setCurrentText(VUZ)

def save_for_filter_tmp():
    save_for_filter("НИР")
    fill_combobox_table_name_in_filter()

def union_tables():
    new_table = form_filter.table_name.text()
    if new_table == "":
        form_filter.label_name.setStyleSheet("color: red;")
        form_filter.label_name.setText("Ошибка! Введите имя таблицы")
        return
    old_table_name = form_filter.union_new_table.currentText()
    if old_table_name == "":
        form_filter.label_name.setStyleSheet("color: red;")
        form_filter.label_name.setText("Ошибка! Выберите таблицу")
        return
    form_filter.label_name.setStyleSheet("color: black;")
    form_filter.label_name.setText("")

    flag = 0
    if new_table == old_table_name:
        new_table = new_table + "1"
        flag = 1

    check_table_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{new_table}'"
    query = QSqlQuery(db)
    if query.exec(check_table_query):
        if query.first():
            db.close()
            conn = sqlite3.connect('SYBD.db')
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE '{new_table}'")
            cursor.close()
            conn.close()
            db.open()

    table_name = "НИР"
    request = get_filter()
    query_str = ""
    if request == "":
        query_str = f'CREATE TABLE "{new_table}" AS SELECT {table_name}.[код ВУЗа], {table_name}.[ВУЗ кратко], {table_name}.[Форма орг-и], {table_name}.[рег. номер], {table_name}.[проект], {table_name}.[код ГРНТИ], {table_name}.[руководитель], {table_name}.[должность рук.], {table_name}.[наличие экспаната], {table_name}.[выставка], {table_name}.[название экспаната] FROM {table_name} INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = {table_name}.[код ВУЗа];'
        query.exec(query_str)
    else:
        tmp_table_name = "tmp_" + new_table
        request = request.replace("AND", "", 1)
        query_str = f'CREATE TABLE "{tmp_table_name}" AS SELECT {table_name}.[код ВУЗа], {table_name}.[ВУЗ кратко], {table_name}.[Форма орг-и], {table_name}.[рег. номер], {table_name}.[проект], {table_name}.[код ГРНТИ], {table_name}.[руководитель], {table_name}.[должность рук.], {table_name}.[наличие экспаната], {table_name}.[выставка], {table_name}.[название экспаната] FROM {table_name} INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = {table_name}.[код ВУЗа] WHERE {request};'
        query.exec(query_str)
        query.exec(f'CREATE TABLE "{new_table}" AS SELECT * FROM "{tmp_table_name}" UNION SELECT * FROM "{old_table_name}"')
        db.close()
        conn = sqlite3.connect('SYBD.db')
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE '{tmp_table_name}'")
        cursor.close()
        conn.close()
        db.open()

    if flag == 1:
        dr = new_table
        new_table = new_table[0:len(new_table)-1]
        db.close()
        conn = sqlite3.connect('SYBD.db')
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE '{new_table}'")
        cursor.execute(f'CREATE TABLE "{new_table}" AS SELECT * FROM {dr}')
        cursor.execute(f"DROP TABLE '{dr}'")
        cursor.close()
        conn.close()
        db.open()
    form_filter.label_name.setText("Таблицы объединены")

def Filter():
    window_filer.show()
    fill_combobox_for_filer('фед. округ', 'federal_district', "")
    fill_combobox_for_filer('область', 'region', '')
    fill_combobox_for_filer('город', 'city', '')
    fill_combobox_for_filer('ВУЗ кратко', 'VUZ', '')
    if form_filter.vyst.count() == 0:
        form_filter.vyst.addItems([None, 'Есть', 'Нет', 'Планируется'])
    fill_combobox_table_name_in_filter()

    form_filter.federal_district.currentTextChanged.connect(func_for_federal_district)
    form_filter.VUZ.currentTextChanged.connect(func_for_VUZ)
    form_filter.region.currentTextChanged.connect(func_for_region)
    form_filter.city.currentTextChanged.connect(func_for_city)
    form_filter.vyst.currentTextChanged.connect(filter_Save_func)

    form_filter.union_button.clicked.connect(union_tables)
    form_filter.button_ok.clicked.connect(filter_Save_func)
    form_filter.save.clicked.connect(save_for_filter_tmp)
    form_filter.Button_Cancel.clicked.connect(filter_cancel_for_main)

#############################################################################################
#############################################################################################
#############################################################################################

current_table_name = ""

def filter_cancel_for_table():
    form_filter.button_ok.clicked.disconnect(filter_Save_func)
    form_filter.save.clicked.disconnect(save_for_filter_table)
    form_filter.Button_Cancel.clicked.disconnect(filter_cancel_for_table)
    form_filter.federal_district.setEnabled(True)
    form_filter.region.setEnabled(True)
    form_filter.city.setEnabled(True)
    form_filter.VUZ.setEnabled(True)
    filter_cancel()

def save_for_filter_table():
    save_for_filter(current_table_name)
    fill_combobox_table_name_in_filter()

def Filter_for_table():
    global current_table_name
    current_table_name = form.CMB_table_name.currentText()
    if current_table_name == "":
        return
    form_filter.table_name.setText(current_table_name)
    window_filer.show()
    fill_combobox_table_name_in_filter()
    fill_combobox_for_filer('фед. округ', 'federal_district', "")
    fill_combobox_for_filer('область', 'region', '')
    fill_combobox_for_filer('город', 'city', '')
    fill_combobox_for_filer('ВУЗ кратко', 'VUZ', '')
    if form_filter.vyst.count() == 0:
        form_filter.vyst.addItems([None, 'Есть', 'Нет', 'Планируется'])

    form_filter.federal_district.currentTextChanged.connect(func_for_federal_district)
    form_filter.VUZ.currentTextChanged.connect(func_for_VUZ)
    form_filter.region.currentTextChanged.connect(func_for_region)
    form_filter.city.currentTextChanged.connect(func_for_city)
    form_filter.vyst.currentTextChanged.connect(filter_Save_func)

    fill_filter_table()
    form_filter.union_button.clicked.connect(union_tables)
    form_filter.button_ok.clicked.connect(filter_Save_func)
    form_filter.save.clicked.connect(save_for_filter_table)
    form_filter.Button_Cancel.clicked.connect(filter_cancel_for_table)

def fill_filter_table():
    table_name = current_table_name
    conn = sqlite3.connect('SYBD.db')
    cursor = conn.cursor()
    cursor.execute(f'''SELECT distinct "ВУЗ кратко" FROM "{table_name}"''')
    res = cursor.fetchall()
    if len(res) == 1:
        VUZ = str(res[0])
        VUZ = VUZ[2:len(VUZ)-3]
        form_filter.VUZ.setCurrentText(VUZ)
        cursor.close()
        conn.close()
        form_filter.federal_district.setEnabled(False)
        form_filter.region.setEnabled(False)
        form_filter.city.setEnabled(False)
        form_filter.VUZ.setEnabled(False)
        return
    cursor.execute(f'''SELECT distinct ВУЗы."город" FROM "{table_name}" INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = {table_name}.[код ВУЗа]''')
    res = cursor.fetchall()
    if len(res) == 1:
        city = str(res[0])
        city = city[2:len(city)-3]
        form_filter.city.setCurrentText(city)
        cursor.close()
        conn.close()
        form_filter.federal_district.setEnabled(False)
        form_filter.region.setEnabled(False)
        form_filter.city.setEnabled(False)
        return
    cursor.execute(f'''SELECT distinct ВУЗы."область" FROM "{table_name}" INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = {table_name}.[код ВУЗа]''')
    res = cursor.fetchall()
    if len(res) == 1:
        region = str(res[0])
        region = region[2:len(region)-3]
        form_filter.region.setCurrentText(region)
        form_filter.federal_district.setEnabled(False)
        form_filter.region.setEnabled(False)
        cursor.close()
        conn.close()
        return
    cursor.execute(f'''SELECT distinct ВУЗы."фед. округ" FROM "{table_name}" INNER JOIN ВУЗы ON ВУЗы.[код ВУЗа] = {table_name}.[код ВУЗа]''')
    res = cursor.fetchall()
    if len(res) == 1:
        federal_district = str(res[0])
        federal_district = federal_district[2:len(federal_district)-3]
        form_filter.federal_district.setCurrentText(federal_district)
        form_filter.federal_district.setEnabled(False)
        cursor.close()
        conn.close()
        return
    cursor.close()
    conn.close()

#############################################################################################
#############################################################################################
#############################################################################################

#Главная часть
# Подключение к БД
db_name = 'SYBD.db'
db = connect_db(db_name)
if not db:
    sys.exit(-1)
else:
    print("connection ok")

app = QApplication([])
# Основное окно
Form, Window = uic.loadUiType("MF.ui")
window = Window()
form = Form()
form.setupUi(window)
# new_tables = []
# fill()

# form.new_table_combobox.addItems([None])
# form.new_table_combobox.addItems(new_tables)

# Окно для подтвержения удаления
Form_row_deletion_confirmation, Window_row_deletion_confirmation = uic.loadUiType("row_deletion_confirmation.ui")
window_row_deletion = Window_row_deletion_confirmation()
form_row_deletion = Form_row_deletion_confirmation()
form_row_deletion.setupUi(window_row_deletion)

# окно-сообщение что строка для удаления/изменения не выделена
Form_message_select_row, Window_message_select_row = uic.loadUiType("message_row_selection.ui")
window_message_select_row = Window_message_select_row()
form_message_select_row = Form_message_select_row()
form_message_select_row.setupUi(window_message_select_row)

# Окно для редактирования, вставления строки
Form_row_add, Window_row_add = uic.loadUiType("insert_row.ui")
window_row_add = Window_row_add()
form_row_add = Form_row_add()
form_row_add.setupUi(window_row_add)

# Окно для сообщения, что данные для вставления в строку в таблицу введены не верно
Form_message_add_row, Window_message_add_row = uic.loadUiType("message_add_row.ui")
window_message_add_row = Window_message_add_row()
form_message_add_row = Form_message_add_row()
form_message_add_row.setupUi(window_message_add_row)

# Окно для добавления фильрации
Form_table_delate, Window_table_delate = uic.loadUiType("table_delete.ui")
window_table_delate = Window_table_delate()
form_table_delate = Form_table_delate()
form_table_delate.setupUi(window_table_delate)

# Окно для добавления фильрации
Form_filter, Window_filter = uic.loadUiType("filter.ui")
window_filer = Window_filter()
form_filter = Form_filter()
form_filter.setupUi(window_filer)


# Ширина столбцов для отображения таблицы
NIR_COLUMN_WIDTH = (70, 100, 40, 70, 300, 120, 120, 140, 100, 300, 300)
VUZ_COLUMN_WIDTH = (70, 200, 300, 100, 140, 150, 140, 100, 200, 70, 70)
GRNTI_COLUMN_WIDTH = (50, 450)


main_functions()

window.show()
app.exec()
