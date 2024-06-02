# Установлен TreeView, БД, кнопка "Открыть" настроена:
# по выбранному году назначает имя, создаёт, открывает БД,
# по выбранному месяцу создаёт таблицу, открывает таблицу.


import tkinter as tk
from tkinter import ttk
import sqlite3


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

        self.ls_year = ['2024', '2025']
        self.combobox_year = ttk.Combobox(toolbar, width=4, values=[self.ls_year[0], self.ls_year[1]])
        self.combobox_year.current(0)
        self.combobox_year.place(x=800, y=5)

        self.ls_month = ["Jan", "Feb", "Marc", "Apr", "May", "June", "July", "Aug",
                        "Sept", "Oct", "Nov", "Dec"]
        self.combobox_month = ttk.Combobox(toolbar, width=5, values=[self.ls_month[0], self.ls_month[1],
                                        self.ls_month[2], self.ls_month[3], self.ls_month[4], self.ls_month[5],
                                        self.ls_month[6], self.ls_month[7], self.ls_month[8], self.ls_month[9],
                                                                     self.ls_month[10], self.ls_month[11]])
        self.combobox_month.current(0)
        self.combobox_month.place(x=800, y=30)

        btn_open_dialog = tk.Button(toolbar, text='Открыть')
        btn_open_dialog.place(x=800, y=55)
        btn_open_dialog.bind('<Button-1>', lambda event: self.open_table(self.combobox_year.get(),
                                                                         self.combobox_month.get()))

        self.tree = ttk.Treeview(self.root, columns=('ID', 'work_shift', 'delivery'), height=30, show='headings')

        self.tree.column('ID', width=80, anchor=tk.CENTER)
        self.tree.column('work_shift', width=100, anchor=tk.CENTER)
        self.tree.column('delivery', width=100, anchor=tk.CENTER)

        self.tree.heading('ID', text='Дата')
        self.tree.heading('work_shift', text='См. (часы)')
        self.tree.heading('delivery', text='Достав.')

        self.tree.pack()

    def open_table(self, year, month):
        self.ls_data = [year, month]
        self.db = DB(self.ls_data[0], self.ls_data[1])
        self.view_records(self.ls_data[1])

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
                        work_shift INTEGER,
                        delivery INTEGER)''')
        self.conn.commit()


if __name__ == '__main__':
    main = Main()
