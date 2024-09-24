from functools import partial

class LOGIN():
    def __init__(self, shopping_db=None, page_controller=None, login_page=None):
        # Setup shopping database
        self.shopping_db = shopping_db

        # Setup page controller
        self.page_controller = page_controller

        # Setup login page parameters
        self.login_page = login_page
        self.login_page.account_edit.setFocus()
        self.login_page.account_edit.setPlaceholderText("請輸入學號")
        self.login_page.pwd_edit.setPlaceholderText("請輸入密碼")
        self.login_page.login_btn.clicked.connect(self.check_account_and_pwd)
        self.login_page.regis_btn.clicked.connect(partial(self.page_controller.change_page, from_page="login", to_page="regis"))

    def check_account_and_pwd(self):
        # Get input information and Print out
        stu_ID = self.login_page.account_edit.text()
        pwd = self.login_page.pwd_edit.text()
        print("Student ID: {}".format(stu_ID))
        print("Password: {}".format(pwd))

        # Check user is existed or not
        select_results = self.shopping_db.SELECT("SELECT user_ID FROM users WHERE stu_ID='%s' and pwd='%s'" %(stu_ID, pwd))
        if len(select_results) == 0:
            self.page_controller.show_warning_page("Warning", "Wrong student ID or password ! PLZ check it again~")
            print("Wrong student ID or password ! PLZ check it again~")
            return False
        else:
            current_user_ID = select_results[0][0]
            self.page_controller.current_user_ID = current_user_ID
            self.page_controller.change_page("login", "home")
