# This is a sample Python script.
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import *


# Подклюючение к базе данных и проверка ее наличия
def connect_db(db_file):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_file)
    if not db.open():
        print("Cannot establish a database connection to {}!".format(db_file))
        return False
    return db

# Отображение таблиц
def show_table(tbl_name, widget_name, column_width):
    table = QSqlTableModel()
    table.setTable(tbl_name)
    table.select()
    getattr(form, widget_name).setModel(table)
    getattr(form, widget_name).setSortingEnabled(True)
    for num_column, width in enumerate(column_width):
        getattr(form, widget_name).setColumnWidth(num_column, width)


# Функции удаления строки
def deleteRow(Indexes):
    for index in Indexes:
        form.table_NIR.model().removeRow(index)
    show_table('НИР', "table_NIR", NIR_COLUMN_WIDTH)
    window_row_deletion.close()


def deleteSelectedRow():
    selected_rows = form.table_NIR.selectionModel().selectedRows()
    selected_rows_indexes = [index.row() for index in selected_rows]
    if selected_rows_indexes:
        window_row_deletion.show()
        form_row_deletion.Button_delete.clicked.connect(lambda: deleteRow(selected_rows_indexes))
        form_row_deletion.Button_cancel.clicked.connect(window_row_deletion.close)

    else:
        window_message_select_row.show()
        form_message_select_row.Button_ok.clicked.connect(window_message_select_row.close)


# Обработка combox для кода ВУЗа и краткого названия, чтобы автоматически подтягивались значения
def processing_combobox(widget_disabled):
    def a(index):
        getattr(form_row_add, widget_disabled).setEditable(False)
        getattr(form_row_add, widget_disabled).setCurrentIndex(index)
    return a


# Заполняем комбо боксы значениями, полученные из БД
def fill_combobox(column, table, widget):
    query = QSqlQuery()
    query.exec(f'SELECT DISTINCT "{column}" FROM {table}')
    distinct_values = [None]
    getattr(form_row_add, widget).clear()
    while query.next():
        distinct_values.append(str(query.value(0)))
    getattr(form_row_add, widget).addItems(distinct_values)


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


# Очищение строк и комбобоксов при нажатии кнопки сброс
def reset_form_adding_row():
    lst_combobox = ['comboBox_codvuz', 'comboBox_z2', 'comboBox_type', 'comboBox_exhitype']
    for combobox in lst_combobox:
        getattr(form_row_add, combobox).setCurrentIndex(0)
    lst_lineEdit = ['lineEdit_regnum', 'lineEdit_subject', 'lineEdit_grnti1_1', 'lineEdit_grnti1_2',
                    'lineEdit_grnti1_3', 'lineEdit_grnti2_1', 'lineEdit_grnti2_2', 'lineEdit_grnti2_3',
                    'lineEdit_bossname', 'lineEdit_bosstitle', 'lineEdit_vystavki', 'lineEdit_exponat']
    for lineEdit in lst_lineEdit:
        getattr(form_row_add, lineEdit).clear()

def reset_form_chengin_row():
    form_row_add.comboBox_exhitype.setCurrentIndex(0)
    lst_lineEdit = ['lineEdit_subject', 'lineEdit_grnti1_1', 'lineEdit_grnti1_2',
                    'lineEdit_grnti1_3', 'lineEdit_grnti2_1', 'lineEdit_grnti2_2',
                    'lineEdit_grnti2_3', 'lineEdit_bossname', 'lineEdit_bosstitle',
                    'lineEdit_vystavki', 'lineEdit_exponat']
    for lineEdit in lst_lineEdit:
        getattr(form_row_add, lineEdit).clear()

