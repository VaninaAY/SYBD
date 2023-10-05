# This is a sample Python script.
import sys
from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QAbstractItemView
from PyQt6.QtSql import *
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt



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
    # currentIndex = form.table_NIR.currentIndex()
    # if currentIndex.isValid():
    if selected_rows_indexes:
        window_row_deletion.show()
        form_row_deletion.Button_delete.clicked.connect(lambda: deleteRow(selected_rows_indexes))
        form_row_deletion.Button_cancel.clicked.connect(window_row_deletion.close)

    else:
        window_message_delete_row.show()
        # form_message.label_message.label.setAlignment(QtCore.Qt.AlignVCenter)   # Выравнивание по центру, которое не работает
        form_message_delete_row.Button_ok.clicked.connect(window_message_delete_row.close)


# Подключение к БД
db_name = 'SYBD.db'
if not connect_db(db_name):
    sys.exit(-1)
else:
    print("connection ok")


Form, Window = uic.loadUiType("MainForm.ui")
Form_row_deletion_confirmation, Window_row_deletion_confirmation = uic.loadUiType("row_deletion_confirmation.ui")
Form_message_delete_row, Window_message_delete_row = uic.loadUiType("message_delete_row.ui")

app = QApplication([])
# Основное окно
window = Window()
form = Form()
form.setupUi(window)

# Окно для подтвержения удаления
window_row_deletion = Window_row_deletion_confirmation()
form_row_deletion = Form_row_deletion_confirmation()
form_row_deletion.setupUi(window_row_deletion)

# окно-сообщение что строка для удаления не выделена
window_message_delete_row = Window_message_delete_row()
form_message_delete_row = Form_message_delete_row()
form_message_delete_row.setupUi(window_message_delete_row)

# Ширина столбцов для отображения таблицы
NIR_COLUMN_WIDTH = (50, 120, 120, 130, 140, 150, 180, 140, 100, 100, 100)
VUZ_COLUMN_WIDTH = (50, 120, 120, 130, 140, 150, 180, 140, 100, 100, 100)
GRNTI_COLUMN_WIDTH = (50, 500)

show_table('НИР', "table_NIR", NIR_COLUMN_WIDTH)
show_table('ВУЗы', "table_VUZ", VUZ_COLUMN_WIDTH)
show_table('ГРНТИ', "table_GRNTI", GRNTI_COLUMN_WIDTH)

form.Button_delete.clicked.connect(deleteSelectedRow)

# form.show_NIR.triggered.connect(show_table('NIR'))
# form.Button_delete.clicked.connect(window_del_row.show)

window.show()
app.exec()