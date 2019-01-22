from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Treeview
import pexpect
from pyperclip import *

DB_PATH: str = "/home/user/password_file"


class Titan:
    window: Tk = Tk(className="Titan")
    loggedIn: bool = False
    show: bool = False

    def __init__(self):
        self.window.title("Titan - Login")
        self.window.resizable(False, False)
        self.window.bind("<Destroy>", self.destroy_root)
        self.set_size_and_center(290, 70)

        self.define_widgets()

        self.window.mainloop()

    def password_copy(self):
        password_list = self.get_widget_by_name(".passwordList")
        item = password_list.focus()
        password = password_list.item(item)["values"][3]
        copy(password)
        showinfo("Titan", "Password copied to clipboard")

    def remove_password(self):
        password_list = self.get_widget_by_name(".passwordList")
        item = password_list.focus()
        identifier = password_list.item(item)["values"][0]
        self.expect_spawn("titan -r " + str(identifier))
        self.get_passwords()

    def define_widgets(self):
        context_menu = Menu(self.window, tearoff=0, name="contextMenu")
        context_menu.add_command(label="Copy password", command=self.password_copy)
        context_menu.add_command(label="Edit entry")
        context_menu.add_command(label="Delete entry", command=self.remove_password)

        password_label = Label(self.window, text="Enter master password", anchor=NW, font=("Arial", 16))
        password_label.grid(row=0)

        password = Entry(self.window, name="password", show="*", font=("Arial", 16))
        password.grid(row=1, pady=5)
        password.bind("<Return>", self.login)

        menu_bar = Menu(self.window, name="menuBar")
        file_menu = Menu(menu_bar, tearoff=0)
        option_menu = Menu(menu_bar, tearoff=0, name="optionMenu")

        file_menu.add_command(label="Exit", command=self.window.destroy)

        option_menu.add_command(label="Show passwords", command=self.show_passwords)
        option_menu.add_command(label="Hide passwords", command=self.hide_passwords)
        option_menu.add_separator()
        option_menu.add_command(label="Add en entry", command=self.add_entry_view)
        option_menu.add_separator()
        option_menu.add_command(label="Change master password", command=self.change_password)

        option_menu.entryconfig(1, state=DISABLED)

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Options", menu=option_menu)

        password_list = Treeview(self.window, name="passwordList", height=10)
        password_list['show'] = 'headings'
        password_list["columns"] = ("ID", "Title", "Username", "Password", "Password ")
        password_list.column("ID", stretch=False, minwidth=50, width=50)
        password_list.column("Title", stretch=False, minwidth=300, width=300)
        password_list.column("Username", stretch=False, minwidth=300, width=300)
        password_list.column("Password", stretch=False, minwidth=300, width=300)
        password_list.column("Password ", stretch=False, minwidth=300, width=300)
        password_list.heading("ID", text="ID")
        password_list.heading("Title", text="Title")
        password_list.heading("Username", text="Username")
        password_list.heading("Password", text="Password")
        password_list.heading("Password ", text="Password")
        password_list.bind("<Button-3>", self.right_click_password)
        password_list.bind("<Button-1>", self.left_click_password)

        Scrollbar(self.window, orient="vertical", command=password_list.yview, name="vScroll")

        Label(self.window, name="titleLabel", text="Enter the title", anchor="e", font=("Arial", 16), justify=RIGHT)
        Label(self.window, name="userLabel", text="Enter the username", anchor="e", font=("Arial", 16), justify=RIGHT)
        Label(self.window, name="passwordLabel", text="Enter password", anchor="e", font=("Arial", 16), justify=RIGHT)
        Entry(self.window, name="newPassword", show="*", font=("Arial", 16))
        Entry(self.window, name="newTitle", font=("Arial", 16))
        Entry(self.window, name="newUser", font=("Arial", 16))
        Button(self.window, name="newEntry", text="Create entry", command=self.add_entry)
        Button(self.window, name="cancelNewEntry", text="Cancel", command=self.display_main_view)

    def forget_all(self):
        for x in self.window.winfo_children():
            x.grid_forget()
            x.pack_forget()
            x.place_forget()

    def destroy_root(self):
        if self.loggedIn:
            self.loggedIn = False
            password = self.window.nametowidget(".password").get()
            self.expect_spawn("titan -e", {"Password: ": password, "Password again: ": password})

    def get_widget_by_name(self, name, parent=None):
        if parent is None:
            for x in self.window.winfo_children():
                if str(x) == name:
                    return x
        else:
            for x in parent.winfo_children():
                if str(x) == name:
                    return x

    def get_entry_value(self, name):
        value = ""
        for x in self.window.winfo_children():
            if str(x) == name:
                try:
                    value = x.get()
                except:
                    pass
        return value

    def set_size_and_center(self, wr, hr):
        ws = self.window.winfo_screenwidth()  # width of the screen
        hs = self.window.winfo_screenheight()  # height of the screen
        x = (ws / 2) - (wr / 2)
        y = (hs / 2) - (hr / 2)
        self.window.geometry('%dx%d+%d+%d' % (wr, hr, x, y))

    def login(self, event):
        caller = event.widget
        password = caller.get()
        response = self.expect_spawn("titan -d " + DB_PATH, {"Password: ": password})
        if "Invalid" in str(response):
            showerror("Titan", "Bad password")
        else:
            self.loggedIn = True
            self.display_main_view()

    @staticmethod
    def expect_spawn(command, expect=None):
        if expect is None:
            expect = {}
        spawn = pexpect.spawn(command)
        for x in expect:
            spawn.expect(x)
            spawn.sendline(expect.get(x))
        response = spawn.read()
        spawn.terminate(True)
        return response

    def left_click_password(self):
        self.get_widget_by_name(".contextMenu").unpost()

    def right_click_password(self, event):
        self.get_widget_by_name(".contextMenu").post(event.x_root, event.y_root)

    def display_main_view(self):
        self.forget_all()
        self.window.title("Titan")
        self.set_size_and_center(960, 230)
        self.window.config(menu=self.get_widget_by_name(".menuBar"))
        self.get_passwords()

    def show_passwords(self):
        option_menu = self.get_widget_by_name(".menuBar.optionMenu", self.get_widget_by_name(".menuBar"))
        option_menu.entryconfig(0, state=DISABLED)
        option_menu.entryconfig(1, state=NORMAL)
        self.show = True
        self.get_passwords()

    def hide_passwords(self):
        self.show = False
        self.get_passwords()

    def get_passwords(self):
        password_list = self.get_widget_by_name(".passwordList")
        list_titan = self.expect_spawn("titan --show-passwords -A")
        if self.show:
            password_list["displaycolumns"] = ("ID", "Title", "Username", "Password")
        else:
            password_list["displaycolumns"] = ("ID", "Title", "Username", "Password ")
            option_menu = self.get_widget_by_name(".menuBar.optionMenu", self.get_widget_by_name(".menuBar"))
            option_menu.entryconfig(0, state=NORMAL)
            option_menu.entryconfig(1, state=DISABLED)
        entry = str(list_titan).split(
            "\\r\\n\\x1b[0m=====================================================================\\r\\n================="
            "====================================================\\r\\n\\x1b[0m")

        password_list.delete(*password_list.get_children())
        for x in entry:
            identifier = x.split("ID: ")[1].split("\\r")[0]
            title = x.split("Title: ")[1].split("\\r")[0]
            username = x.split("User: ")[1].split("\\r")[0]
            password = x.split("Password: ")[1].split("\\r")[0]
            password_list.insert("", "end", values=(identifier, title, username, password, "*"*10))

        password_list.pack()
        self.window.update()
        self.get_widget_by_name(".vScroll").place(x=950, y=0, height=password_list.winfo_height())
        password_list.configure(yscrollcommand=self.get_widget_by_name(".vScroll").set)

    def remove_menu(self):
        empty_menu = Menu(self.window)
        self.window.config(menu=empty_menu)

    def add_entry_view(self):
        self.forget_all()
        self.remove_menu()
        self.window.title("Titan - Add a entry")
        self.window.nametowidget(".titleLabel").grid(row=0, column=0, sticky=E)
        self.window.nametowidget(".newTitle").grid(row=0, column=1, columnspan=2)
        self.window.nametowidget(".userLabel").grid(row=1, column=0, sticky=E)
        self.window.nametowidget(".newUser").grid(row=1, column=1, columnspan=2)
        self.window.nametowidget(".passwordLabel").grid(row=2, column=0, sticky=E)
        self.window.nametowidget(".newPassword").grid(row=2, column=1, columnspan=2)
        self.window.nametowidget(".newEntry").grid(row=4, column=2)
        self.window.nametowidget(".cancelNewEntry").grid(row=4, column=1)
        self.window.nametowidget(".newUser").delete(0, END)
        self.window.nametowidget(".newTitle").delete(0, END)
        self.window.nametowidget(".newPassword").delete(0, END)
        self.set_size_and_center(500, 130)

    def add_entry(self):
        title = self.window.nametowidget(".newTitle").get()
        username = self.window.nametowidget(".newUser").get()
        password = self.window.nametowidget(".newPassword").get()
        self.expect_spawn("titan -a", {"Title: ": title, "Username: ": username, "Url: ": "", "Notes: ": "",
                                       "Password ": password})
        self.display_main_view()

    def change_password(self):
        self.forget_all()
        self.remove_menu()
        self.set_size_and_center(380, 70)
        self.window.nametowidget(".password").delete(0, END)
        password_label = Label(self.window, text="Enter the new master password", anchor=NW, font=("Arial", 16))
        password_label.grid(row=0)

        self.window.nametowidget(".password").config(show="")
        self.window.nametowidget(".password").grid(row=1, pady=5)
        self.window.nametowidget(".password").bind("<Return>", self.display_main_view)


def main():
    root = Titan()


if __name__ == '__main__':
    main()
