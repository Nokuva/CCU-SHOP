from PyQt5.QtGui import QPixmap, QImage
from io import BytesIO
from PIL import Image, ImageQt

class HISTORY():
    def __init__(self, shopping_db=None, page_controller=None, history_page=None):
        # Setup shopping database
        self.shopping_db = shopping_db

        # Setup page controller
        self.page_controller = page_controller

        # Setup item_info page
        self.history_page = history_page
        # Collect item image, name, price, note, status
        self.page_images = [self.history_page.image_1, self.history_page.image_2, self.history_page.image_3]
        self.page_names = [self.history_page.name_1, self.history_page.name_2, self.history_page.name_3]
        self.page_prices = [self.history_page.price_1, self.history_page.price_2, self.history_page.price_3]
        self.page_times = [self.history_page.time_1, self.history_page.time_2, self.history_page.time_3]
        self.page_partners = [self.history_page.partner_1, self.history_page.partner_2, self.history_page.partner_3]
        # Setup button
        self.history_page.prepage_btn.clicked.connect(self.pre_page)
        self.history_page.nextpage_btn.clicked.connect(self.next_page)

    def load_history(self, identity=None):
        current_user_ID = self.page_controller.get_current_user_ID()
        self.start_idx = 0
        self.item_IDs = []
        self.history = dict()
        if identity == "buyer":
            pre_order_results = self.shopping_db.SELECT("SELECT item_ID, buy_time FROM pre_order WHERE buyer='%s' and buy_order=-1" %(current_user_ID))
            for item_ID, buy_time in pre_order_results:
                items_results = self.shopping_db.SELECT("SELECT image, item_name, price, owner FROM items WHERE item_ID='%s'" %(item_ID))[0]
                image, item_name, price, owner = items_results
                self.item_IDs.append(item_ID)
                self.history[item_ID] = dict()
                self.history[item_ID]["image"] = BytesIO(image)
                self.history[item_ID]["name"] = item_name
                self.history[item_ID]["price"] = str(price)
                self.history[item_ID]["time"] = str(buy_time)
                self.history[item_ID]["partner"] = owner
        elif identity == "owner":
            items_results = self.shopping_db.SELECT("SELECT item_ID, image, item_name, price, uploadtime FROM items WHERE owner='%s' and status=2" %(current_user_ID))
            for item_ID, image, item_name, price, uploadtime in items_results:
                buyer = self.shopping_db.SELECT("SELECT buyer FROM pre_order WHERE item_ID='%s'" %(item_ID))[0][0]
                self.item_IDs.append(item_ID + "_" + buyer)
                self.history[item_ID + "_" + buyer] = dict()
                self.history[item_ID + "_" + buyer]["image"] = BytesIO(image)
                self.history[item_ID + "_" + buyer]["name"] = item_name
                self.history[item_ID + "_" + buyer]["price"] = str(price)
                self.history[item_ID + "_" + buyer]["time"] = str(uploadtime)
                self.history[item_ID + "_" + buyer]["partner"] = buyer
                
        # Enabled next_page button if total number of items is bigger than 6
        print("Total number of items: {}".format(len(self.item_IDs)))
        if len(self.item_IDs) > 3:
            self.history_page.nextpage_btn.setEnabled(True)

        # Show history
        self.show_history()

    def reset_show_history(self):
        for page_image, page_name, page_price, page_time, page_partner in zip(self.page_images, self.page_names, self.page_prices, self.page_times, self.page_partners):
            # Setup mystore page
            page_image.setText("商品圖片")
            page_name.setText("商品名稱")
            page_price.setText("商品售價")
            page_time.setText("交易時間")
            page_partner.setText("交易對象")

        # Show items
        self.show_history()

    def show_history(self):
        for idx, item_ID, page_image, page_name, page_price, page_time, page_partner in zip(range(3), self.item_IDs[self.start_idx:self.start_idx+3], self.page_images, self.page_names, self.page_prices, self.page_times, self.page_partners):
            # Load item information from all_uploaded_items
            image = self.history[item_ID]["image"]
            name = self.history[item_ID]["name"]
            price = self.history[item_ID]["price"]
            time = self.history[item_ID]["time"]
            partner = self.history[item_ID]["partner"]
            
            # Setup mystore page
            page_image.setPixmap(QPixmap.fromImage(self.convert_binary_image_to_qimage(image)))
            page_name.setText(name)
            page_price.setText(price)
            page_time.setText(time)
            page_partner.setText(partner)

    def pre_page(self):
        if self.start_idx - 3 >= 0:
            self.start_idx -= 3
            self.history_page.pages.setText(str(int((self.start_idx / 3) + 1)))
            self.reset_show_history()
            self.history_page.nextpage_btn.setEnabled(True)
            self.history_page.prepage_btn.setEnabled(False if self.start_idx - 3 < 0 else True)
        else:
            self.page_controller.show_warning_page("Warning", "已經到第一頁囉^^")
        print("Run pre_page, start index: {}".format(self.start_idx))
    
    def next_page(self):
        if self.start_idx + 3 < len(self.item_IDs):
            self.start_idx += 3
            self.history_page.pages.setText(str(int((self.start_idx / 3) + 1)))
            self.reset_show_history()
            self.history_page.prepage_btn.setEnabled(True)
            self.history_page.nextpage_btn.setEnabled(False if self.start_idx + 3 >= len(self.item_IDs) else True)
        else:
            self.page_controller.show_warning_page("Warning", "已經到最後一頁囉^^")
        print("Run next_page, start index: {}".format(self.start_idx))

    def convert_binary_image_to_qimage(self, img):
        img = Image.open(img)
        # Resize image to fit label size
        img_w, img_h = img.size
        if img_w > img_h:
            img = img.resize((159, int(img_h * 159 / img_w)))
            img_w, img_h = img.size
            if img_h > 166:
                img = img.resize((int(img_w * 166 / img_h), 166))
        else:
            img = img.resize((int(img_w * 166 / img_h), 166))
            img_w, img_h = img.size
            if img_w > 159:
                img = img.resize((159, int(img_h * 159 / img_w)))
        q_image = ImageQt.ImageQt(img) # Convert PIL image to QImage
        
        return q_image