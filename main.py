import sys
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QMainWindow, QLabel, QTableWidget, QTableWidgetItem


class Registration(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(800, 300, 300, 300)
        self.setWindowTitle('Регистрация')

        self.btn = QPushButton('Вход', self)
        self.btn.resize(100, 50)
        self.btn.move(100, 100)

        self.btn.clicked.connect(self.open_second_form)

    def open_second_form(self):
        self.second_form = SecondForm(self, "Добро пожаловать...")
        self.second_form.show()
        self.close()


class Error(QWidget):
    def __init__(self, *error_text):
        super().__init__()
        self.initUI(error_text)

    def initUI(self, error_text):
        self.setGeometry(800, 300, 300, 100)
        self.setWindowTitle('Ошибка')

        self.lb = QLabel(self)
        # self.lb.resize(100, 50)
        self.lb.move(20, 30)
        self.lb.setText(f'Ошибка: {error_text[-1]}')


class SecondForm(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('table.ui', self)
        self.initUI(args)

    def initUI(self, args):
        self.setWindowTitle('Окно таблицы')

        self.connection = sqlite3.connect("food.db")

        # Вывод данных с первого окна
        self.lbl = QLabel(args[-1], self)
        self.lbl.move(10, 10)
        self.lbl.adjustSize()

        # ComboBox
        cur = self.connection.cursor()
        t = ['Всё']
        for i in [i[0] for i in cur.execute("""SELECT name FROM type""").fetchall()]:
            t.append(i)
        self.comboBox.addItems(t)
        self.item = False

        # Button "НАЙТИ"
        self.pushButton.clicked.connect(self.reform_table)

        # Задаём значения для таблиц
        self.defualt = """SELECT
                dishes.name,
                dishes.kalori,
                dishes.protein,
                dishes.fats,
                dishes.carb,
                type.id
            FROM
                dishes_type
            LEFT JOIN dishes ON dishes_type.id_dishes = dishes.id
            LEFT JOIN type ON dishes_type.id_type = type.id"""

        self.query = self.defualt

        # Отображаем всю таблицу
        self.select_data()

    def reform_table(self):
        # Создаём нужные переменные
        new_win = False
        fats, carbs, proteins, kaloris = '', '', '', ''

        # Проверка на правельный ввод данных в QLineEdit
        try:
            # Проверка на отрицательность
            if self.linef.text():
                fats = int(self.linef.text())
                if fats < 0:
                    new_win = True
            if self.linec.text():
                carbs = int(self.linec.text())
                if carbs < 0:
                    new_win = True
            if self.linep.text():
                proteins = int(self.linep.text())
                if proteins < 0:
                    new_win = True
            if self.linek.text():
                kaloris = int(self.linek.text())
                if kaloris < 0:
                    new_win = True
        except ValueError:
            # Вывод ошибки, если введено строковое значение или не целого числа
            self.error = Error(self, "Введено строковое значение или не целое, \nа нужно натуральное или ноль!!!")
            self.error.show()

        if new_win:
            # Вывод ошибки, если введено отрицательное число
            self.new_win = False
            self.error = Error(self, "Введено отрицытельное значение, \nа не натуральное или ноль!!!")
            self.error.show()
        else:
            # Выбранный элемент ComboBox
            self.item = self.comboBox.currentText()

            if self.item == 'Всё':
                self.query = self.defualt
            else:
                self.query = f"""SELECT
                    dishes.name,
                    dishes.kalori,
                    dishes.protein,
                    dishes.fats,
                    dishes.carb,
                    type.id
                FROM
                    dishes_type
                LEFT JOIN dishes ON dishes_type.id_dishes = dishes.id
                LEFT JOIN type ON dishes_type.id_type = type.id
                WHERE type.name = '{self.item}'"""

            cursor = self.connection.cursor()
            res = cursor.execute(self.query).fetchall()

            def making_num(comp, n):
                need = ''
                num = -1
                for i in res:
                    if abs(int(i[n]) - comp) <= num or num == -1:
                        need = int(i[n])
                        num = abs(int(i[n]) - comp)
                
                return need

            need_k = -1
            need_f = -1
            need_c = -1
            need_p = -1

            if kaloris:
                need_k = making_num(kaloris, n=1)

            if carbs:
                need_c = making_num(carbs, n=4)
            
            if proteins:
                need_p = making_num(proteins, n=2)

            if fats:
                need_f = making_num(fats, n=3)

            if self.item != 'Всё':
                if need_k == -1 and need_f == -1 and need_c == -1 and need_p == -1:
                    pass
                else:
                    self.query = f"""SELECT
                        dishes.name,
                        dishes.kalori,
                        dishes.protein,
                        dishes.fats,
                        dishes.carb,
                        type.id
                    FROM
                        dishes_type
                    LEFT JOIN dishes ON dishes_type.id_dishes = dishes.id
                    LEFT JOIN type ON dishes_type.id_type = type.id
                    WHERE type.name = '{self.item}' AND dishes.kalori = {need_k} OR dishes.protein = {need_p} OR dishes.carb = {need_c} OR dishes.fats = {need_f}"""
            else:
                # Не Всё
                if need_k == -1 and need_f == -1 and need_c == -1 and need_p == -1:
                    self.query = self.defualt
                else:
                    self.query = f"""SELECT
                        dishes.name,
                        dishes.kalori,
                        dishes.protein,
                        dishes.fats,
                        dishes.carb,
                        type.id
                    FROM
                        dishes_type
                    LEFT JOIN dishes ON dishes_type.id_dishes = dishes.id
                    LEFT JOIN type ON dishes_type.id_type = type.id
                    WHERE dishes.kalori = {need_k} OR dishes.protein = {need_p} OR dishes.carb = {need_c} OR dishes.fats = {need_f}"""

        self.select_data()

    def select_data(self):
        # Создание таблицы
        res = list(set(self.connection.cursor().execute(self.query).fetchall()))

        # Проверка на отсутствие элементов в res
        if not res:
            self.tableWidget.setColumnCount(0)
        else:
            self.tableWidget.setColumnCount(len(res[0]))
        self.tableWidget.setRowCount(0)

        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

        self.tableWidget.setColumnWidth(1, 164)
        self.tableWidget.setColumnWidth(2, 50)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Калории', 'Белки', 'Жиры', 'Углеводы', 'Тип'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Registration()
    ex.show()
    sys.exit(app.exec())