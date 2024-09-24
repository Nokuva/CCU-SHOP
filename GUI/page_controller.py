from PyQt5.QtWidgets import QMessageBox

class PAGE_CONTROLLER():
    def __init__(self):
        self.pages = dict()
        self.pages_class = dict()
        self.current_user_ID = None

    def set_current_user_ID(self, current_user_ID):
        self.current_user_ID = current_user_ID
    
    def get_current_user_ID(self):
        return self.current_user_ID

    def set_page(self, page_name, page):
        self.pages[page_name] = page

    def get_page(self, page_name=None):
        return self.pages[page_name] if page_name is not None else self.pages
    
    def set_page_class(self, page_name, page_class):
        self.pages_class[page_name] = page_class

    def get_page_class(self, page_name=None):
        return self.pages_class[page_name] if page_name is not None else self.pages_class

    def change_page(self, from_page, to_page):
        self.close_page(from_page)
        self.show_page(to_page)

    def show_page(self, page_name):
        if page_name == "mystore" :
            self.pages_class[page_name].reset_mystore_items()
        elif page_name == "home":
            self.pages_class[page_name].reset_home_items()
        elif page_name == "stay":
            self.pages_class[page_name].reset_buy_items()
        
        self.pages[page_name].show()

    def close_page(self, page_name):
        if page_name == "additem":
            self.pages_class["mystore"].reset_mystore_items()
        if page_name == "item_info":
            self.pages_class["home"].reset_home_items()
        
        self.pages[page_name].close()

    def show_warning_page(self, title, message):
        QMessageBox.information(None, title, message)