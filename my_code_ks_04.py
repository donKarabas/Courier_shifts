# Добавлена и настроена Статистика.

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import datetime
from calendar import monthrange
import re


class Main:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Курьерские смены')
        self.root.geometry('1265x900+300+100')
        self.root.resizable(False, False)

        self.init_main()

        self.root.mainloop()

    def init_main(self):
        toolbar = tk.Frame(self.root, bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.update_img = tk.PhotoImage(file='update2.png')
        btn_update = tk.Button(toolbar, text='Редактировать', command=self.redact, bg='#d7d8e0', bd=0,
                               compound=tk.TOP, image=self.update_img)
        btn_update.pack(side=tk.LEFT)

        self.search_img = tk.PhotoImage(file='search2.png')
        btn_search = tk.Button(toolbar, text='Поиск', command=self.open_search_dialog, bg='#d7d8e0', bd=0,
                               compound=tk.TOP, image=self.search_img)
        btn_search.pack(side=tk.LEFT)

        label_year = tk.Label(toolbar, text='год')
        label_year.place(x=760, y=5)
        label_month = tk.Label(toolbar, text='месяц')
        label_month.place(x=737, y=30)

        self.ls_month = ["Jan", "Feb", "Marc", "Apr", "May", "June", "July", "Aug",
                         "Sept", "Oct", "Nov", "Dec"]

        self.ind_month = int(datetime.datetime.now().strftime('%m'))
        self.cur_year = int(datetime.datetime.now().strftime('%Y'))
        self.ls_year_int = [self.cur_year - 1, self.cur_year, self.cur_year + 1]
        self.ls_year = [str(self.ls_year_int[0]), str(self.ls_year_int[1]), str(self.ls_year_int[2])]

        self.combobox_year = ttk.Combobox(toolbar, width=4, values=[self.ls_year[0], self.ls_year[1],
                                                                    self.ls_year[2]])
        self.combobox_year.current(1)
        self.combobox_year.place(x=800, y=5)

        self.combobox_month = ttk.Combobox(toolbar, width=5, values=[self.ls_month[0], self.ls_month[1],
                                                                     self.ls_month[2], self.ls_month[3],
                                                                     self.ls_month[4], self.ls_month[5],
                                                                     self.ls_month[6], self.ls_month[7],
                                                                     self.ls_month[8], self.ls_month[9],
                                                                     self.ls_month[10], self.ls_month[11]])
        self.combobox_month.current(self.ind_month - 1)
        self.combobox_month.place(x=800, y=30)

        self.button_start(toolbar)

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

    def button_start(self, toolbar):
        btn_open_dialog = tk.Button(toolbar, text='Открыть')
        btn_open_dialog.place(x=800, y=55)
        btn_open_dialog.bind('<Button-1>', lambda event: self.open_table(self.combobox_year.get(),
                                                                         self.combobox_month.get(), toolbar))

    def open_table(self, year, month, toolbar):
        self.ls_data = [year, month]
        self.db = DB(self.ls_data[0], self.ls_data[1])

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

        self.view_records(self.ls_data[1])

        btn_open_dialog = tk.Button(toolbar, state='disabled', text='Открыть')
        btn_open_dialog.place(x=800, y=55)

        self.close_table(toolbar)

    def close_table(self, toolbar):
        btn_close = tk.Button(self.root, text='Закрыть', command=self.close_process)
        btn_close.place(x=910, y=55)
        btn_close.bind('<Button-1>', lambda event: self.button_start(toolbar))

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

    def update_record(self, month, ws, delivery, gw, dr, comments):
        self.close_statistics()
        try:
            self.db.c.execute(f'''UPDATE {month} SET work_shift=?, delivery=?, good_works=?, 
                                    daily_revenue=?, comments=? WHERE ID=?''',
                              (ws, delivery, gw, dr, comments,
                               self.tree.set(self.tree.selection()[0], '#1')))
            self.db.conn.commit()
            self.view_records(month)
        except:
            tk.messagebox.showerror('Ошибка открытия!', f'Для работы необходимо открыть таблицу\n'
                                                        f'Для редактирования необходимо выделить строку')

    def view_records(self, month):
        self.month_table = month
        self.db.c.execute(f'''SELECT * FROM {self.month_table}''')
        self.tab_cont = self.table_contents(self.db.c.fetchall())
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.tab_cont]

        self.open_view_stat(self.tab_cont)

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

    def search_records(self, month, choice_row, str_search):
        self.close_statistics()
        try:
            self.dict_search = {'комментарии': 'comments', 'дни недели': 'day_week'}
            self.search_row = self.dict_search[choice_row]
            self.str_search = ('%' + str_search + '%',)
            self.db.c.execute(f'''SELECT * FROM {month} WHERE {self.search_row}
                                LIKE ?''', self.str_search)
            self.search_contents = self.table_contents(self.db.c.fetchall())
            [self.tree.delete(i) for i in self.tree.get_children()]
            [self.tree.insert('', 'end', values=row) for row in self.search_contents]

            self.open_view_stat(self.search_contents)
        except:
            pass

    def redact(self):
        Update(self.month_tab())

    def open_search_dialog(self):
        Search(self.month_tab())

    def open_view_stat(self, tab):
        self.stata = Statistics(tab, self.month_tab())

    def close_process(self):
        self.tree.destroy()
        self.close_statistics()

    def close_statistics(self):
        self.stata.close_statstics()


