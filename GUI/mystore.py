# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 16:42:28 2020

@author: User
"""

from PyQt5.QtGui import QPixmap, QImage
from functools import partial
from io import BytesIO
from PIL import Image, ImageQt

class MYSTORE():
    def __init__(self, shopping_db=None, page_controller=None, mystore_page=None):
        # Setup shopping database
        self.shopping_db = shopping_db

        # Setup page controller
        self.page_controller = page_controller
        
        # Setup mystore page 
        self.mystore_page = mystore_page
        # Collect item image, name, price, note, status
        self.page_images = [self.mystore_page.image_1, self.mystore_page.image_2, self.mystore_page.image_3]
        self.page_names = [self.mystore_page.name_1, self.mystore_page.name_2, self.mystore_page.name_3]
        self.page_prices = [self.mystore_page.price_1, self.mystore_page.price_2, self.mystore_page.price_3]
        self.page_notes = [self.mystore_page.note_1, self.mystore_page.note_2, self.mystore_page.note_3]
        self.page_statuss = [self.mystore_page.status_1, self.mystore_page.status_2, self.mystore_page.status_3]
        self.page_finish_btns = [self.mystore_page.finish_btn_1, self.mystore_page.finish_btn_2, self.mystore_page.finish_btn_3]
        # Setup button
        self.mystore_page.home_btn.clicked.connect(partial(self.page_controller.change_page, from_page="mystore", to_page="home"))
        self.mystore_page.mystore_btn.clicked.connect(partial(self.page_controller.change_page, from_page="mystore", to_page="mystore"))
        self.mystore_page.stay_btn.clicked.connect(partial(self.page_controller.change_page, from_page="mystore", to_page="stay"))
        for idx, finish_btn in enumerate(self.page_finish_btns):
            finish_btn.clicked.connect(partial(self.finish_trade, idx=idx))
        self.mystore_page.prepage_btn.clicked.connect(self.pre_page)
        self.mystore_page.nextpage_btn.clicked.connect(self.next_page)
        self.mystore_page.additem_btn.clicked.connect(partial(self.page_controller.show_page, page_name="additem"))
        self.mystore_page.history_btn.clicked.connect(self.show_history)
        
        # Predefine status table
        self.status_table = {0: "有人排", 1: "有貨", 2: "已售空"}
        
    def show_history(self):
        history_class = self.page_controller.get_page_class("history")
        history_class.load_history(identity="owner")
        self.page_controller.show_page("history")

    def reset_mystore_items(self):
        # Setup uploaded items
        self.start_idx = 0
        self.item_IDs = []
        self.all_uploaded_items = dict()
        
        # Load items from DATABASE
        print("This is mystore class, current user is {}".format(self.page_controller.get_current_user_ID()))
        select_results = self.shopping_db.SELECT("SELECT item_ID, image, item_name, price, note, status FROM items WHERE owner='%s' ORDER BY status ASC, uploadtime DESC" %(self.page_controller.get_current_user_ID()))
        for item_ID, image, item_name, price, note, status in select_results:
            # Save SELECT results
            self.item_IDs.append(item_ID)
            self.all_uploaded_items[item_ID] = dict()
            self.all_uploaded_items[item_ID]["image"] = BytesIO(image)
            self.all_uploaded_items[item_ID]["name"] = item_name
            self.all_uploaded_items[item_ID]["price"] = price
            self.all_uploaded_items[item_ID]["note"] = note
            self.all_uploaded_items[item_ID]["status"] = status

        # Enabled next_page button if total number of items is bigger than 3
        print("Total number of items: {}".format(len(self.item_IDs)))
        if len(self.item_IDs) > 3:
            self.mystore_page.nextpage_btn.setEnabled(True)

        # Show items
        self.show_items()
            
    def reset_show_items(self):
        for page_image, page_name, page_price, page_note, page_status, page_finish_btn in zip(self.page_images, self.page_names, self.page_prices, self.page_notes, self.page_statuss, self.page_finish_btns):
            # Setup mystore page
            page_image.setText("商品圖片:")
            page_name.setText("商品名稱:")
            page_price.setText("商品售價:")
            page_note.setText("商品備註:")
            page_status.setText("商品狀態:")
            page_finish_btn.setEnabled(False)

        # Show items
        self.show_items()
        
    def show_items(self):
        for idx, item_ID, page_image, page_name, page_price, page_note, page_status in zip(range(3), self.item_IDs[self.start_idx:self.start_idx+3], self.page_images, self.page_names, self.page_prices, self.page_notes, self.page_statuss):
            # Load item information from all_uploaded_items
            image = self.all_uploaded_items[item_ID]["image"]
            name = self.all_uploaded_items[item_ID]["name"]
            price = self.all_uploaded_items[item_ID]["price"]
            note = self.all_uploaded_items[item_ID]["note"]
            status = self.all_uploaded_items[item_ID]["status"]
            
            # Setup mystore page
            page_image.setPixmap(QPixmap.fromImage(self.convert_binary_image_to_qimage(image)))
            page_name.setText("商品名稱: " + name)
            page_price.setText("商品售價: " + str(price))
            page_note.setText("商品備註: " + note)
            page_status.setText("商品狀態: " + self.status_table[status])
            if status == 2:
                self.page_finish_btns[idx].setEnabled(False)
            else:
                self.page_finish_btns[idx].setEnabled(True)

    def pre_page(self):
        if self.start_idx - 3 >= 0:
            self.start_idx -= 3
            self.mystore_page.pages.setText(str(int((self.start_idx / 3) + 1)))
            self.reset_show_items()
            self.mystore_page.nextpage_btn.setEnabled(True)
            self.mystore_page.prepage_btn.setEnabled(False if self.start_idx - 3 < 0 else True)
        else:
            self.page_controller.show_warning_page("Warning", "已經到第一頁囉^^")
        print("Run pre_page, start index: {}".format(self.start_idx))
    
    def next_page(self):
        if self.start_idx + 3 < len(self.item_IDs):
            self.start_idx += 3
            self.mystore_page.pages.setText(str(int((self.start_idx / 3) + 1)))
            self.reset_show_items()
            self.mystore_page.prepage_btn.setEnabled(True)
            self.mystore_page.nextpage_btn.setEnabled(False if self.start_idx + 3 >= len(self.item_IDs) else True)
        else:
            self.page_controller.show_warning_page("Warning", "已經到最後一頁囉^^")
        print("Run next_page, start index: {}".format(self.start_idx))

    def finish_trade(self, idx=-1):
        print("Finish trade: {}".format(idx))
        # Update 'items' TABLE
        self.current_item_IDs = self.item_IDs[self.start_idx:self.start_idx+3][idx]
        sql = "UPDATE items SET status=%s WHERE item_ID=%s"
        condition = (2, self.current_item_IDs)
        self.shopping_db.TABLE_modify(sql, condition)

        # Update 'pre_order' TABLE
        sql = "UPDATE pre_order SET buy_order=%s WHERE item_ID=%s and buyer=%s"
        condition = (-1, self.current_item_IDs, self.page_controller.get_current_user_ID())
        self.shopping_db.TABLE_modify(sql, condition)

        # DELETE 'pre_order' TABLE
        sql = "DELETE FROM pre_order WHERE item_ID=%s and buy_order!=%s"
        condition = (self.current_item_IDs, -1)
        self.shopping_db.TABLE_modify(sql, condition)

        # Reset mystore items
        self.reset_mystore_items()

    def convert_binary_image_to_qimage(self, img):
        img = Image.open(img)
        img_w, img_h = img.size
        img = img.resize((251, int(img_h * 251 / img_w))) if img_w > img_h else img.resize((int(img_w * 241 / img_h), 241)) # Resize image to fit label size
        q_image = ImageQt.ImageQt(img) # Convert PIL image to QImage
        
        return q_image