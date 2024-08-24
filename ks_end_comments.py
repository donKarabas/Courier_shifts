# Добавил в код программы root.protocol('WM_DELETE_WINDOW', self.on_exit)
# Перед закрытием программы закрывается база данных
# Добавил комментарии к коду.

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import datetime
from calendar import monthrange
import re


class Main:
    def __init__(self):
        # Устанавливаем главное окно.
        self.root = tk.Tk()
        self.root.title('Курьерские смены')
        self.root.geometry('1265x900+300+100')
        self.root.resizable(False, False)

        # Запуск программы из функции.
        self.init_main()

        # Инструкция запускает функцию on_exit перед закрытием главного окна. Подтверждение закрытия
        # сначала закрывает базу данных db.conn.close()
        self.root.protocol('WM_DELETE_WINDOW', self.on_exit)

        self.root.mainloop()

    def init_main(self):
        # Устанавливаем главную панель инструментов - toolbar.
        toolbar = tk.Frame(self.root, bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Кнопка редактирования в toolbar. (функция redact)
        self.update_img = tk.PhotoImage(file='update2.png')
        btn_update = tk.Button(toolbar, text='Редактировать', command=self.redact, bg='#d7d8e0', bd=0,
                               compound=tk.TOP, image=self.update_img)
        btn_update.pack(side=tk.LEFT)

        # Кнопка поиска в toolbar. (функция open_search_dialog)
        self.search_img = tk.PhotoImage(file='search2.png')
        btn_search = tk.Button(toolbar, text='Поиск', command=self.open_search_dialog, bg='#d7d8e0', bd=0,
                               compound=tk.TOP, image=self.search_img)
        btn_search.pack(side=tk.LEFT)

        # Виджеты выбора года и месяца в toolbar.
        # По году определяется имя базы данных (БД), по месяцу определяется имя таблицы в БД.
        label_year = tk.Label(toolbar, text='год')
        label_year.place(x=760, y=5)
        label_month = tk.Label(toolbar, text='месяц')
        label_month.place(x=737, y=30)

        # Список месяцев, подаётся в combobox.
        self.ls_month = ["Jan", "Feb", "Marc", "Apr", "May", "June", "July", "Aug",
                         "Sept", "Oct", "Nov", "Dec"]

        # Получаем числовое значение месяца, определяем года, которые будут подаваться в combobox.
        self.ind_month = int(datetime.datetime.now().strftime('%m'))
        self.cur_year = int(datetime.datetime.now().strftime('%Y'))
        self.ls_year_int = [self.cur_year - 1, self.cur_year, self.cur_year + 1]
        self.ls_year = [str(self.ls_year_int[0]), str(self.ls_year_int[1]), str(self.ls_year_int[2])]

        # Combobox для виджета "год" - по умолчанию текущий год + прошлый год + будущий год.
        self.combobox_year = ttk.Combobox(toolbar, width=4, values=[self.ls_year[0], self.ls_year[1],
                                                                    self.ls_year[2]])
        self.combobox_year.current(1)
        self.combobox_year.place(x=800, y=5)

        # Combobox для виджета "месяц" - по списку месяцев и индексу месяца получаем название месяца.
        # По умолчанию установлен текущий месяц.
        self.combobox_month = ttk.Combobox(toolbar, width=5, values=[self.ls_month[0], self.ls_month[1],
                                                                     self.ls_month[2], self.ls_month[3],
                                                                     self.ls_month[4], self.ls_month[5],
                                                                     self.ls_month[6], self.ls_month[7],
                                                                     self.ls_month[8], self.ls_month[9],
                                                                     self.ls_month[10], self.ls_month[11]])
        self.combobox_month.current(self.ind_month - 1)
        self.combobox_month.place(x=800, y=30)

        # Вызов функции старта. В функцию передаётся toolbar
        self.button_start(toolbar)

    # Функция получает и возвращает для передачи в другие классы следующие значения класса Main
    # Выбранный месяц (имя таблицы), адрес экземпляра класса, выбранный год (имя БД),
    # виджет Treeview, главное окно root.
    def month_tab(self):
        try:
            month = self.ls_data[1]
            address = self
            year = self.ls_data[0]
            view = self.tree
            root = self.root
            return month, address, year, view, root
        except AttributeError:
            tk.messagebox.showerror('Ошибка открытия!', 'Для работы необходимо открыть таблицу\n'
                                                        'Для редактирования необходимо выделить строку')

    # В начале работы видим кнопку "открыть" под блоком виджетов и выбора combobox "год", "месяц".
    # Функция определяет блок инструкций, обеспечивающий работу кнопки.
    def button_start(self, toolbar):
        btn_open_dialog = tk.Button(toolbar, text='Открыть')
        btn_open_dialog.place(x=800, y=55)
        # Вызов функции open_table, куда передаётся toolbar и выбранные в combobox год и месяц.
        btn_open_dialog.bind('<Button-1>', lambda event: self.open_table(self.combobox_year.get(),
                                                                         self.combobox_month.get(), toolbar))

    # Функция содержит блок инструкций, обеспечивающий открытие таблицы.
    def open_table(self, year, month, toolbar):
        # Передаём выбранный год и месяц в класс DB и содаём экземпляр класса.
        self.ls_data = [year, month]
        self.db = DB(self.ls_data[0], self.ls_data[1])

        # Создаём виджет Treeview для отображения таблицы.
        self.tree = ttk.Treeview(self.root, columns=('ID', 'day_week', 'work_shift', 'delivery', 'good_works',
                                                     'daily_revenue', 'comments'), height=31, show='headings')

        self.tree.column('ID', width=80, anchor=tk.CENTER)
        self.tree.column('day_week', width=80, anchor=tk.CENTER)
        self.tree.column('work_shift', width=100, anchor=tk.CENTER)
        self.tree.column('delivery', width=100, anchor=tk.CENTER)
        self.tree.column('good_works', width=100, anchor=tk.CENTER)
        self.tree.column('daily_revenue', width=100, anchor=tk.CENTER)
        self.tree.column('comments', width=690, anchor=tk.W)

        self.tree.heading('ID', text='Дата')
        self.tree.heading('day_week', text='день')
        self.tree.heading('work_shift', text='См. (часы)')
        self.tree.heading('delivery', text='Достав.')
        self.tree.heading('good_works', text='Доб. дел.')
        self.tree.heading('daily_revenue', text='Днев. выр.')
        self.tree.heading('comments', text='Комментарии')

        self.tree.pack()

        # sql запрос на выбор строк в таблице по номеру, соответствующему дате месяца. Если таблица
        # пустая, определяется и записывается в таблицу количество дней в месяце(дата) и день
        # недели, соответствующий году, месяцу и дате.
        self.db.c.execute(F'''SELECT ID FROM {self.ls_data[1]}''')
        results = self.db.c.fetchone()
        if results == None:
            day_weeks = ['пн', 'вт', 'ср', 'чт',
                         'пт', 'сб', 'вс']
            ind_month = self.ls_month.index(month) + 1
            int_year = int(year)
            days = monthrange(int_year, ind_month)[1]
            for n in range(days):
                date = datetime.datetime(int_year, ind_month, n + 1)
                ind_week = date.weekday()
                day_week = day_weeks[ind_week]
                self.db.c.execute(f'''INSERT INTO {month} (ID, day_week, work_shift, delivery, good_works, 
                                    daily_revenue, comments)
                                    VALUES(?, ?, ?, ?, ?, ?, ?)''',
                                  (n + 1, day_week, '', '', '', '', ''))
            self.db.conn.commit()

        # Вызов функции просмотра содержимого таблицы. Передаётся выбранный месяц.
        self.view_records(self.ls_data[1])

        # Открывает БД и таблицу в БД, указанных в combobox.
        # После открытия таблицы, кнопка "Открыть" становится неактивной, появляется активная кнопка "Закрыть".
        btn_open_dialog = tk.Button(toolbar, state='disabled', text='Открыть')
        btn_open_dialog.place(x=800, y=55)

        # Вызов функции кнопки "Закрыть". Передаётся toolbar.
        self.close_table(toolbar)

    # Блок инструкций для кнопки "Закрыть".
    def close_table(self, toolbar):
        # Вызов функции close_process
        btn_close = tk.Button(self.root, text='Закрыть', command=self.close_process)
        btn_close.place(x=910, y=55)
        # Вызов функции button_start(toolbar)
        # По нажатию кнопки закрывается таблица и становится активной кнопка "Открыть"
        btn_close.bind('<Button-1>', lambda event: self.button_start(toolbar))

    # Проверяет полученные данные из класса Update
    # Если данные проходят проверку, они передаются в функцию update_record
    def validate(self, month, ws, delivery, gw, dr, comments):
        result_entry_ws = re.match('^\d{0,2}(\.\d{1})?$', ws)
        result_entry_delivery = re.match('^\d{0,2}(\.\d{1})?$', delivery)
        result_entry_gw = re.match('^-?\d{0,5}?$', gw)
        result_entry_dr = re.match('^\d{0,6}(\.\d{1,2})?$', dr)

        if (result_entry_ws and result_entry_delivery and result_entry_gw
                and result_entry_dr):
            self.update_record(month, ws, delivery, gw, dr, comments)
        else:
            tk.messagebox.showinfo('Ошибка', 'Неверный ввод данных')

    # Записывает обновлённые данные в БД.
    def update_record(self, month, ws, delivery, gw, dr, comments):
        self.close_statistics()     # Вызов функции класса Statistics
        try:
            self.db.c.execute(f'''UPDATE {month} SET work_shift=?, delivery=?, good_works=?, 
                                    daily_revenue=?, comments=? WHERE ID=?''',
                              (ws, delivery, gw, dr, comments,
                               self.tree.set(self.tree.selection()[0], '#1')))
            self.db.conn.commit()
            # Вызов функции просмотра содержимого таблицы. Передаётся месяц(название таблицы)
            self.view_records(month)
        except:
            tk.messagebox.showerror('Ошибка открытия!', f'Для работы необходимо открыть таблицу\n'
                                                        f'Для редактирования необходимо выделить строку')

    # Просмотр содержимого таблицы. Функция получает месяц (название таблицы).
    def view_records(self, month):
        self.month_table = month
        self.db.c.execute(f'''SELECT * FROM {self.month_table}''')
        self.tab_cont = self.table_contents(self.db.c.fetchall())   # Вызов функции table_contents
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.tab_cont]
        # Вызов функции open_view_stat. Передаёт очищенный список кортежей.
        self.open_view_stat(self.tab_cont)

    # Перебирает список кортежей, удаляет из чисел типа int точку и ноль, если число целое,
    # и это целое число возвращает.
    def table_contents(self, ls):
        ls2 = ls
        count = 0
        for item in ls2:
            item = list(item)

            item[2] = str(item[2]).rstrip('0').rstrip('.')
            item[3] = str(item[3]).rstrip('0').rstrip('.')

            item_2 = tuple(item)
            ls2[count] = item_2

            count += 1

        return ls2

    # Инструкции для обработки поискового запроса. В функцию передаётся адрес экземпляра класса Main
    # (передаётся self), месяц (наименование таблицы), выбор столбца, по которому будет проводиться
    # поиск ("дни недели" или "комментарии") и собственно запрос.
    def search_records(self, month, choice_row, str_search):
        self.close_statistics()     # Вызов close_statistics класса Statistics
        try:
            # Инструкция адаптации наименования столбцов поиска, выбранные в combobox
            # и изначально взятые в БД как: "comments" или "day_week"
            self.dict_search = {'комментарии': 'comments', 'дни недели': 'day_week'}
            self.search_row = self.dict_search[choice_row]
            self.str_search = ('%' + str_search + '%',)
            self.db.c.execute(f'''SELECT * FROM {month} WHERE {self.search_row}
                                LIKE ?''', self.str_search)
            # Вызов table_contents
            self.search_contents = self.table_contents(self.db.c.fetchall())
            [self.tree.delete(i) for i in self.tree.get_children()]
            [self.tree.insert('', 'end', values=row) for row in self.search_contents]
            # Вызов open_view_stat
            self.open_view_stat(self.search_contents)
        except:
            pass

    # Редактирование таблицы, основная функция программы. Ссылка на класс Update.
    # В класс, ссылкой на функцию month_tab, передаётся кортеж значений из класса Main
    def redact(self):
        Update(self.month_tab())

    # Поиск. Ссылка на класс Search
    # В класс, ссылкой на функцию month_tab, передаётся кортеж значений из класса Main
    def open_search_dialog(self):
        Search(self.month_tab())

    # Функция ссылается на класс Statistics. В класс передаются данные БД списком очищенных
    # кортежей и кортеж значений класса Main функцией month_tab
    def open_view_stat(self, tab):
        self.stata = Statistics(tab, self.month_tab())

    # Закрывает виджет Treeview
    def close_process(self):
        self.tree.destroy()
        # Вызов close_statistics класса Main
        self.close_statistics()

    # Функция close_statistics класса Main
    def close_statistics(self):
        # Вызов close_statistics класса Statistics
        self.stata.close_statstics()

    # При закрытии главного окна программы, функция открывает диалоговое окно с предложением
    # подтвердить закрытие программы. После подтверждения закрывается база данных и закрывается
    # программа.
    def on_exit(self):
        try:
            if messagebox.askyesno('Выйти', 'Закрыть программу'):
                self.db.conn.close()
                print('base close')
                self.root.destroy()
        except AttributeError:
            self.root.destroy()