class Update(tk.Toplevel):
    def __init__(self, month_address):
        try:
            super().__init__()
            self.init_update()
            self.month = month_address[0]
            self.address = month_address[1]
            self.year = month_address[2]
            self.main_view = month_address[3]
            self.db = DB(self.year, self.month)
            self.default_data()
        except TypeError:
            self.destroy()

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
        self.err_msg = tk.StringVar()
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

        self.check = (self.register(self.validate_comment), '%P')

        self.entry_comments = tk.Entry(self, validate='key', validatecommand=self.check, bg='white')
        self.entry_comments.place(x=200, y=130)
        self.entry_ws.focus_set()

        btn_cancel = tk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=310, y=170)
        btn_ok = tk.Button(self, text='Добавить')
        btn_ok.place(x=200, y=170)

        btn_ok.bind('<Button-1>', lambda event: Main.validate(self.address, self.month, self.entry_ws.get(),
                                                              self.entry_delivery.get(), self.entry_gw.get(),
                                                              self.entry_dr.get(), self.entry_comments.get()))
        btn_ok.bind('<Button-1>', lambda event: self.destroy(), add='+')

        self.grab_set()
        self.focus_set()

    def validate_comment(self, less_comment):
        str_comm = re.match('^.{0,69}$', less_comment) is not None
        if not str_comm:
            self.err_msg.set('69x69!')
        else:
            self.err_msg.set('')
        return str_comm

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


class Search(tk.Toplevel):
    def __init__(self, month_address):
        try:
            super().__init__()
            self.init_search()
            self.month = month_address[0]
            self.address = month_address[1]
        except TypeError:
            self.destroy()

    def init_search(self):
        self.title('Поиск')
        self.geometry('500x220+650+300')
        self.resizable(False, False)

        lable_tab_search = tk.Label(self, text='колонка')
        lable_tab_search.place(x=50, y=20)
        lable_search = tk.Label(self, text='Поиск')
        lable_search.place(x=50, y=50)

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
        btn_search.bind('<Button-1>', lambda event: Main.search_records(self.address, self.month,
                                                                        self.combo_tab.get(),
                                                                        self.entry_search.get()))
        btn_search.bind('<Button-1>', lambda event: self.destroy(), add='+')


class Statistics:
    def __init__(self, val_tab, arguments):
        self.stata = val_tab
        self.root_stat = arguments[4]
        print(self.stata)

        self.init_statistics()

    def init_statistics(self):
        self.label_shifts = tk.Label(self.root_stat, text='Смен')
        self.label_shifts.place(x=150, y=750)
        self.label_hours = tk.Label(self.root_stat, text='Часов')
        self.label_hours.place(x=150, y=780)

        self.value_amount_shifts = tk.StringVar()
        self.label_amount_shifts = tk.Label(self.root_stat, textvariable=self.value_amount_shifts)
        self.label_amount_shifts.place(x=250, y=750)
        self.value_amount_shifts.set(str(self.calc_statistics()))

        self.value_hours_shifts = tk.StringVar()
        self.label_hours_shifts = tk.Label(self.root_stat, textvariable=self.value_hours_shifts)
        self.label_hours_shifts.place(x=250, y=780)
        self.value_hours_shifts.set('276')

    def calc_statistics(self):
        count_shifts = 0
        count_hours = 0
        for item in self.stata:
            shifts = item[2]
            hours = item[3]
            if shifts != '' and shifts != '0':
                count_shifts += 1
            self.count_shifts = count_shifts
        return self.count_shifts

    def close_statstics(self):
        self.label_amount_shifts.destroy()
        self.label_hours_shifts.destroy()
        print('объекты закрыты')


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