def row_validation():
    # проверка, на то что все значения в норме
    lst_combobox = ['comboBox_codvuz', 'comboBox_z2', 'comboBox_type', 'comboBox_exhitype']
    lst_lineEdit_must_be_field = ['lineEdit_regnum', 'lineEdit_subject', 'lineEdit_grnti1_1', 'lineEdit_grnti1_2',
                                  'lineEdit_bossname']
    # Проверка, что комбобокс заполнен
    for combobox in lst_combobox:
        if getattr(form_row_add, combobox).currentIndex() == 0:
            return False, None

    # Проверка, что тектовый редактор заполнены
    for lineEdit in lst_lineEdit_must_be_field:
        if getattr(form_row_add, lineEdit).text() == '':
            return False, None

    # Проверка на первичный ключ - не работает
    # query = QSqlQuery()
    #
    # print('запрос')
    # print(query.executedQuery())
    # query.prepare('''SELECT * FROM my_table WHERE "код ВУЗа" = :val1 AND НТП = :val2 AND 'рег. номер' = :val3''')
    # query.bindValue(":val1", int(form_row_add.comboBox_codvuz.currentText()))
    # query.bindValue(":val2", form_row_add.comboBox_type.currentText())
    # query.bindValue(":val3", form_row_add.lineEdit_regnum.text())
    #
    # if query.exec() and query.next():
    #         print('ключ не прошел проверку')
    #         return False

    # Проверка последних 2-ух полей с выставкой
    if form_row_add.comboBox_exhitype.currentText() != 'Нет':
        for lineEdit in ['lineEdit_vystavki', 'lineEdit_exponat']:
            if getattr(form_row_add, lineEdit).text() == '':
                return False, None

    # проверка кода грнти
    cod_grnti = [form_row_add.lineEdit_grnti1_1.text(), form_row_add.lineEdit_grnti1_2.text(),
                 form_row_add.lineEdit_grnti1_3.text(),
                 form_row_add.lineEdit_grnti2_1.text(), form_row_add.lineEdit_grnti2_2.text(),
                 form_row_add.lineEdit_grnti2_3.text()]

    for num in cod_grnti:
        if not ((num.isnumeric() and len(num) == 2) or num == ''):
            return False, None
    if len(cod_grnti[0]) == 2 and len(cod_grnti[1]) == 2:
        total_cod_grnti = cod_grnti[0] + '.' + cod_grnti[1]
        if len(cod_grnti[2]) == 2:
            total_cod_grnti += '.' + cod_grnti[2]
            if len(cod_grnti[3]) == 2 and len(cod_grnti[4]) == 2:
                total_cod_grnti += ';' + cod_grnti[3] + '.' + cod_grnti[4]
            elif not (len(cod_grnti[3]) == 0 and len(cod_grnti[4]) == 0 and len(cod_grnti[5]) == 0):
                return False, None
        else:
            if len(cod_grnti[3]) == 2 and len(cod_grnti[4]) == 2:
                total_cod_grnti += ';' + cod_grnti[3] + '.' + cod_grnti[4]
            elif not (len(cod_grnti[3]) == 0 and len(cod_grnti[4]) == 0 and len(cod_grnti[5]) == 0):
                return False, None
        if len(cod_grnti[5]) == 2:
            total_cod_grnti += '.' + cod_grnti[5]
    else:
        return False, None
    return True, total_cod_grnti

def insert_row_in_bd():
    flag, codGRNTI = row_validation()
    if flag:
        exhitype = form_row_add.comboBox_exhitype.currentText()[0]

        values_new_row = [form_row_add.comboBox_codvuz.currentText(), form_row_add.comboBox_z2.currentText(),
                          form_row_add.comboBox_type.currentText(), form_row_add.lineEdit_regnum.text(),
                          form_row_add.lineEdit_subject.text(), codGRNTI, form_row_add.lineEdit_bossname.text(),
                          form_row_add.lineEdit_bosstitle.text(), exhitype,
                          form_row_add.lineEdit_vystavki.text(), form_row_add.lineEdit_exponat.text()]

        values_new_row = tuple(values_new_row)
        query = QSqlQuery()
        query.exec(f'''INSERT INTO НИР VALUES {values_new_row}''')

        show_table('НИР', "table_NIR", NIR_COLUMN_WIDTH)

        close_form_row_add()


        # подсветить вставленную строку

    else:
        window_message_add_row.show()
        form_message_add_row.Button_ok.clicked.connect(window_message_add_row.close)

