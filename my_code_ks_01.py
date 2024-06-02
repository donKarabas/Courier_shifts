
# При первом открытии таблицы заполняет столбцы: "Дата", "день".
# При открытии таблицы кнопка "Открыть отключается".

import tkinter as tk
from tkinter import ttk
import sqlite3
import datetime
from calendar import monthrange


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

        label_year = tk.Label(toolbar, text='год')
        label_year.place(x=760, y=5)
        label_month = tk.Label(toolbar, text='месяц')
        label_month.place(x=737, y=30)

        self.ls_month = ["Jan", "Feb", "Marc", "Apr", "May", "June", "July", "Aug",
                         "Sept", "Oct", "Nov", "Dec"]

        self.ind_month = int(datetime.datetime.now().strftime('%m'))
        self.cur_year = int(datetime.datetime.now().strftime('%Y'))
        self.ls_year_int = [self.cur_year-1, self.cur_year, self.cur_year+1]
        self.ls_year = [str(self.ls_year_int[0]), str(self.ls_year_int[1]), str(self.ls_year_int[2])]

        self.combobox_year = ttk.Combobox(toolbar, width=4, values=[self.ls_year[0], self.ls_year[1],
                                                                    self.ls_year[2]])
        self.combobox_year.current(1)
        self.combobox_year.place(x=800, y=5)

        self.combobox_month = ttk.Combobox(toolbar, width=5, values=[self.ls_month[0], self.ls_month[1],
                                        self.ls_month[2], self.ls_month[3], self.ls_month[4], self.ls_month[5],
                                        self.ls_month[6], self.ls_month[7], self.ls_month[8], self.ls_month[9],
                                                                     self.ls_month[10], self.ls_month[11]])
        self.combobox_month.current(self.ind_month-1)
        self.combobox_month.place(x=800, y=30)

        self.button_start(toolbar)

    def button_start(self, toolbar):
        btn_open_dialog = tk.Button(toolbar, text='Открыть')
        btn_open_dialog.place(x=800, y=55)
        btn_open_dialog.bind('<Button-1>', lambda event: self.open_table(self.combobox_year.get(),
                                                                    self.combobox_month.get(), toolbar))

    def open_table(self, year, month, toolbar):
        self.ls_data = [year, month]
        self.db = DB(self.ls_data[0], self.ls_data[1])

        self.tree = ttk.Treeview(self.root, columns=('ID', 'day_week', 'work_shift', 'delivery'),
                                 height=31, show='headings')

        self.tree.column('ID', width=80, anchor=tk.CENTER)
        self.tree.column('day_week', width=80, anchor=tk.CENTER)
        self.tree.column('work_shift', width=100, anchor=tk.CENTER)
        self.tree.column('delivery', width=100, anchor=tk.CENTER)

        self.tree.heading('ID', text='Дата')
        self.tree.heading('day_week', text='день')
        self.tree.heading('work_shift', text='См. (часы)')
        self.tree.heading('delivery', text='Достав.')

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
                date = datetime.datetime(int_year, ind_month, n+1)
                ind_week = date.weekday()
                day_week = day_weeks[ind_week]
                self.db.c.execute(f'''INSERT INTO {month} (ID, day_week, work_shift, delivery)
                                    VALUES(?, ?, ?, ?)''',
                                  (n+1, day_week, '', ''))
            self.db.conn.commit()

        self.view_records(self.ls_data[1])

        btn_open_dialog = tk.Button(toolbar, state='disabled', text='Открыть')
        btn_open_dialog.place(x=800, y=55)

        self.close_table(toolbar)

    def close_table(self, toolbar):
        btn_close = tk.Button(self.root, text='Закрыть', command=self.tree.destroy)
        btn_close.place(x=910, y=55)
        btn_close.bind('<Button-1>', lambda event: self.button_start(toolbar))

    def redact(self):
        pass

    def view_records(self, month):
        self.month_table = month
        self.db.c.execute(f'''SELECT * FROM {self.month_table}''')
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]


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
                        work_shift INTEGER,
                        delivery INTEGER)''')
        self.conn.commit()


if __name__ == '__main__':
    main = Main()

