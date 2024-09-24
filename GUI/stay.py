from PyQt5.QtGui import QPixmap, QImage
from functools import partial
from io import BytesIO
from PIL import Image, ImageQt

class STAY():
    def __init__(self, shopping_db=None, page_controller=None, stay_page=None):
        # Setup shopping database
        self.shopping_db = shopping_db

        # Setup page controller
        self.page_controller = page_controller

        # Setup stay page
        self.stay_page = stay_page
        # Collect item image, name, price, note, status
        self.page_images = [self.stay_page.image_1, self.stay_page.image_2, self.stay_page.image_3, self.stay_page.image_4]
        self.page_names = [self.stay_page.name_1, self.stay_page.name_2, self.stay_page.name_3, self.stay_page.name_4]
        self.page_prices = [self.stay_page.price_1, self.stay_page.price_2, self.stay_page.price_3, self.stay_page.price_4]
        self.page_statuss = [self.stay_page.status_1, self.stay_page.status_2, self.stay_page.status_3, self.stay_page.status_4]
        self.page_remove_btns = [self.stay_page.remove_btn_1, self.stay_page.remove_btn_2, self.stay_page.remove_btn_3, self.stay_page.remove_btn_4]
        # Setup button
        self.stay_page.home_btn.clicked.connect(partial(self.page_controller.change_page, from_page="stay", to_page="home"))
        self.stay_page.mystore_btn.clicked.connect(partial(self.page_controller.change_page, from_page="stay", to_page="mystore"))
        self.stay_page.prepage_btn.clicked.connect(self.pre_page)
        self.stay_page.nextpage_btn.clicked.connect(self.next_page)
        self.stay_page.history_btn.clicked.connect(self.show_history)

    def show_history(self):
        history_class = self.page_controller.get_page_class("history")
        history_class.load_history(identity="buyer")
        self.page_controller.show_page("history")

    def reset_buy_items(self):
        # Setup buy items
        self.start_idx = 0
        self.current_user_ID = self.page_controller.get_current_user_ID() # Get current user_ID
        self.item_IDs = self.shopping_db.SELECT("SELECT item_ID FROM pre_order WHERE buyer='%s' and buy_order!=-1 ORDER BY buy_order ASC, buy_time DESC" %(self.current_user_ID)) # SELECT buy information FROM 'pre_order' TABLE
        self.all_buy_items = dict()

        # SELECT item information FROM 'items' TABLE
        for item_ID in self.item_IDs:
            select_results = self.shopping_db.SELECT("SELECT items.image, items.item_name, items.price, pre_order.buy_order FROM items, pre_order WHERE items.item_ID='%s' and items.status=0 and pre_order.buy_order!=-1" %(item_ID))[0]
            image, item_name, price, buy_order = select_results
            self.all_buy_items[item_ID] = dict()
            self.all_buy_items[item_ID]["image"] = BytesIO(image)
            self.all_buy_items[item_ID]["name"] = item_name
            self.all_buy_items[item_ID]["price"] = str(price)
            self.all_buy_items[item_ID]["buy_order"] = str(buy_order)

        # Enabled next_page button if total number of items is bigger than 4
        print("Total number of items: {}".format(len(self.item_IDs)))
        if len(self.item_IDs) > 4:
            self.stay_page.nextpage_btn.setEnabled(True)

        # Show items
        self.show_items()

    def reset_show_items(self):
        for page_image, page_name, page_price, page_status, page_remove_btn in zip(self.page_images, self.page_names, self.page_prices, self.page_statuss, self.page_remove_btns):
            # Setup mystore page
            page_image.setText("商品圖片")
            page_name.setText("商品名稱")
            page_price.setText("商品售價")
            page_status.setText("商品狀態")
            page_remove_btn.setEnabled(False)

        # Show items
        self.show_items()

    def show_items(self):
        for idx, item_ID, page_image, page_name, page_price, page_status in zip(range(4), self.item_IDs[self.start_idx:self.start_idx+4], self.page_images, self.page_names, self.page_prices, self.page_statuss):
            # Load item information from all_uploaded_items
            image = self.all_buy_items[item_ID]["image"]
            name = self.all_buy_items[item_ID]["name"]
            price = self.all_buy_items[item_ID]["price"]
            buy_order = self.all_buy_items[item_ID]["buy_order"]
            
            # Setup mystore page
            page_image.setPixmap(QPixmap.fromImage(self.convert_binary_image_to_qimage(image)))
            page_name.setText(name)
            page_price.setText(price)
            page_status.setText("第 " + buy_order + " 順位")
            self.page_remove_btns[idx].setEnabled(True)

    def pre_page(self):
        if self.start_idx - 4 >= 0:
            self.start_idx -= 4
            self.stay_page.pages.setText(str(int((self.start_idx / 4) + 1)))
            self.reset_show_items()
            self.stay_page.nextpage_btn.setEnabled(True)
            self.stay_page.prepage_btn.setEnabled(False if self.start_idx - 4 < 0 else True)
        else:
            self.page_controller.show_warning_page("Warning", "已經到第一頁囉^^")
        print("Run pre_page, start index: {}".format(self.start_idx))
    
    def next_page(self):
        if self.start_idx + 4 < len(self.item_IDs):
            self.start_idx += 4
            self.stay_page.pages.setText(str(int((self.start_idx / 4) + 1)))
            self.reset_show_items()
            self.stay_page.prepage_btn.setEnabled(True)
            self.stay_page.nextpage_btn.setEnabled(False if self.start_idx + 4 >= len(self.item_IDs) else True)
        else:
            self.page_controller.show_warning_page("Warning", "已經到最後一頁囉^^")
        print("Run next_page, start index: {}".format(self.start_idx))

    def convert_binary_image_to_qimage(self, img):
        img = Image.open(img)
        # Resize image to fit label size
        img_w, img_h = img.size
        if img_w > img_h:
            img = img.resize((161, int(img_h * 161 / img_w)))
            img_w, img_h = img.size
            if img_h > 160:
                img = img.resize((int(img_w * 160 / img_h), 160))
        else:
            img = img.resize((int(img_w * 160 / img_h), 160))
            img_w, img_h = img.size
            if img_w > 161:
                img = img.resize((161, int(img_h * 161 / img_w)))
        q_image = ImageQt.ImageQt(img) # Convert PIL image to QImage
        
        return q_image
