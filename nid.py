from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5 import uic
import sys

NIDWindow = uic.loadUiType("NID.ui")[0]

class NIDWindowClass(QWidget, NIDWindow):
    # 시그널 정의
    data_saved = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        

        # QPushButton에 대한 이벤트 핸들러 연결
        self.pushButton_save.clicked.connect(self.nid_save)
        self.pushButton_cancel.clicked.connect(self.nid_cancel)
    
    def nid_save(self):
        if self.lineEdit_NID_SES.text().strip() and self.lineEdit_NID_AUT.text().strip():
            NID_SES = self.lineEdit_NID_SES.text().strip()
            NID_AUT = self.lineEdit_NID_AUT.text().strip()
            OAUTH = "true"
            # 시그널 발생
            self.data_saved.emit(OAUTH, NID_SES, NID_AUT)
            QMessageBox.about(self,'Alert','Saved!')
        else:
            NID_SES = 'null'
            NID_AUT = 'null'
            self.OAUTH = "false"
            QMessageBox.about(self,'Alert','Enter SES and AUT both.\nNID has been reseted.')
            
    def nid_cancel(self):
        self.close()