def close_form_row_add():
    reset_form_adding_row()

    form_row_add.Button_add.clicked.disconnect()
    form_row_add.Button_add.clicked.connect(nothing)
    form_row_add.Button_reset.clicked.disconnect()
    form_row_add.Button_reset.clicked.connect(nothing)

    window_row_add.close()


def AddRow():
    window_row_add.show()
    reset_form_adding_row()
    form_row_add.Button_cancel.clicked.connect(close_form_row_add)

    form_row_add.Button_add.clicked.disconnect(nothing)
    form_row_add.Button_add.clicked.connect(insert_row_in_bd)

    form_row_add.Button_reset.clicked.disconnect(nothing)
    form_row_add.Button_reset.clicked.connect(reset_form_adding_row)

    fill_combobox('код ВУЗа','ВУЗы', 'comboBox_codvuz')
    fill_combobox('ВУЗ кратко', 'ВУЗы', 'comboBox_z2')

    form_row_add.comboBox_codvuz.activated.connect(processing_combobox('comboBox_z2'))
    form_row_add.comboBox_z2.activated.connect(processing_combobox('comboBox_codvuz'))

    fill_combobox('НТП', 'НИР', 'comboBox_type')
    form_row_add.comboBox_codvuz.setEnabled(True)
    form_row_add.comboBox_z2.setEnabled(True)
    form_row_add.comboBox_type.setEnabled(True)
    form_row_add.lineEdit_regnum.setReadOnly(False)

    form_row_add.comboBox_exhitype.clear()
    form_row_add.comboBox_exhitype.addItems([None, 'Есть', 'Нет', 'Планируется'] )
    form_row_add.comboBox_exhitype.activated.connect(exhibition_processing)
def update_row_in_bd():
    flag, codGRNTI = row_validation()
    if flag:
        exhitype = form_row_add.comboBox_exhitype.currentText()[0]

        values_new_row = [form_row_add.comboBox_codvuz.currentText(), form_row_add.comboBox_z2.currentText(),
                          form_row_add.comboBox_type.currentText(), form_row_add.lineEdit_regnum.text(),
                          form_row_add.lineEdit_subject.text(), codGRNTI, form_row_add.lineEdit_bossname.text(),
                          form_row_add.lineEdit_bosstitle.text(), exhitype,
                          form_row_add.lineEdit_vystavki.text(), form_row_add.lineEdit_exponat.text()]

        values_new_row = tuple(values_new_row)

        query = QSqlQuery()
        query.exec(f"""UPDATE НИР SET "ВУЗ кратко" = "{values_new_row[1]}", проект = "{values_new_row[4]}",  "код ГРНТИ" = "{values_new_row[5]}", 
                    руководитель = "{values_new_row[6]}", "должность рук." = "{values_new_row[7]}",
                    "наличие экспаната" = "{values_new_row[8]}", выставка = "{values_new_row[9]}", "название экспаната" = "{values_new_row[10]}"
                    WHERE "код ВУЗа" = "{values_new_row[0]}"  AND НТП = "{values_new_row[2]}" AND "рег. номер" = "{values_new_row[3]}"
                    """)

        show_table('НИР', "table_NIR", NIR_COLUMN_WIDTH)

        reset_form_adding_row()
        window_row_add.close()

        close_form_row_add()

    else:
        window_message_add_row.show()
        form_message_add_row.Button_ok.clicked.connect(window_message_add_row.close)



