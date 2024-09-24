from PyQt5 import QtWidgets, uic
from shopping_DB import shopping_DB
from GUI.page_controller import PAGE_CONTROLLER
from GUI.login import LOGIN
from GUI.register import REGISTER
from GUI.home import HOME
from GUI.item_info import ITEM_INFO
from GUI.mystore import MYSTORE
from GUI.additem import ADDITEM
from GUI.stay import STAY
from GUI.history import HISTORY

if __name__ == "__main__":
    # Start PyQt program
    app = QtWidgets.QApplication([])

    # Load each page
    login_page = uic.loadUi("GUI/ui_file/login.ui")
    regis_page = uic.loadUi("GUI/ui_file/regis.ui")
    home_page = uic.loadUi("GUI/ui_file/home.ui")
    item_info_page = uic.loadUi("GUI/ui_file/item_info.ui")
    mystore_page = uic.loadUi("GUI/ui_file/mystore.ui")
    additem_page = uic.loadUi("GUI/ui_file/additem.ui")
    stay_page = uic.loadUi("GUI/ui_file/stay.ui")
    history_page = uic.loadUi("GUI/ui_file/history.ui")

    # Create shopping database based on specific host
    host = '127.0.0.1'
    shopping_db = shopping_DB(host)

    # CREATE needed TABLE IF NOT EXISTS
    shopping_db.CREATE_TABLE(
        # 'users' TABLE
        "CREATE TABLE IF NOT EXISTS users ( \
            user_ID VARCHAR(4) PRIMARY Key, \
            stu_ID VARCHAR(10),             \
            pwd VARCHAR(20),                \
            email VARCHAR(20)               \
        )"
    )
    shopping_db.CREATE_TABLE(
        # 'items' TABLE
        "CREATE TABLE IF NOT EXISTS items ( \
            item_ID VARCHAR(4) PRIMARY Key, \
            image MEDIUMBLOB,               \
            item_name VARCHAR(10),          \
            price INTEGER,                  \
            owner VARCHAR(4),               \
            note VARCHAR(200),              \
            uploadtime DATETIME,            \
            status INTEGER                  \
        )"
    )
    shopping_db.CREATE_TABLE(
        # 'pre_order' TABLE
        "CREATE TABLE IF NOT EXISTS pre_order ( \
            item_ID VARCHAR(4),                 \
            buyer VARCHAR(4),                   \
            buy_time DATETIME,                  \
            buy_order INTEGER                   \
        )"
    )

    # Setup each page
    page_controller = PAGE_CONTROLLER()
    login = LOGIN(shopping_db, page_controller, login_page)
    regis = REGISTER(shopping_db, page_controller, regis_page)
    home = HOME(shopping_db, page_controller, home_page)
    item_info = ITEM_INFO(shopping_db, page_controller, item_info_page)
    mystore = MYSTORE(shopping_db, page_controller, mystore_page)
    additem = ADDITEM(shopping_db, page_controller, additem_page)
    stay = STAY(shopping_db, page_controller, stay_page)
    history = HISTORY(shopping_db, page_controller, history_page)

    # Setup page_name, page, page_class into page controller
    page_names = ["login", "regis", "home", "item_info", "mystore", "additem", "stay", "history"]
    pages = [login.login_page, regis.regis_page, home.home_page, item_info.item_info_page, mystore.mystore_page, additem.additem_page, stay.stay_page, history.history_page]
    pages_class = [login, regis, home, item_info, mystore, additem, stay, history]
    for page_name, page, page_class in zip(page_names, pages, pages_class):
        page_controller.set_page(page_name, page)
        page_controller.set_page_class(page_name, page_class)
    
    print("All page: {}".format(page_controller.get_page()))
    
    # Start shopping store
    login_page = page_controller.get_page("login")
    page_controller.show_page("login")

    app.exec()
