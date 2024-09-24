from datetime import datetime

class ITEM_INFO():
    def __init__(self, shopping_db=None, page_controller=None, item_info_page=None):
        # Setup shopping database
        self.shopping_db = shopping_db

        # Setup page controller
        self.page_controller = page_controller

        # Setup item_info page
        self.item_info_page = item_info_page
        self.item_info_page.buy_btn.clicked.connect(self.buy)

    def show_item_info(self, item_ID=None, qimage=None, name=None, price=None, status=None, note=None, buy_btn_enabled=False):
        self.selected_item_ID = item_ID
        self.item_info_page.image.setPixmap(qimage)
        self.item_info_page.name.setText("商品名稱: " + name)
        self.item_info_page.price.setText("商品售價: " + str(price))
        self.item_info_page.status.setText("商品狀態: " + status)
        self.item_info_page.note.setText("商品備註: " + note)
        self.item_info_page.buy_btn.setEnabled(buy_btn_enabled)

    def buy(self):
        # SELECT MAX(buy_order) FROM 'pre_order' TABLE
        max_buy_order = self.shopping_db.SELECT("SELECT MAX(buy_order) FROM pre_order WHERE item_ID='%s'" %(self.selected_item_ID))[0][0]
        max_buy_order = 0 if max_buy_order is None else max_buy_order
        
        # INSERT buy information INTO 'pre_order' TABLE
        buy_order = max_buy_order + 1
        buy_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO pre_order (item_ID, buyer, buy_time, buy_order) VALUES (%s, %s, %s, %s)"
        condition = (self.selected_item_ID, self.page_controller.get_current_user_ID(), buy_time, buy_order)
        self.shopping_db.TABLE_modify(sql, condition)

        # UPDATE status in 'items' TABLE
        sql = "UPDATE items SET status=%s WHERE item_ID=%s"
        condition = (0, self.selected_item_ID)
        self.shopping_db.TABLE_modify(sql, condition)

        self.page_controller.close_page("item_info")