# Класс Update, основной функционал программы. Получает кортеж значений класса Main.
class Update(tk.Toplevel):          # Наследуется от объекта Toplevel.
    def __init__(self, month_address):
        try:
            super().__init__()
            self.init_update()
            self.month = month_address[0]
            self.address = month_address[1]
            self.year = month_address[2]
            self.main_view = month_address[3]
            self.db = DB(self.year, self.month)     # Экземпляр класса DB
            # Ссылка на default_data
            self.default_data()
        except TypeError:
            self.destroy()

    # Основные инструкции для окна Update
    def init_update(self):
        self.title('Редактировать таблицу')
        self.geometry('500x220+650+300')
        self.resizable(False, False)

        lable_ws = tk.Label(self, text='Смены (часы)')
        lable_ws.place(x=50, y=10)
        lable_delivery = tk.Label(self, text='Доставки')
        lable_delivery.place(x=50, y=40)
        lable_gw = tk.Label(self, text='Добрые дела')
        lable_gw.place(x=50, y=70)
        lable_dr = tk.Label(self, text='Дневная выручка')
        lable_dr.place(x=50, y=100)
        lable_comments = tk.Label(self, text='Комментарии')
        lable_comments.place(x=50, y=130)
        self.err_msg = tk.StringVar()   # Сообщение о максимальном заполнении строки комментариев.
        lable_err = tk.Label(self, foreground='red', textvariable=self.err_msg)
        lable_err.place(x=420, y=130)

        self.entry_ws = tk.Entry(self, bg='white')
        self.entry_ws.place(x=200, y=10)
        self.entry_delivery = tk.Entry(self, bg='white')
        self.entry_delivery.place(x=200, y=40)
        self.entry_gw = tk.Entry(self, bg='white')
        self.entry_gw.place(x=200, y=70)
        self.entry_dr = tk.Entry(self, bg='white')
        self.entry_dr.place(x=200, y=100)
        # Ссылка на validate_comment
        self.check = (self.register(self.validate_comment), '%P')

        self.entry_comments = tk.Entry(self, validate='key', validatecommand=self.check, bg='white')
        self.entry_comments.place(x=200, y=130)
        self.entry_ws.focus_set()

        btn_cancel = tk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=310, y=170)
        btn_ok = tk.Button(self, text='Добавить')
        btn_ok.place(x=200, y=170)
        # Ссылка на функцию validate класса Main. Передаются обновлённые данные, сделанные
        # в окне редакции.
        btn_ok.bind('<Button-1>', lambda event: Main.validate(self.address, self.month, self.entry_ws.get(),
                                                              self.entry_delivery.get(), self.entry_gw.get(),
                                                              self.entry_dr.get(), self.entry_comments.get()))
        # Дополнительная функция для кнопки "Добавить". По нажатии кнопки, после отправки
        # новых данных в класса Main, закрывает окно редактирования.
        btn_ok.bind('<Button-1>', lambda event: self.destroy(), add='+')

        self.grab_set()
        self.focus_set()

    # Функция проверяет максимально допустимую длину комментариев.
    def validate_comment(self, less_comment):
        str_comm = re.match('^.{0,69}$', less_comment) is not None
        if not str_comm:
            self.err_msg.set('69x69!')
        else:
            self.err_msg.set('')
        return str_comm

    # Извлекает и отображает ранее сделанные записи в редактируемой строке.
    def default_data(self):
        try:
            self.db.c.execute(f'''SELECT * FROM {self.month} WHERE id=?''',
                              (self.main_view.set(self.main_view.selection()[0], '#1'),))
            row = self.db.c.fetchone()
            self.entry_ws.insert(0, row[2])
            self.entry_delivery.insert(0, row[3])
            self.entry_gw.insert(0, row[4])
            self.entry_dr.insert(0, row[5])
            self.entry_comments.insert(0, row[6])
        except:
            pass