def ChangeRow():
    selected_row = form.table_NIR.selectedIndexes()
    if selected_row:
        window_row_add.show()
        reset_form_adding_row()

        form_row_add.Button_cancel.clicked.connect(close_form_row_add)

        form_row_add.Button_add.clicked.disconnect(nothing)
        form_row_add.Button_add.clicked.connect(update_row_in_bd)


        form_row_add.Button_reset.clicked.disconnect(nothing)
        form_row_add.Button_reset.clicked.connect(reset_form_chengin_row)

        data = []
        for index in selected_row:
            data.append(form.table_NIR.model().data(index))

        fill_combobox('код ВУЗа', 'ВУЗы', 'comboBox_codvuz')
        fill_combobox('ВУЗ кратко', 'ВУЗы', 'comboBox_z2')
        fill_combobox('НТП', 'НИР', 'comboBox_type')

        form_row_add.comboBox_codvuz.setCurrentText(str(data[0]))
        form_row_add.comboBox_z2.setCurrentText(data[1])
        form_row_add.comboBox_type.setCurrentText(data[2])

        form_row_add.comboBox_codvuz.setEnabled(False)
        form_row_add.comboBox_z2.setEnabled(False)
        form_row_add.comboBox_type.setEnabled(False)

        form_row_add.lineEdit_regnum.setText(data[3])
        form_row_add.lineEdit_regnum.setReadOnly(True)

        data_grnti = []
        grnti = data[5].split(';')
        for i in grnti:
            num = i.split('.')
            if len(num) == 2:
                num.append('')
        data_grnti.extend(num)
        if len(data_grnti) != 6:
            data_grnti.extend(['', '', ''])

        data4_10 = [data[4]] + data_grnti + data[6:8] + data[9:]
        lst_line_EDITOR = ['lineEdit_subject', 'lineEdit_grnti1_1', 'lineEdit_grnti1_2', 'lineEdit_grnti1_3',
                           'lineEdit_grnti2_1', 'lineEdit_grnti2_2', 'lineEdit_grnti2_3', 'lineEdit_bossname',
                           'lineEdit_bosstitle', 'lineEdit_vystavki', 'lineEdit_exponat']

        # getattr(form_row_add, lst_line_EDITOR[0]).setText(data4_10[0])
        for i in range(len(lst_line_EDITOR)):
            getattr(form_row_add, lst_line_EDITOR[i]).setText(data4_10[i])

        form_row_add.comboBox_exhitype.clear()
        form_row_add.comboBox_exhitype.addItems([None, 'Есть', 'Нет', 'Планируется'])
        if data[8] == 'Е':
            data[8] = 'Есть'
        elif data[8] == 'Н':
            data[8] = 'Нет'
        else:
            data[8] = 'Планируется'
        # form_row_add.comboBox_exhitype.activated.connect(exhibition_processing)
        form_row_add.comboBox_exhitype.setCurrentText(data[8])
        if form_row_add.comboBox_exhitype.currentText() == 'Нет':
            form_row_add.lineEdit_vystavki.setReadOnly(True)
            form_row_add.lineEdit_exponat.setReadOnly(True)
        form_row_add.comboBox_exhitype.activated.connect(exhibition_processing)

    else:
        window_message_select_row.show()
        form_message_select_row.Button_ok.clicked.connect(window_message_select_row.close)

def nothing():
    pass



#Главная часть
# Подключение к БД
db_name = 'SYBD.db'
if not connect_db(db_name):
    sys.exit(-1)
else:
    print("connection ok")

app = QApplication([])
# Основное окно
Form, Window = uic.loadUiType("MainForm.ui")
window = Window()
form = Form()
form.setupUi(window)

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

# Ширина столбцов для отображения таблицы
NIR_COLUMN_WIDTH = (70, 100, 40, 70, 300, 120, 120, 140, 100, 300, 300)
VUZ_COLUMN_WIDTH = (70, 200, 300, 100, 140, 150, 140, 100, 200, 70, 70)
GRNTI_COLUMN_WIDTH = (50, 450)


show_table('НИР', "table_NIR", NIR_COLUMN_WIDTH)
show_table('ВУЗы', "table_VUZ", VUZ_COLUMN_WIDTH)
show_table('ГРНТИ', "table_GRNTI", GRNTI_COLUMN_WIDTH)

form.Button_delete.clicked.connect(deleteSelectedRow)
form.Button_add.clicked.connect(AddRow)
form.Button_change.clicked.connect(ChangeRow)

form_row_add.Button_reset.clicked.connect(nothing)
form_row_add.Button_add.clicked.connect(nothing)

def close_event(event):
    close_form_row_add()
    event.accept()

window_row_add.closeEvent = close_event



window.show()
app.exec()