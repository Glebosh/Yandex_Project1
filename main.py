import sys, os, shutil
import sqlite3

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, QVBoxLayout
from PyQt5.QtWidgets import QMainWindow, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor


class EntryMenu(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('EntryMenuForm.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Меню входа')

        # Связь с таблицей
        self.connection = sqlite3.connect("food.db")

        # Buttons
        self.btn_ent.clicked.connect(self.entering)
        self.btn_reg.clicked.connect(self.registration)

    def entering(self):
        name = self.linen.text()
        password = self.linep.text()
        cur = self.connection.cursor()

        names = [i[0] for i in cur.execute("""SELECT name FROM registration""").fetchall()]

        # Проверка присутствия имени
        if not name or not password:
            pass
        else:
            if name in names:
                # Проверка пароля
                password_t = cur.execute("""SELECT password FROM registration
                WHERE name = ?""", (name,)).fetchone()

                if password == password_t[0]:
                    # Ввод пользователя и вход в систему
                    self.user = cur.execute("""SELECT id FROM registration
                    WHERE name = ?""", (name,)).fetchone()

                    self.mainWin = SecondForm(self, self.user[0])
                    self.mainWin.show()
                    self.close()
                else:
                    self.error = Error(self, 'Пароль не подходит!')
                    self.error.show()
            else:
                self.error = Error(self, 'Такого пользователя нет!')
                self.error.show()
            

    def registration(self):
        self.reg = Registration(self)
        self.reg.show()
        self.close()


class Registration(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('RegistrationForm.ui', self)
        self.initUI()

    def initUI(self):
        # Связь с таблицей
        self.connection = sqlite3.connect("food.db")
        
        # Buttons
        self.btn.clicked.connect(self.registration)
        self.btn_back.clicked.connect(self.back)

    def back(self):
        self.menu = EntryMenu(self)
        self.menu.show()
        self.close()


    def registration(self):
        name = self.linen.text()
        password = self.linep.text()
        password_2 = self.linep_2.text()
        cur = self.connection.cursor()
        # Имена
        names = [i[0] for i in cur.execute("""SELECT name FROM registration""").fetchall()]

        # Проверка имени
        if name in names:
            self.error = Error(self, 'Данное имя уже существует.\nПридумайте другое!')
            self.error.show()
        elif len(set(name)) <= 4:
            self.error = Error(self, 'Данное имя не подходит по количетсву \nнеповторяющихся символов!')
            self.error.show()
        elif name.isdigit():
            self.error = Error(self, 'В имени не могут быть одни числа!')
            self.error.show()
        else:
            # Проверка пароля
            if password == '':
                self.error = Error(self, 'Введите пароль в основное поле!')
                self.error.show()
            elif len(set(password)) <= 5:
                self.error = Error(self, 'Данный пароль не подходит по длине!')
                self.error.show()
            elif password.isdigit():
                self.error = Error(self, 'В пароле не могут быть одни числа!')
                self.error.show()
            elif password.isalpha():
                self.error = Error(self, 'В пароле не могут быть одни буквы!')
                self.error.show()
            elif password.isupper():
                self.error = Error(self, 'В пароле не могут быть буквы\nтолько верхнего регистра!')
                self.error.show()
            elif password.islower():
                self.error = Error(self, 'В пароле не могут быть буквы\nтолько нижнего регистра!')
                self.error.show()
            else:
                # Проверка повторения пароля
                if password_2 == '':
                    self.error = Error(self, 'Ведите пароль в окно повторения!')
                    self.error.show()
                elif password != password_2:
                    self.error = Error(self, 'Введёные пароли не сходятся!')
                    self.error.show()
                else:
                    # Добавление пользователя в db
                    cur.execute("""INSERT INTO registration(name, password)
                    VALUES(?, ?)""", (name, password))
                    self.connection.commit()

                    # Вход в систему
                    self.user = cur.execute("""SELECT id FROM registration
                    WHERE name = ?""", (name,)).fetchone()
                    self.mainWin = SecondForm(self, self.user[0])
                    self.mainWin.show()
                    self.close()


class DelForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('DelForm.ui', self)
        self.initUI(args)
    
    def initUI(self, args):
        self.setWindowTitle('Окно удаления')
        self.user = args[-1]

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
            # Проверка пользователя
            user = self.connection.cursor().execute("""SELECT user FROM dishes
            WHERE name = ?""", (text,)).fetchone()
            if user[0] == self.user or self.user == '1' or self.user == 1:
                # Запрос к id
                id_receipt = cur.execute("""SELECT receipt FROM dishes
                    WHERE name = ?""", (text,)).fetchone()
                id_dishes = cur.execute("""SELECT id FROM dishes
                    WHERE name = ?""", (text,)).fetchone()

                # Проверка фотографии и её удаление
                photo = cur.execute("""SELECT photo FROM receipt 
                    WHERE id = ?""", (id_receipt[0],)).fetchone()[0]
                if photo:
                    need_file = f'{os.getcwd()}/Photos'
                    os.remove(f'{need_file}/{photo}')
                
                # Удаление выбранных строк
                cur.execute("""DELETE from receipt
                    WHERE id = ?""", (id_receipt[0],))
                cur.execute("""DELETE from dishes
                    WHERE id = ?""", (id_dishes[0],))
                cur.execute(f"""DELETE from dishes_type
                    WHERE id_dishes = ?""", (id_dishes[0],))

                self.connection.commit()
            else:
                self.error = Error(self, "Вы не можите удалять \nчужие публикации!!!")
                self.error.show()

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
        self.initUI(args)

    def initUI(self, args):
        self.setWindowTitle('Окно добавления')

        self.photo = ''
        self.user = args[-1]

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
        # Создаём нужные переменные
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
        names = [str(i[0]).lower() for i in names]

        # Проверка имени
        if not name_text or ''.join(''.join(''.join(name_text.split(' ')).split('.')).split(',')).isdigit():
            self.error = Error(self, "Введено число или ничего, а не строка \nв названии!!!")
            self.error.show()
        elif str(name_text).lower() in names:
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

                            new_name = ''
                            
                            # Добавление в receipt
                            s = ';'.join(s_inger)
                            cur = self.connection.cursor()
                            cur.execute(f"""INSERT INTO receipt(ingredients,receipt,photo) 
                            VALUES(?,?,?)""", (s, text, new_name))
                            self.connection.commit()

                            # id receipt
                            cur = self.connection.cursor()
                            id_receipt = cur.execute("""SELECT id FROM receipt 
                            WHERE ingredients = ? AND receipt = ?""", (s, text)).fetchone()

                            # Добавляем фотографию, если она есть
                            if self.photo:
                                if self.photo.path():
                                    # Перемещаем фотографию и переименовываем
                                    need_file = f'{os.getcwd()}/Photos'
                                    need_path = '/'.join(self.photo.path().split('/')[:-1])
                                    new_name = f'photo_{id_receipt[0]}.png'
                                    # print(self.photo.path(), f'{need_path}/{new_name}')
                                    os.rename(self.photo.path(), f'{need_path}/{new_name}')
                                    shutil.move(f'{need_path}/{new_name}', f'{need_file}')

                            if new_name:
                                cur.execute("""UPDATE receipt
                                SET photo = ?
                                WHERE id = ?""", (new_name, id_receipt[0]))

                            # Добавление в dishes
                            id_need = cur.execute("""SELECT id FROM receipt
                                WHERE receipt = ? AND ingredients = ?""", (text, s)).fetchone()

                            cur.execute(f"""INSERT INTO dishes(name, kalori, protein, fats, carb, receipt, user) 
                            VALUES(?, ?, ?, ?, ?, ?, ?)""", (name_text, kaloris, proteins, fats, carbs, id_need[0], self.user))
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
                            self.error = Error(self, 'Неожиданная ошибка, перезагрузитесь!')
                            self.error.show()
                            
        self.close()


class RedactForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('ReformForm.ui', self)
        self.initUI(args)

    def initUI(self, args):
        self.setWindowTitle('Окно изменений')
        self.modified = {}
        self.photo = ''
        self.user = args[-1]

        # Связь с таблицей
        self.connection = sqlite3.connect("food.db")
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.titles = None

        # CheckBox
        self.del_photo = False
        self.checkBox.stateChanged.connect(self.change_state)

        # ComboBox
        cur = self.connection.cursor()
        t = []
        for i in [i[0] for i in cur.execute("""SELECT name FROM type""").fetchall()]:
            t.append(i)
        self.comboBox.addItems(t)

        # Buttons
        self.btn_load.clicked.connect(self.load_table)
        self.btn_save.clicked.connect(self.save_table)
        self.btn_photo.clicked.connect(self.add_photo)

    def change_state(self, state):
        if state == Qt.Checked:
            self.del_photo = True
        else:
            self.del_photo = False

    def add_photo(self):
        self.photo = PhotoForm(self)
        self.photo.show()

    def load_table(self):
        # Все имена
        names = self.connection.cursor().execute("""SELECT name FROM dishes""")
        names = [str(i[0]).lower() for i in names]

        # Проверка на соответствие имён
        self.name = self.linen.text()
        if self.name.lower() not in names:
            self.error = Error(self, "Такого названия нет в таблице!!!")
            self.error.show()
        else:
            # Проверка пользователя
            user = self.connection.cursor().execute("""SELECT user FROM dishes
            WHERE name = ?""", (self.name,)).fetchone()
            if user[0] == self.user or self.user == 1 or self.user == '1':
                # Создание таблицы
                res = list(set(self.connection.cursor().execute("""SELECT
                    dishes.name,
                    dishes.kalori,
                    dishes.protein,
                    dishes.fats,
                    dishes.carb
                FROM
                    dishes_type
                LEFT JOIN dishes ON dishes_type.id_dishes = dishes.id
                LEFT JOIN type ON dishes_type.id_type = type.id
                WHERE dishes.name = ?""", (self.name,)).fetchall()))

                # Проверка на отсутствие элементов в res
                if not res:
                    self.tableWidget.setColumnCount(0)
                else:
                    self.tableWidget.setColumnCount(len(res[0]))

                # Создание таблицы
                self.titles = ['ID', 'kalori', 'protein', 'fats', 'carb']
                self.tableWidget.setRowCount(0)

                for i, row in enumerate(res):
                    self.tableWidget.setRowCount(
                        self.tableWidget.rowCount() + 1)
                    for j, elem in enumerate(row):
                        self.tableWidget.setItem(
                            i, j, QTableWidgetItem(str(elem)))

                self.tableWidget.setColumnWidth(1, 164)
                self.tableWidget.setColumnWidth(2, 50)
                self.tableWidget.setHorizontalHeaderLabels(['Название', 'Калории', 'Белки', 'Жиры', 'Углеводы'])

                # Receipt
                rec = self.connection.cursor().execute("""SELECT receipt FROM receipt
                WHERE id=(SELECT receipt FROM dishes WHERE name = ?)""", (self.name,)).fetchone()
                self.plainTextEdit.setPlainText(rec[0])

                # Ingredients
                rec = self.connection.cursor().execute("""SELECT ingredients FROM receipt
                WHERE id=(SELECT receipt FROM dishes WHERE name = ?)""", (self.name,)).fetchone()
                self.lineingr.setText('; '.join(rec[0].split(';')))

                self.modified = {}
            else:
                self.error = Error(self, "Вы не можите редактировать \nчужие публикации!!!")
                self.error.show()

    def item_changed(self, item):
        # Если значение в ячейке было изменено, 
        # то в словарь записывается пара: название поля, новое значение
        self.modified[self.titles[item.column()]] = item.text()

    def save_table(self):
        self.t = True
        # Проверка значений для имени и значений белков, жиров, углеводов, калорий
        if 'Название' in self.modified.keys() and len(self.modified) > 1:
            # Проверка, если имя и другие элементы
            for i in self.modified:
                if i != 'Название':
                    el = str(self.modified[i])
                    try:
                        if int(el) < 0:
                            self.error = Error(self, "Введено отрицытельное значение, \nа не натуральное или ноль!!!")
                            self.error.show()
                            self.t = False
                    except ValueError:
                        self.error = Error(self, "Введено строковое значение или не целое, \nа нужно натуральное или ноль!!!")
                        self.error.show()
                        self.t = False
                else:
                    try:
                        if float(str(self.modified['Название'])):
                            self.error = Error(self, "Введено число, а не строка!!!")
                            self.error.show()
                            self.t = False
                    except ValueError:
                        pass
        # Проверка, если только имя
        elif 'Название' in self.modified.keys() and len(self.modified) == 1:
            try:
                if float(str(self.modified['Название'])):
                    self.error = Error(self, "Введено число, а не строка!!!")
                    self.error.show()
                    self.t = False
            except ValueError:
                pass
        # Проверка, если нет имени, но есть другие элементы
        elif 'Название' not in self.modified.keys() and len(self.modified) != 0:
            for i in self.modified:
                el = str(self.modified[i])
                try:
                    if int(el) < 0:
                        self.error = Error(self, "Введено отрицытельное значение, \nа не натуральное или ноль!!!")
                        self.error.show()
                        self.t = False
                except ValueError:
                    self.error = Error(self, "Введено строковое значение или не целое, \nа нужно натуральное или ноль!!!")
                    self.error.show()
                    self.t = False
        
        if self.t:
            ingr_text = self.lineingr.text()
            s_inger = [i for i in ingr_text.split('; ')]
            # Проверка на ингредиенты
            if ''.join(s_inger).isdigit() or not ingr_text or ''.join(''.join(''.join(ingr_text.split(' ')).split('.')).split(',')).isdigit():
                self.error = Error(self, "Введено число или ничего, а не строка \nв ингредиентах!!!")
                self.error.show()
            else:
                # Запрос к id
                cur = self.connection.cursor()
                id_dish = cur.execute("""SELECT id FROM dishes WHERE name = ?""", (self.name,)).fetchone()
                id_receipt = cur.execute("""SELECT id FROM receipt 
                WHERE id = (SELECT receipt FROM dishes WHERE name = ?)""", (self.name,)).fetchone()

                # Нужные элементы
                text = self.plainTextEdit.toPlainText()
                item = self.comboBox.currentText()

                # Добавляем фотографию, если она есть
                try:
                    name_file = ''
                    if not self.del_photo:
                        if self.photo:
                            # Запрос к фотографии
                            photo = cur.execute("""SELECT photo FROM receipt 
                                WHERE id = ?""", (id_receipt[0],)).fetchone()[0]
                            if photo:
                                # Удаляем старое фото
                                need_file = f'{os.getcwd()}/Photos'
                                os.remove(f'{need_file}/{photo}')
                            if self.photo.path():
                                # Перемещаем фотографию и переименовываем
                                need_file = f'{os.getcwd()}/Photos'
                                name_file = self.photo.path()
                                need_path = '/'.join(self.photo.path().split('/')[:-1])
                                new_name = f'photo_{id_receipt[0]}.png'
                                # print(self.photo.path(), f'{need_path}/{new_name}')
                                os.rename(self.photo.path(), f'{need_path}/{new_name}')
                                shutil.move(f'{need_path}/{new_name}', f'{need_file}')

                    # Изменение фото
                    check_photo = cur.execute("""SELECT photo FROM receipt
                    WHERE id = ?""", (id_receipt[0],)).fetchone()
                    if self.del_photo:
                        if check_photo:
                            cur.execute("""UPDATE receipt
                            SET photo = ?
                            WHERE id = ?""", ('', id_receipt[0]))
                            need_file = f'{os.getcwd()}/Photos'
                            os.remove(f'{need_file}/{check_photo[0]}')
                    else:
                        if name_file:
                            cur.execute("""UPDATE receipt
                            SET photo = ?
                            WHERE id = ?""", (new_name, id_receipt[0]))

                    # Изменение в receipt 
                    cur.execute("""UPDATE receipt
                    SET receipt = ?, ingredients = ?
                    WHERE id = ?""", (text, ';'.join(s_inger), id_receipt[0]))

                    # Изменение в dishes_type
                    cur.execute("""UPDATE dishes_type 
                    SET id_type=(SELECT id FROM type WHERE name = ?)
                    WHERE id_dishes = ?""", (item, id_dish[0]))
                    
                    # Изменение в dishes
                    if self.modified:
                        que = "UPDATE dishes SET\n"
                        que += ", ".join([f"{key}='{self.modified.get(key)}'"
                                        for key in self.modified.keys()])
                        que += "WHERE name = ?"
                        cur.execute(que, (self.name,))
                    else:
                        pass
                        # self.error = Error(self, 'Изменений по калориям и \nдругим харак. не произошло!')
                        # self.error.show()
                    self.connection.commit()
                    self.modified.clear()
                
                except Exception:
                    self.error = Error(self, 'Изменений не произошло!')
                    self.error.show()

                self.close()


class ChoiceForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('ChoiceForm.ui', self)
        self.initUI(args)
    
    def initUI(self, args):
        # Связь с таблицей
        self.connection = sqlite3.connect("food.db")
        cur = self.connection.cursor()

        # Имя блюда
        for i in args:
            name = str(i)
        self.label_name.setText(f'Название: {name}')
        
        # Вся информация по блюду(Характеристика, рецепт и тд.)
        dishes = cur.execute("""SELECT kalori, protein, fats, carb, receipt, id FROM dishes
        WHERE name = ?""", (name,)).fetchone()

        receipt = cur.execute("""SELECT receipt, ingredients, photo FROM receipt
        WHERE id = ?""", (dishes[-2],)).fetchone()

        type = cur.execute("""SELECT name FROM type
        WHERE id = (SELECT id_type FROM dishes_type
        WHERE id_dishes = ?)""", (dishes[-1],)).fetchone()
        
        # Основные характеристики
        try:
            self.linek.setText(str(dishes[0]))
            self.linep.setText(str(dishes[1]))
            self.linef.setText(str(dishes[2]))
            self.linec.setText(str(dishes[3]))
            self.label_type.setText(f'Тип: {type[0]}')
        except Exception:
            self.error = Error(self, "Ошибка с файлами!!!")
            self.error.show()

        # Рецепт и ингредиенты
        try:
            self.textEdit_r.setPlainText(receipt[0])
            self.textEdit_i.setPlainText(';\n'.join(receipt[1].split(';')))
        except Exception:
            self.error = Error(self, "Ошибка с файлами!!!")
            self.error.show()

        # Фотография
        try:
            if receipt[-1]:
                self.pix = QtGui.QPixmap(f'{os.getcwd()}/Photos/{receipt[-1]}')
                self.label_photo.setPixmap(self.pix)
        except Exception:
            self.error = Error(self, "Ошибка с файлами!!!")
            self.error.show()


class Error(QWidget):
    def __init__(self, *error_text):
        super().__init__()
        self.initUI(error_text)

    def initUI(self, error_text):
        self.setGeometry(800, 300, 400, 100)
        self.setWindowTitle('Ошибка')

        self.lb = QLabel(self)
        # self.lb.resize(100, 50)
        self.lb.move(20, 30)
        # Текст ошибки
        self.lb.setText(f'Ошибка: {error_text[-1]}')


class HelpForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('HelpForm.ui', self)
        self.setWindowTitle('Помошник')

        # Работа с txt(Запись в строки)
        with open('helper.txt', encoding='utf8') as file:
            data = file.readlines()
            self.label.setText(data[0].rstrip('\n'))
            self.label_2.setText(data[1].rstrip('\n'))
            self.label_3.setText(data[2].rstrip('\n'))
            self.label_4.setText(data[3].rstrip('\n'))
            self.label_5.setText(data[4].rstrip('\n'))
            self.label_6.setText(data[5].rstrip('\n'))
            self.label_7.setText(data[6].rstrip('\n'))


class SecondForm(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('table.ui', self)
        self.initUI(args)

    def initUI(self, args):
        self.setWindowTitle('Окно таблицы')

        # Связь с таблицей
        self.connection = sqlite3.connect("food.db")

        # Пользователь
        self.user = args[-1]
        

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
        self.btn_help.clicked.connect(self.help_form)

        # Задаём значения для таблиц
        self.default = """SELECT
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

        self.query = self.default

        # Отображаем всю таблицу
        self.select_data()

        # Color Table
        rows = self.connection.cursor().execute("""SELECT name, user FROM dishes""").fetchall()
        if self.user != 1:
            self.color_table(rows)

    def color_table(self, rows):
        self.tableWidget.setSortingEnabled(False)

        # Вызываем функцию для выделения цветом блюд
        for num, i in enumerate(rows):
            if i[-1] == self.user:
                self.color_row(num, QColor(204, 255, 229))
            # print(i, num)
        self.tableWidget.setSortingEnabled(True)

    def color_row(self, row, color):
        # Красим строки
        for i in range(self.tableWidget.columnCount()):
            self.tableWidget.item(row, i).setBackground(color)

    def help_form(self):
        self.help = HelpForm(self)
        self.help.show()

    def refresh_table(self):
        self.query = self.default
        self.tableWidget.setSortingEnabled(False)
        self.select_data()

        # Color Table
        rows = self.connection.cursor().execute("""SELECT name, user FROM dishes""").fetchall()
        if self.user != 1:
            self.color_table(rows)

        # Сортируем название и добавляем возможность сортировать всю таблицу
        if self.tableWidget.rowCount() != 0:
            # print('True1')
            self.tableWidget.sortItems(0, order=0)
            self.tableWidget.setSortingEnabled(True)

    def add_element(self):
        self.add_form = AddingForm(self, self.user)
        self.add_form.show()

    def del_element(self):
        self.del_form = DelForm(self, self.user)
        self.del_form.show()

    def change_element(self):
        self.red_form = RedactForm(self, self.user)
        self.red_form.show()

    def choose_element(self):
        # Создание диалога
        name, ok_pressed = QInputDialog.getText(self, "Введите блюда", 
                                                "Название название блюда:")
        if ok_pressed:
            # Открываем ChoiceForm, если блюдо есть в таблице
            if name in [i[0] for i in self.connection.cursor().execute("""SELECT name FROM dishes""").fetchall()]:
                self.choice = ChoiceForm(self, name)
                self.choice.show()
            else:
                self.error = Error(self, "Такого блюда нет в таблице!!!")
                self.error.show()

    def find1_table(self):
        # Отключаем сортировку для корректного вывода
        self.tableWidget.setSortingEnabled(False)
        
        # Создаём нужные переменные
        new_win = False
        rows = ''
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
                self.query = self.default
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

            # Поиск подходящих значения для переменных и добавление их в characteristics
            characteristics = []
            if kaloris:
                need_k = making_num(kaloris, n=1)
                characteristics.append(f'dishes.kalori = {need_k}')

            if carbs:
                need_c = making_num(carbs, n=4)
                characteristics.append(f'dishes.carb = {need_c}')
            
            if proteins:
                need_p = making_num(proteins, n=2)
                characteristics.append(f'dishes.protein = {need_p}')

            if fats:
                need_f = making_num(fats, n=3)
                characteristics.append(f'dishes.fats = {need_f}')

            # Поиск для таблицы, где выбран тип блюда и его доп. характеристики
            if self.item != 'Всё':
                # Запрос к типу блюда, вывод всех id блюд с выбранным типом
                item = cursor.execute("""SELECT id FROM type WHERE name = ?""", (self.item,)).fetchone()
                items = [i[0] for i in cursor.execute("""SELECT id_type FROM dishes_type""").fetchall()]
                if item[0] not in items:
                    self.query = """"""
                elif need_k == -1 and need_f == -1 and need_c == -1 and need_p == -1:
                    # Поиск только по типу
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

                    rows = self.connection.cursor().execute(f"""SELECT dishes.name, dishes.user FROM dishes_type
                    LEFT JOIN dishes ON dishes_type.id_dishes = dishes.id
                    LEFT JOIN type ON dishes_type.id_type = type.id
                    WHERE type.name = '{self.item}'""").fetchall()
                else:
                    # Поиск по типу и характеристикам из characteristics
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
                    WHERE type.name = '{self.item}' AND {' AND '.join(characteristics)}"""

                    rows = self.connection.cursor().execute(f"""SELECT dishes.name, dishes.user FROM dishes_type
                    LEFT JOIN dishes ON dishes_type.id_dishes = dishes.id
                    LEFT JOIN type ON dishes_type.id_type = type.id
                    WHERE type.name = '{self.item}' AND {' AND '.join(characteristics)}""").fetchall()
            else:
                # Поиск для таблицы, где выбран только тип блюда
                if need_k == -1 and need_f == -1 and need_c == -1 and need_p == -1:
                    # Выводим ВСЁ
                    self.query = self.default

                    rows = self.connection.cursor().execute("""SELECT name, user FROM dishes""").fetchall()
                else:
                    # Поиск только по характеристикам из characteristics
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
                    WHERE {' AND '.join(characteristics)}"""

                    rows = self.connection.cursor().execute(f"""SELECT dishes.name, dishes.user FROM dishes_type
                    LEFT JOIN dishes ON dishes_type.id_dishes = dishes.id
                    LEFT JOIN type ON dishes_type.id_type = type.id
                    WHERE {' AND '.join(characteristics)}""").fetchall()

        self.select_data()

        # Color Table
        if self.user != 1:
            self.color_table(rows)

    def find2_table(self):
        # Отключаем сортировку для корректного вывода
        self.tableWidget.setSortingEnabled(False)

        self.linek.setText('')
        self.linec.setText('')
        self.linep.setText('')
        self.linef.setText('')

        text = self.lineingr.text().lower().split('; ')
        rows = ''

        # Проверка на присутствие введёных значений
        if not text:
            self.query = self.default
            self.select_data()
        else:
            # Ингредиенты всех блюд
            cur = self.connection.cursor()
            ingredients = cur.execute("""SELECT ingredients FROM receipt""").fetchall()
            ids = []
            accept_dish = False

            # Список нужных id (id блюд с выбранными ингредиентами)
            for el in ingredients:
                for i in el[0].lower().split('; '):
                    for j in text:
                        if j in i:
                            accept_dish = True
                        else:
                            accept_dish = False
                            break
                    if accept_dish:
                        id_ingredient = cur.execute("""SELECT id FROM receipt WHERE ingredients = ?""", (el[0],)).fetchone()
                        ids.append(id_ingredient[0])
            
            # Выводим нужные блюда
            if set(ids):
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

                rows = self.connection.cursor().execute(f"""SELECT name, user FROM dishes
                WHERE dishes.receipt = {ids[0]} {' '.join(find)}""").fetchall()
            else:
                self.query = """"""
            
            self.select_data()

            # Color Table
            if self.user != 1:
                self.color_table(rows)

    def select_data(self):
        # Создание таблицы
        res = list(set(self.connection.cursor().execute(self.query).fetchall()))
        # print(self.tableWidget.isSortingEnabled())

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
        self.tableWidget.setHorizontalHeaderLabels(['Название', 'Калории', 'Белки', 'Жиры', 'Углеводы', 'Тип'])

        # Сортируем название и добавляем возможность сортировать всю таблицу
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.sortItems(0, order=0)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = EntryMenu()
        ex.show()
        sys.exit(app.exec())
    except Exception:
        print("Ошибка с файлами!!!")