# Класс поиска.  Получает кортеж значений класса Main. Класс позволяет осуществить
# выборку по заданным словам с учётом статистики по найденным строкам.
class Search(tk.Toplevel):          # Наследуется от объекта Toplevel.
    def __init__(self, month_address):
        try:
            super().__init__()
            self.init_search()
            self.month = month_address[0]   # Выбранный месяц (название таблицы)
            self.address = month_address[1]     # Адрес объекта класса Main
        except TypeError:
            self.destroy()

    # Инструкции класса.
    def init_search(self):
        self.title('Поиск')
        self.geometry('500x220+650+300')
        self.resizable(False, False)

        lable_tab_search = tk.Label(self, text='колонка')
        lable_tab_search.place(x=50, y=20)
        lable_search = tk.Label(self, text='Поиск')
        lable_search.place(x=50, y=50)
        # Combobox позволяет осуществить поиск по двум столбцам:
        # "комментарии" и "дни недели".
        self.combo_tab = ttk.Combobox(self, values=[u'комментарии', u'дни недели'])
        self.combo_tab.current(0)
        self.combo_tab.place(x=200, y=20)

        self.entry_search = ttk.Entry(self)
        self.entry_search.place(x=200, y=50)
        self.entry_search.focus()

        btn_cansel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cansel.place(x=310, y=170)
        btn_search = ttk.Button(self, text='Поиск')
        btn_search.place(x=200, y=170)
        # Ссылка на функцию search_records класса Main. Передаются условия поиска, определённые
        # в окне поиска.
        btn_search.bind('<Button-1>', lambda event: Main.search_records(self.address, self.month,
                                                                        self.combo_tab.get(),
                                                                        self.entry_search.get()))
        # Дополнительная функция для кнопки "Поиск". По нажатии кнопки, после отправки
        # условий поиска в класса Main, закрывает окно поиска.
        btn_search.bind('<Button-1>', lambda event: self.destroy(), add='+')


