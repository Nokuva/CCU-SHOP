from PyQt5.QtGui import QPixmap, QImage
from functools import partial
from io import BytesIO
from PIL import Image, ImageQt
from datetime import datetime

class HOME():
    def __init__(self, shopping_db=None, page_controller=None, home_page=None):
        # Setup shopping database
        self.shopping_db = shopping_db

        # Setup page controller
        self.page_controller = page_controller

        # Setup home page parameters
        self.home_page = home_page
        self.home_page.search_bar.setFocus()
        self.home_page.search_bar.setPlaceholderText("眼影、衣服、腳踏車、costco鮮奶......")
        # Collect item image, name, price, note, status
        self.page_images = [self.home_page.image_1, self.home_page.image_2, self.home_page.image_3, self.home_page.image_4, self.home_page.image_5, self.home_page.image_6]
        self.page_names = [self.home_page.name_1, self.home_page.name_2, self.home_page.name_3, self.home_page.name_4, self.home_page.name_5, self.home_page.name_6]
        self.page_prices = [self.home_page.price_1, self.home_page.price_2, self.home_page.price_3, self.home_page.price_4, self.home_page.price_5, self.home_page.price_6]
        self.page_statuss = [self.home_page.status_1, self.home_page.status_2, self.home_page.status_3, self.home_page.status_4, self.home_page.status_5, self.home_page.status_6]
        self.page_info_btns = [self.home_page.info_btn_1, self.home_page.info_btn_2, self.home_page.info_btn_3, self.home_page.info_btn_4, self.home_page.info_btn_5, self.home_page.info_btn_6]
        self.page_buy_btns = [self.home_page.buy_btn_1, self.home_page.buy_btn_2, self.home_page.buy_btn_3, self.home_page.buy_btn_4, self.home_page.buy_btn_5, self.home_page.buy_btn_6]
        # Setup status indicator
        for status in self.page_statuss:
            status.setText("")
            status.setStyleSheet("border-radius: 5px; background-color: ;")
        # Setup button
        self.home_page.mystore_btn.clicked.connect(partial(self.page_controller.change_page, from_page="home", to_page="mystore"))
        self.home_page.stay_btn.clicked.connect(partial(self.page_controller.change_page, from_page="home", to_page="stay"))
        for idx, info_btn in enumerate(self.page_info_btns):
            info_btn.clicked.connect(partial(self.show_item_info_page, idx=idx))
        for idx, buy_btn in enumerate(self.page_buy_btns):
            buy_btn.clicked.connect(partial(self.buy, idx=idx))
        self.home_page.prepage_btn.clicked.connect(self.pre_page)
        self.home_page.nextpage_btn.clicked.connect(self.next_page)
        
        # Predefine status indicator and table
        self.status_indicator = {0: "yellow", 1: "green", 2: "red"}
        self.status_table = {0: "有人排", 1: "有貨", 2: "已售空"}

    def show_item_info_page(self, idx=-1):
        # Get SELECT results from 'items' TABLE
        selected_item_ID = self.item_IDs[self.start_idx:self.start_idx+6][idx]
        binary_image = self.all_uploaded_items[selected_item_ID]["image"]
        name = self.all_uploaded_items[selected_item_ID]["name"]
        price = self.all_uploaded_items[selected_item_ID]["price"]
        status = self.all_uploaded_items[selected_item_ID]["status"]
        note = self.all_uploaded_items[selected_item_ID]["note"]

        # Convert image and status
        qimage = QPixmap.fromImage(self.convert_binary_image_to_qimage(binary_image))
        status = self.status_table[status]

        # Get buy_btn is enabled or not
        select_results = self.shopping_db.SELECT("SELECT * FROM items, pre_order WHERE (items.item_ID='%s' and items.owner='%s') or (pre_order.item_ID='%s' and pre_order.buyer='%s')" %(selected_item_ID, self.page_controller.get_current_user_ID(), selected_item_ID, self.page_controller.get_current_user_ID()))
        buy_btn_enabled = True if len(select_results) == 0 else False

        # Pass to item_info_class
        item_info_class = self.page_controller.get_page_class("item_info")
        item_info_class.show_item_info(item_ID=selected_item_ID, qimage=qimage, name=name, price=price, status=status, note=note, buy_btn_enabled=buy_btn_enabled)
        self.page_controller.show_page("item_info")

    def buy(self, idx=-1):
        # Get selected item_ID
        selected_item_ID = self.item_IDs[self.start_idx:self.start_idx+6][idx]

        # SELECT MAX(buy_order) FROM 'pre_order' TABLE
        max_buy_order = self.shopping_db.SELECT("SELECT MAX(buy_order) FROM pre_order WHERE item_ID='%s'" %(selected_item_ID))[0][0]
        max_buy_order = 0 if max_buy_order is None else max_buy_order
        
        # INSERT buy information INTO 'pre_order' TABLE
        buy_order = max_buy_order + 1
        buy_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO pre_order (item_ID, buyer, buy_time, buy_order) VALUES (%s, %s, %s, %s)"
        condition = (selected_item_ID, self.page_controller.get_current_user_ID(), buy_time, buy_order)
        self.shopping_db.TABLE_modify(sql, condition)

        # UPDATE status in 'items' TABLE
        sql = "UPDATE items SET status=%s WHERE item_ID=%s"
        condition = (0, selected_item_ID)
        self.shopping_db.TABLE_modify(sql, condition)

        # Reset home_page
        self.reset_home_items()

    def reset_home_items(self):
        # Setup uploaded items
        self.start_idx = 0
        self.item_IDs = []
        self.all_uploaded_items = dict()
        
        # Load items from DATABASE
        select_results = self.shopping_db.SELECT("SELECT item_ID, image, item_name, price, note, status FROM items WHERE status!=2 ORDER BY uploadtime DESC")
        for item_ID, image, item_name, price, note, status in select_results:
            # Save SELECT results
            print(item_ID, item_name, price, note, status)
            self.item_IDs.append(item_ID)
            self.all_uploaded_items[item_ID] = dict()
            self.all_uploaded_items[item_ID]["image"] = BytesIO(image)
            self.all_uploaded_items[item_ID]["name"] = item_name
            self.all_uploaded_items[item_ID]["price"] = str(price)
            self.all_uploaded_items[item_ID]["note"] = note
            self.all_uploaded_items[item_ID]["status"] = status

        # Enabled next_page button if total number of items is bigger than 6
        print("Total number of items: {}".format(len(self.item_IDs)))
        if len(self.item_IDs) > 6:
            self.home_page.nextpage_btn.setEnabled(True)

        # Show items
        self.show_items()

    def reset_show_items(self):
        for page_image, page_name, page_price, page_status, page_info_btn, page_buy_btn in zip(self.page_images, self.page_names, self.page_prices, self.page_statuss, self.page_info_btns, self.page_buy_btns):
            # Setup mystore page
            page_image.setText("商品圖片:")
            page_name.setText("      商品名稱:")
            page_price.setText("      商品售價:")
            page_status.setStyleSheet("border-radius: 5px; background-color: ;")
            page_info_btn.setEnabled(False)
            page_buy_btn.setEnabled(False)

        # Show items
        self.show_items()
        
    def show_items(self):
        for idx, item_ID, page_image, page_name, page_price, page_status in zip(range(6), self.item_IDs[self.start_idx:self.start_idx+6], self.page_images, self.page_names, self.page_prices, self.page_statuss):
            # Load item information from all_uploaded_items
            image = self.all_uploaded_items[item_ID]["image"]
            name = self.all_uploaded_items[item_ID]["name"]
            price = self.all_uploaded_items[item_ID]["price"]
            status = self.all_uploaded_items[item_ID]["status"]
            
            # Setup mystore page
            page_image.setPixmap(QPixmap.fromImage(self.convert_binary_image_to_qimage(image)))
            page_name.setText("      商品名稱: " + name)
            page_price.setText("      商品售價: " + price)
            page_status.setStyleSheet("border-radius: 5px; background-color: " + self.status_indicator[status] + ";")
            self.page_info_btns[idx].setEnabled(True)

            # Enabled buy button if status != 2 in the 'items' TABLE
            select_results = self.shopping_db.SELECT("SELECT * FROM items, pre_order WHERE (items.item_ID='%s' and items.owner='%s') or (pre_order.item_ID='%s' and pre_order.buyer='%s')" %(item_ID, self.page_controller.get_current_user_ID(), item_ID, self.page_controller.get_current_user_ID()))
            self.page_buy_btns[idx].setEnabled(True if len(select_results) == 0 else False)

    def pre_page(self):
        if self.start_idx - 6 >= 0:
            self.start_idx -= 6
            self.home_page.pages.setText(str(int((self.start_idx / 6) + 1)))
            self.reset_show_items()
            self.home_page.nextpage_btn.setEnabled(True)
            self.home_page.prepage_btn.setEnabled(False if self.start_idx - 6 < 0 else True)
        else:
            self.page_controller.show_warning_page("Warning", "已經到第一頁囉^^")
        print("Run pre_page, start index: {}".format(self.start_idx))
    
    def next_page(self):
        if self.start_idx + 6 < len(self.item_IDs):
            self.start_idx += 6
            self.home_page.pages.setText(str(int((self.start_idx / 6) + 1)))
            self.reset_show_items()
            self.home_page.prepage_btn.setEnabled(True)
            self.home_page.nextpage_btn.setEnabled(False if self.start_idx + 6 >= len(self.item_IDs) else True)
        else:
            self.page_controller.show_warning_page("Warning", "已經到最後一頁囉^^")
        print("Run next_page, start index: {}".format(self.start_idx))

    def convert_binary_image_to_qimage(self, img):
        img = Image.open(img)
        # Resize image to fit label size
        img_w, img_h = img.size
        if img_w > img_h:
            img = img.resize((253, int(img_h * 253 / img_w)))
            img_w, img_h = img.size
            if img_h > 171:
                img = img.resize((int(img_w * 171 / img_h), 171))
        else:
            img = img.resize((int(img_w * 171 / img_h), 171))
            img_w, img_h = img.size
            if img_w > 253:
                img = img.resize((253, int(img_h * 253 / img_w)))
        q_image = ImageQt.ImageQt(img) # Convert PIL image to QImage
        
        return q_image
