import sys, os, shutil
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, QVBoxLayout
from PyQt5.QtWidgets import QMainWindow, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


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


class DelForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('DelForm.ui', self)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Окно удаления')

        # Связь с таблицей
        self.connection = sqlite3.connect("food.db")

        # Button
        self.btn.clicked.connect(self.deleting)

    def deleting(self):
        text = self.line.text()

        # Все имена блюд
        cur = self.connection.cursor()
        names = cur.execute("""SELECT name FROM dishes""")
        names = [i[0] for i in names]

        # Проверка на соответствие имени в блюдах
        if text not in names:
            self.error = Error(self, "Данного блюда нет в таблице!")
            self.error.show()
        else:
            id_receipt = cur.execute("""SELECT receipt FROM dishes
                WHERE name = ?""", (text,)).fetchone()
            id_dishes = cur.execute("""SELECT id FROM dishes
                WHERE name = ?""", (text,)).fetchone()
            
            # Удаление нужных строк
            cur.execute("""DELETE from receipt
                WHERE id = ?""", (id_receipt[0],))
            cur.execute("""DELETE from dishes
                WHERE id = ?""", (id_dishes[0],))
            cur.execute("""DELETE from dishes_type
                WHERE id = ?""", (id_dishes[0],))

            self.connection.commit()

        self.close()


class Photo(QLabel):
    def __init__(self):
        super().__init__()

        # Текст у окна
        self.setAlignment(Qt.AlignCenter)
        self.setText('Перенесите фотографию в это окно')

    def setPhoto(self, photo):
        # Выставление фотографии
        super().setPixmap(photo)


class PhotoForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Окно фотографии')
        self.resize(300, 300)
        self.setAcceptDrops(True)

        self.file_path = ''

        # Место для фотографии
        layout = QVBoxLayout()

        # Фотография
        self.photo = Photo()

        # Добавляем фотографию
        layout.addWidget(self.photo)

        # Сохраняем изменения
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        # Проверка на присутствие фотографии
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        # Проверка на присутствие фотографии
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # Загружаем фото
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            # Путь файла
            self.file_path = event.mimeData().urls()[0].toLocalFile()
            self.path()

            event.accept()
            self.close()
        else:
            event.ignore()

    def path(self):
        return self.file_path

    def set_image(self, file_path):
        self.photo.setPixmap(QPixmap(file_path))


class AddingForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('AddForm.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Окно добавления')

        self.photo = ''

        # Связь с таблицей
        self.connection = sqlite3.connect("food.db")

        # ComboBox
        cur = self.connection.cursor()
        t = []
        for i in [i[0] for i in cur.execute("""SELECT name FROM type""").fetchall()]:
            t.append(i)
        self.comboBox.addItems(t)
        self.item = False

        # Button
        self.btn.clicked.connect(self.adding)
        self.btn_addphoto.clicked.connect(self.add_photo)

    def add_photo(self):
        self.photo = PhotoForm(self)
        self.photo.show()

    def adding(self):
        # Создаём нужные переменные\
        name_text = self.linean.text()
        ingr_text = self.linei.text()
        fats = self.linef.text()
        carbs = self.linec.text()
        proteins = self.linep.text()
        kaloris = self.linek.text()
        new_win = False
        nothing = False

        # переменные имён и ингредиентов
        s_inger = [i for i in ingr_text.split('; ')]
        names = self.connection.cursor().execute("""SELECT name FROM dishes""")
        names = [i[0] for i in names]

        # Проверка имени
        if not name_text or ''.join(''.join(''.join(name_text.split(' ')).split('.')).split(',')).isdigit():
            self.error = Error(self, "Введено число или ничего, а не строка \nв названии!!!")
            self.error.show()
        elif name_text in names:
            self.error = Error(self, "Такое название уже есть в таблице!!!")
            self.error.show()
        else:
            # Проверка ингредиентов
            if ''.join(s_inger).isdigit() or not ingr_text or ''.join(''.join(''.join(ingr_text.split(' ')).split('.')).split(',')).isdigit():
                self.error = Error(self, "Введено число или ничего, а не строка \nв ингредиентах!!!")
                self.error.show()
            else:
                try:
                    # Проверка на отрицательность и присутствия элементов
                    if fats:
                        fats = int(fats)
                        if fats < 0:
                            new_win = True
                    else:
                        nothing = True
                    if carbs:
                        carbs = int(carbs)
                        if carbs < 0:
                            new_win = True
                    else:
                        nothing = True
                    if proteins:
                        proteins = int(proteins)
                        if proteins < 0:
                            new_win = True
                    else:
                        nothing = True
                    if kaloris:
                        kaloris = int(kaloris)
                        if kaloris < 0:
                            new_win = True
                    else:
                        nothing = True
                except ValueError:
                    # Вывод ошибки, если введено строковое значение или не целого числа
                    self.error = Error(self, "Введено строковое значение или не целое, \nа нужно натуральное или ноль у характеристик!!!")
                    self.error.show()

                if new_win:
                    # Вывод ошибки, если введено отрицательное число
                    self.new_win = False
                    self.error = Error(self, "Введено отрицытельное значение, \nа не натуральное или ноль у характеристик!!!")
                    self.error.show()
                
                elif nothing:
                    # Вывод ошибки, если ничего не введено
                    nothing = False
                    self.error = Error(self, "Вы забыли ввести значение \nв поле с вводом у характеристик!")
                    self.error.show()
                else:
                    # Проверка рецепта
                    text = self.plainText.toPlainText()
                    if not text:
                        self.error = Error(self, "Вы забыли ввести рецепт блюда!!!")
                        self.error.show()
                    else:
                        try:
                            # Выбранный элемент ComboBox
                            item = self.comboBox.currentText()

                            # Добавляем фотографию, если она есть
                            name_file = ''
                            if self.photo:
                                if self.photo.path():
                                    # Перемещаем фотографию
                                    need_file = f'{os.getcwd()}/Photos'
                                    name_file = self.photo.path().split('/')[-1]
                                    shutil.move(self.photo.path(), need_file)
                            
                            # Добавление в receipt
                            s = ';'.join(s_inger)
                            cur = self.connection.cursor()
                            cur.execute(f"""INSERT INTO receipt(ingredients,receipt,photo) 
                            VALUES(?,?,?)""", (s, text, name_file))
                            self.connection.commit()

                            # Добавление в dishes
                            id_need = cur.execute("""SELECT id FROM receipt
                                WHERE receipt = ? AND ingredients = ?""", (text, s)).fetchone()

                            cur.execute(f"""INSERT INTO dishes(name, kalori, protein, fats, carb, receipt) 
                            VALUES(?, ?, ?, ?, ?, ?)""", (name_text, kaloris, proteins, fats, carbs, id_need[0]))
                            self.connection.commit()

                            # Добавление в dishes_type
                            id_type = cur.execute("""SELECT id FROM type
                                WHERE name = ?""", (item,)).fetchone()

                            id_dish = cur.execute("""SELECT id FROM dishes
                                WHERE name = ?""", (name_text,)).fetchone()

                            cur.execute(f"""INSERT INTO dishes_type(id_type, id_dishes) 
                            VALUES(?, ?)""", (id_type[0], id_dish[0]))
                            self.connection.commit()

                            self.connection.close()
                        except Exception:
                            error = Error(self, 'Неожиданная ошибка, перезагрузитесь!')
                            error.show()
        self.close()


class ChoiceForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('', self)
        self.initUI(args)
    
    def initUI(self, args):
        pass


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

        # Связь с таблицей
        self.connection = sqlite3.connect("food.db")

        # Вывод данных с первого окна
        self.lbl = QLabel(args[-1], self)
        self.lbl.move(10, 750)
        self.lbl.adjustSize()

        # ComboBox
        cur = self.connection.cursor()
        t = ['Всё']
        for i in [i[0] for i in cur.execute("""SELECT name FROM type""").fetchall()]:
            t.append(i)
        self.comboBox.addItems(t)
        self.item = False

        # Buttons
        self.btn_find1.clicked.connect(self.find1_table)
        self.btn_find2.clicked.connect(self.find2_table)
        self.btn_add.clicked.connect(self.add_element)
        self.btn_del.clicked.connect(self.del_element)
        self.btn_change.clicked.connect(self.change_element)
        self.btn_choose.clicked.connect(self.choose_element)
        self.btn_refresh.clicked.connect(self.refresh_table)

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

    def refresh_table(self):
        self.defualt = self.defualt
        self.select_data()

    def add_element(self):
        self.add_form = AddingForm(self)
        self.add_form.show()

    def del_element(self):
        self.del_form = DelForm(self)
        self.del_form.show()

    def change_element(self):
        # ДОДЕЛАТЬ!!!!! И выключить редактирование в таблице
        pass

    def choose_element(self):
        name, ok_pressed = QInputDialog.getText(self, "Введите блюда", 
                                                "Название название блюда:")
        if ok_pressed:
            if name in [i[0] for i in self.connection.cursor().execute("""SELECT name FROM dishes""").fetchall()]:
                self.choice = ChoiceForm(self, name)
                self.choice.show()
            else:
                self.error = Error(self, "Такого блюда нет в таблице!!!")
                self.error.show()

    def find1_table(self):
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

            # Подбираем нужный поиск по таблице
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

            # Выводим все нужные элементы таблицы
            cursor = self.connection.cursor()
            res = cursor.execute(self.query).fetchall()

            # Функция по нахождению наиближайшего введённого значения в таблице
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

            # Поиск подходящих значения для переменных
            if kaloris:
                need_k = making_num(kaloris, n=1)

            if carbs:
                need_c = making_num(carbs, n=4)
            
            if proteins:
                need_p = making_num(proteins, n=2)

            if fats:
                need_f = making_num(fats, n=3)

            # Поиск для таблицы, где выбран тип блюда и его доп. характеристики
            if self.item != 'Всё':
                item = cursor.execute("""SELECT id FROM type WHERE name = ?""", (self.item,)).fetchone()
                items = [i[0] for i in cursor.execute("""SELECT id_type FROM dishes_type""").fetchall()]
                if item[0] not in items:
                    # print(items)
                    self.query = """"""
                elif need_k == -1 and need_f == -1 and need_c == -1 and need_p == -1:
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
                    WHERE type.name = '{self.item}' AND (dishes.kalori = {need_k} OR dishes.protein = {need_p} OR dishes.carb = {need_c} OR dishes.fats = {need_f})"""
            else:
                # Поиск для таблицы, где выбран только тип блюда
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

    def find2_table(self):
        self.linek.setText('')
        self.linec.setText('')
        self.linep.setText('')
        self.linef.setText('')

        text = self.lineingr.text().lower().split(';')

        # Проверка на присутствие введёных значений
        if not text:
            self.query = self.defualt
            self.select_data()
        else:
            # Ингредиенты всех блюд
            cur = self.connection.cursor()
            ingredients = cur.execute("""SELECT ingredients FROM receipt""").fetchall()
            ids = []

            # Список нужных id
            for el in ingredients:
                for i in el[0].lower().split('; '):
                    for j in text:
                        # Удаление лишних пробелов
                        j = j.strip()
                        if j in i:
                            id_ingredient = cur.execute("""SELECT id FROM receipt WHERE ingredients = ?""", (el[0],)).fetchone()
                            ids.append(id_ingredient[0])
            
            # Выводим нужные блюда
            if ids:
                find = []
                for i in range(1, len(ids)):
                    find.append(f'OR dishes.receipt = {ids[i]}')
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
                    WHERE dishes.receipt = {ids[0]} {' '.join(find)}"""
            else:
                self.query = """"""
            
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