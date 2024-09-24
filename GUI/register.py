from functools import partial

class REGISTER():
    def __init__(self, shopping_db=None, page_controller=None, regis_page=None):
        # Setup shopping database
        self.shopping_db = shopping_db

        # Setup regis_page
        self.page_controller = page_controller

        # Setup regis page parameters
        self.regis_page = regis_page
        self.regis_page.ID_edit.setFocus()
        self.regis_page.ID_edit.setPlaceholderText("請輸入學號")
        self.regis_page.pwd_edit.setPlaceholderText("請輸入密碼")
        self.regis_page.pwd_edit_2.setPlaceholderText("請再次輸入密碼")
        self.regis_page.email_edit.setPlaceholderText("請輸入信箱")
        self.regis_page.regis_btn.clicked.connect(self.check_regis_info)
        self.regis_page.return_btn.clicked.connect(self.return_to_login)

    def check_regis_info(self):
        # Get input information and Print out
        stu_ID = self.regis_page.ID_edit.text()
        pwd = self.regis_page.pwd_edit.text()
        pwd_2 = self.regis_page.pwd_edit_2.text()
        email = self.regis_page.email_edit.text()
        print("Student ID: {}".format(stu_ID))
        print("Password: {}".format(pwd))
        print("Password_again: {}".format(pwd_2))
        print("Email: {}".format(email))

        # Prevent invaild input
        if stu_ID == "" or pwd == "" or pwd_2 == "" or email == "":
            self.page_controller.show_warning_page("Warning", "Invaild value. All column should be filled !!!")
            print("Invaild value. All column should be filled !!!")
            return False

        if pwd != pwd_2:
            self.page_controller.show_warning_page("Warning", "Inconsistent password. PLZ check your password again !!!")
            print("Inconsistent password. PLZ check your password again !!!")
            return False

        # SELECT MAX(user_ID) FROM 'users' TABLE
        max_user_ID = self.shopping_db.SELECT("SELECT MSX(user_ID) FROM users")[0][0]
        max_user_ID = "S000" if max_user_ID is None else max_user_ID

        # INSERT user information
        sql = "INSERT INTO users (user_ID, stu_ID, pwd, email) VALUES (%s, %s, %s, %s)"
        condition = ("S%03d" %(int(max_user_ID[1:])+1), stu_ID, pwd, email)
        self.shopping_db.TABLE_modify(sql, condition)

        # Change to login page
        self.reset_page()
        self.page_controller.change_page("regis", "login")

    def return_to_login(self):
        self.reset_page()
        self.page_controller.change_page(from_page="regis", to_page="login")

    def reset_page(self):
        # Clear lineEdit
        self.regis_page.ID_edit.setText("")
        self.regis_page.pwd_edit.setText("")
        self.regis_page.pwd_edit_2.setText("")
        self.regis_page.email_edit.setText("")

        # Reset lineEdit
        self.regis_page.ID_edit.setFocus()
        self.regis_page.ID_edit.setPlaceholderText("請輸入學號")
        self.regis_page.pwd_edit.setPlaceholderText("請輸入密碼")
        self.regis_page.pwd_edit_2.setPlaceholderText("請再次輸入密碼")
        self.regis_page.email_edit.setPlaceholderText("請輸入信箱")
