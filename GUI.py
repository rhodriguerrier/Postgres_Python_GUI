import tkinter as tk
from connect import Connect
from pandastable import Table, TableModel
import bcrypt


def get_table_names():
    name_list = []
    query_string = """SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'public'"""
    with Connect() as temp_conn:
        table_name_df = temp_conn.get_table_with_query(query_string)

    for i in range(len(table_name_df.index)):
        name_list.append(table_name_df.iloc[i]['table_name'])

    return name_list


class FrameSwitcher(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.resizable(False, False)

        self.frames = {}
        for F in (LoginPage, StartPage, ViewTables, EnterData):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        def check_credentials(user_name, user_pswd):
            error_label['text'] = ""
            query_string = f'''SELECT * FROM "Users" WHERE "Username" = '{user_name}';'''
            with Connect() as conn:
                user_details = conn.get_table_with_query(query_string)

            if user_details.empty:
                error_label['text'] = "Username cannot be found."
                username_field.delete(0, tk.END)
                password_field.delete(0, tk.END)
                return

            db_hash = bytes(user_details.iloc[0]['Password'])
            if bcrypt.checkpw(user_pswd.encode('UTF-8'), db_hash):
                username_field.delete(0, tk.END)
                password_field.delete(0, tk.END)
                controller.show_frame("StartPage")
            else:
                error_label['text'] = "Password is incorrect."
                username_field.delete(0, tk.END)
                password_field.delete(0, tk.END)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        login_frame = tk.Frame(self)
        login_frame.grid(row=0, column=0, sticky="")
        title_label = tk.Label(login_frame, text="School Management System", font=("Helvetica", 26))
        title_label.grid(row=0, columnspan=2)
        instruction_label = tk.Label(login_frame, text="Please enter login details.")
        instruction_label.grid(row=1, columnspan=2)
        username_label = tk.Label(login_frame, text="Username:")
        username_label.grid(row=2, column=0)
        username_field = tk.Entry(login_frame)
        username_field.grid(row=2, column=1)
        password_label = tk.Label(login_frame, text="Password:")
        password_label.grid(row=3, column=0)
        password_field = tk.Entry(login_frame, show="*")
        password_field.grid(row=3, column=1)
        login_button = tk.Button(login_frame, text="Login",
                                 command=lambda: check_credentials(username_field.get(), password_field.get()))
        login_button.grid(row=4, columnspan=2)
        error_label = tk.Label(login_frame, text="", fg="red")
        error_label.grid(row=5, columnspan=2)


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        launchpad_frame = tk.Frame(self)
        launchpad_frame.grid(row=0, column=0, sticky="")
        program_title = tk.Label(launchpad_frame, text="School Database Management System")
        program_title.grid(row=0, columnspan=2)
        view_tables_button = tk.Button(launchpad_frame, text="View Existing Tables",
                                       command=lambda: controller.show_frame("ViewTables"))
        view_tables_button.grid(row=1, columnspan=2)
        enter_data_button = tk.Button(launchpad_frame, text="Enter New Data",
                                      command=lambda: controller.show_frame("EnterData"))
        enter_data_button.grid(row=2, columnspan=2)
        logout_button = tk.Button(launchpad_frame, text="Logout",
                                  command=lambda: controller.show_frame("LoginPage"))
        logout_button.grid(row=3, columnspan=2)


class ViewTables(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        def update_table(*args):
            update_query = f'''SELECT * FROM "{table_choice.get()}"'''
            with Connect() as my_conn_update:
                update_df = my_conn_update.get_table_with_query(update_query)
            dfTbl.updateModel(TableModel(update_df))
            dfTbl.redraw()

        table_choice = tk.StringVar(self)
        table_choice.set(OPTIONS[0])
        dropdown = tk.OptionMenu(self, table_choice, *OPTIONS)
        dropdown.grid(row=0, column=0, sticky="nesw")
        button2 = tk.Button(self, text="Back to Start Page",
                            command=lambda: controller.show_frame("StartPage"))
        button2.grid(row=0, column=1, sticky="nesw")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        frame_table = tk.Frame(self)
        frame_table.grid(row=1, columnspan=3)
        sql_query = f'''SELECT * FROM "{table_choice.get()}"'''
        with Connect() as my_conn:
            df = my_conn.get_table_with_query(sql_query)
        self.table = dfTbl = Table(frame_table, dataframe=df,
                                   showstatusbar=False, showtoolbar=False, editable=False)
        dfTbl.show()
        table_choice.trace("w", update_table)


class EnterData(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        def update_col_names(*args):
            for widget in frame_form.winfo_children():
                widget.destroy()
            update_query = f"""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_choice.get()}'"""
            with Connect() as my_db_conn_update:
                update_df = my_db_conn_update.get_table_with_query(update_query)
            widgets_list = []
            for i in range(1, len(update_df)):
                temp_label = tk.Label(frame_form, text=update_df.iloc[i]['column_name'])
                widgets_list.append(temp_label)
                temp_field = tk.Entry(frame_form)
                widgets_list.append(temp_field)

            for j in widgets_list:
                j.pack()

        def submit_data():
            column_names_list = []
            data_submit_list = []
            for widget in frame_form.winfo_children():
                if isinstance(widget, tk.Entry):
                    if widget.get().isdigit():
                        data_submit_list.append(widget.get())
                    else:
                        data_submit_list.append("'"+widget.get()+"'")
                    widget.delete(0, tk.END)
                else:
                    column_names_list.append('"'+widget.cget("text")+'"')
            column_string = ', '.join(column_names_list)
            data_string = ', '.join(data_submit_list)
            query_string = f"""INSERT INTO "{table_choice.get()}" ({column_string}) VALUES ({data_string});"""
            with Connect() as conn_write:
                try:
                    conn_write.write_data_to_table(query_string)
                    print("Successfully written to database")
                except Exception as error:
                    print("Something went wrong!" + error)
                    print(type(error))

        table_choice = tk.StringVar(self)
        dropdown = tk.OptionMenu(self, table_choice, *OPTIONS)
        dropdown.grid(row=0, column=0, sticky="nesw")
        submit_button = tk.Button(self, text="Submit Data to Table",
                                  command=lambda: submit_data())
        submit_button.grid(row=0, column=1, sticky="nesw")
        back_to_start_button = tk.Button(self, text="Back to Start Page",
                                         command=lambda: controller.show_frame("StartPage"))
        back_to_start_button.grid(row=0, column=2, sticky="nesw")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        frame_form = tk.Frame(self)
        frame_form.grid(row=1, columnspan=3)
        table_choice.trace('w', update_col_names)


OPTIONS = get_table_names()
app = FrameSwitcher()
app.mainloop()