# Класс статистики обеспечивает динамическое отображение статистики при получении обновления данных
# и при выборке поиском. Получает список кортежей из БД и кортеж данных из класса Main.
class Statistics:
    # Константы класса
    WORK_SHIFT = 12
    RATE = 2000
    RATE_DELIV = 200

    def __init__(self, val_tab, arguments):
        self.stata = val_tab    # Список кортежей БД
        self.root_stat = arguments[4]   # Кортеж данных из класса Main
        self.ws = Statistics.WORK_SHIFT
        self.rate = Statistics.RATE
        self.rate_deliv = Statistics.RATE_DELIV

        # Вызов init_statistics
        self.init_statistics()

    # Виджеты класса Statistics
    def init_statistics(self):
        # Вызов calc_statistics
        self.calc_stata = self.calc_statistics()

        self.label_shifts = tk.Label(self.root_stat, text='Смен')
        self.label_shifts.place(x=135, y=750)
        self.label_hours = tk.Label(self.root_stat, text='Часов')
        self.label_hours.place(x=135, y=775)
        self.label_deliv = tk.Label(self.root_stat, text='Дост.')
        self.label_deliv.place(x=135, y=800)
        self.label_good_works = tk.Label(self.root_stat, text='ДД')
        self.label_good_works.place(x=135, y=825)

        self.value_deliv = tk.StringVar()
        self.label_value_deliv = tk.Label(self.root_stat, textvariable=self.value_deliv)
        self.label_value_deliv.place(x=220, y=800)
        self.value_deliv.set(str(self.calc_stata[2]))

        self.value_amount_shifts = tk.StringVar()
        self.label_amount_shifts = tk.Label(self.root_stat, textvariable=self.value_amount_shifts)
        self.label_amount_shifts.place(x=220, y=750)
        self.value_amount_shifts.set(str(self.calc_stata[0]))

        self.value_hours_shifts = tk.StringVar()
        self.label_hours_shifts = tk.Label(self.root_stat, textvariable=self.value_hours_shifts)
        self.label_hours_shifts.place(x=220, y=775)
        self.value_hours_shifts.set(str(self.calc_stata[1]))

        self.value_hours_shifts_rub = tk.StringVar()
        self.label_hours_shifts_rub = tk.Label(self.root_stat, textvariable = self.value_hours_shifts_rub)
        self.label_hours_shifts_rub.place(x=285, y=775)
        self.value_hours_shifts_rub.set(str(self.calc_stata[3]) + ' руб.')

        self.value_deliv_rub = tk.StringVar()
        self.label_deliv_rub = tk.Label(self.root_stat, textvariable=self.value_deliv_rub)
        self.label_deliv_rub.place(x=285, y=800)
        self.value_deliv_rub.set(str(self.calc_stata[4]) + ' руб.')

        self.value_month_revenue = tk.StringVar()
        self.label_month_revenue = tk.Label(self.root_stat, textvariable=self.value_month_revenue,
                                            font=('arial', '10'))
        self.label_month_revenue.place(x=475, y=745)
        self.value_month_revenue.set(str(self.calc_stata[5]) + ' руб.')

        self.value_good_works_rub = tk.StringVar()
        self.label_good_works_rub = tk.Label(self.root_stat, textvariable=self.value_good_works_rub)
        self.label_good_works_rub.place(x=285, y=825)
        self.value_good_works_rub.set(str(self.calc_stata[6]))

        self.value_total_incom_rub = tk.StringVar()
        self.label_total_incom_rub = tk.Label(self.root_stat, textvariable=self.value_total_incom_rub,
                                              font='Arial 12 bold')
        self.label_total_incom_rub.place(x=415, y=800)
        self.value_total_incom_rub.set(str(self.calc_stata[7]) + ' руб.')

    # Инструкции для рассчёта статистики. Функция возвращает кортеж статистики.
    def calc_statistics(self):
        count_shifts = 0
        count_hours = 0
        count_deliv = 0
        count_hours_rub = 0
        count_good_works_rub = 0
        count_month_revenue = 0

        for item in self.stata:
            shifts = item[2]
            deliv = item[3]
            good_works = item[4]
            month_revenue = item[5]
            if shifts != '' and shifts != '0':  # Количество смен
                count_shifts += 1

            if shifts != '':            # Количество часов
                hours = float(item[2])
                count_hours += hours
                if hours == self.ws:        # Сумма, начисленная за часы
                    hours_rub = self.rate
                else:
                    hours_rub = round((self.rate / self.ws * hours), 0)
                count_hours_rub += hours_rub

            if deliv != '' and deliv != '0':    # Количество доставок
                orders = float(item[3])
                count_deliv += orders

            if month_revenue != '':     # Начислено за месяц
                count_month_revenue += month_revenue

            if good_works != '':        # Добрые дела
                gw = int(item[4])
                count_good_works_rub += gw

        self.count_shifts = count_shifts        # Количество смен
        self.count_hours = count_hours          # Количество часов
        self.count_deliv = count_deliv          # Количество доставок
        self.count_hours_rub = count_hours_rub  # Сумма за часы
        self.count_deliv_rub = self.count_deliv * self.rate_deliv   # Сумма за доставки
        self.count_deliv_rub = round(round(self.count_deliv_rub))   # Округлённая сумма за доставки
        self.count_month_revenue = count_month_revenue              # Сумма за месяц
        self.count_good_works_rub = count_good_works_rub            # Добрые дела
        self.total_incom = self.count_hours_rub + self.count_deliv_rub  # Общая сумма сбора ресторана
                                                                        # по заказам из настоящей статистики.
        return (self.count_shifts, self.count_hours, self.count_deliv, self.count_hours_rub,
                self.count_deliv_rub, self.count_month_revenue, self.count_good_works_rub, self.total_incom)

    # Функция обнуляет данные статистики. Включается перед получением новых данных.
    def close_statstics(self):
        self.label_amount_shifts.destroy()
        self.label_hours_shifts.destroy()
        self.label_value_deliv.destroy()
        self.label_hours_shifts_rub.destroy()
        self.label_deliv_rub.destroy()
        self.label_month_revenue.destroy()
        self.label_good_works_rub.destroy()
        self.label_total_incom_rub.destroy()


# Класс DB получает выбранные год и месяц. Год присваивает имени БД, создаёт её и/или открывает.
# Месяц присваивает таблице в БД. Создаёт её и/или открывает.
class DB():
    def __init__(self, year, month):
        self.year = year
        self.month_table = month
        self.name_baze = f'{self.year}' + '_test_courier.db'
        self.conn = sqlite3.connect(f'{self.name_baze}')
        self.c = self.conn.cursor()
        self.c.execute(f'''CREATE TABLE IF NOT EXISTS {self.month_table}
                        (ID INTEGER PRIMARY KEY,
                        day_week TEXT,
                        work_shift REAL,
                        delivery REAL,
                        good_works INTEGER,
                        daily_revenue REAL,
                        comments TEXT)''')
        self.conn.commit()


if __name__ == '__main__':
    main = Main()
