# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 16:03:09 2020

@author: User
"""

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image, ImageQt
from datetime import datetime

class ADDITEM():
    def __init__(self, shopping_db=None, page_controller=None, additem_page=None):
        # Setup shopping database
        self.shopping_db = shopping_db

        # Setup page controller
        self.page_controller = page_controller
        
        # Setup additem page
        self.additem_page = additem_page
        self.additem_page.name_edit.setFocus()
        self.additem_page.price_edit.setPlaceholderText("EX: 100")
        self.additem_page.note_edit.setPlaceholderText("EX: 二手/新品/面交時地/不議價...")
        self.additem_page.addimage_btn.clicked.connect(self.add_image)
        self.additem_page.save_btn.clicked.connect(self.save)
        
    def reset_page(self):
        # Clear lineEdit
        self.additem_page.image.setText("請新增圖片")
        self.additem_page.name_edit.setText("")
        self.additem_page.price_edit.setText("")
        self.additem_page.note_edit.setText("")

        # Reset lineEdit
        self.additem_page.name_edit.setFocus()
        self.additem_page.price_edit.setPlaceholderText("EX: 100")
        self.additem_page.note_edit.setPlaceholderText("EX: 二手/新品/面交時地/不議價...")


    def add_image(self):
        # Get image path
        self.image_path, _ = QFileDialog.getOpenFileName(None, "Open image file", r"C:\\Users\\User\\", "Image files (*.jpg *.jpeg *.png)")
        print("Image path: {}".format(self.image_path))
        
        # Load image
        if self.image_path != "":
            img = Image.open(self.image_path)
            # Resize image to fit label size
            img_w, img_h = img.size
            if img_w > img_h:
                img = img.resize((284, int(img_h * 284 / img_w)))
                img_w, img_h = img.size
                if img_h > 241:
                    img = img.resize((int(img_w * 241 / img_h), 241))
            else:
                img = img.resize((int(img_w * 241 / img_h), 241))
                img_w, img_h = img.size
                if img_w > 284:
                    img = img.resize((284, int(img_h * 284 / img_w)))
            q_image = ImageQt.ImageQt(img) # Convert PIL image to QImage
            self.additem_page.image.setPixmap(QPixmap.fromImage(q_image)) # Show QImage
    
    def save(self):
        # SELECT MAX(item_ID) FROM 'items' TABLE
        max_item_ID = self.shopping_db.SELECT("SELECT MAX(item_ID) FROM items")[0][0]
        max_item_ID = "I000" if max_item_ID is None else max_item_ID
        
        # INSERT items to TABLE
        item_ID = "I%03d" %(int(max_item_ID[1:])+1)
        binary_image = self.read_image_binary_data(self.image_path)
        item_name = self.additem_page.name_edit.text()
        price = self.additem_page.price_edit.text()
        owner = self.page_controller.get_current_user_ID()
        print("Owner: {}".format(owner))
        note = self.additem_page.note_edit.toPlainText()
        uploadtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = 1
        sql = "INSERT INTO items (item_ID, image, item_name, price, owner, note, uploadtime, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        condition = (item_ID, binary_image, item_name, price, owner, note, uploadtime, status)
        self.shopping_db.TABLE_modify(sql, condition)
        
        # Close additem page
        self.page_controller.close_page("additem")
        
    def read_image_binary_data(self, image_path):
        with open(image_path, "rb") as file:
            binary_data = file.read()
        return binary_data
        