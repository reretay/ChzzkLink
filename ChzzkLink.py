import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
import requests
import subprocess
import time
import os
import re
import signal
from livebackgroundthread import Live_BackgroundThread
from videobackgroundthread import Video_BackgroundThread

# UI 파일 연결
form_class = uic.loadUiType("ChzzkLinkUI.ui")[0]

# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # QPushButton에 대한 이벤트 핸들러 연결
        self.pushButton_start.clicked.connect(self.start_recording)
        self.pushButton_stop.clicked.connect(self.stop_recording)
        self.pushButton_end.clicked.connect(self.end_program)

        self.background_thread = None

    # 녹화 시작 함수
    def start_recording(self):
        channel_id = None
        video_num = None
        channel_url = self.lineEdit_channel_id.text().strip() # QLineEdit 에서 읽어오기
        if 'live' in channel_url:
            download_type = f'live'
            match = re.search(r'/live/(\w+)', channel_url) # URL에서 채널 ID 추출
            channel_id = match.group(1)
            print(channel_id)
        elif 'video' in channel_url:
            download_type = f'video'
            match = re.search(r'/video/(\w+)', channel_url) # URL에서 VOD NUM 추출
            video_num = match.group(1)
        else:
            print("It is not proper url")
        
        if channel_id and download_type=='live':
            if not self.background_thread or not self.background_thread.isRunning():
                # 백그라운드 스레드 생성 및 실행
                self.background_thread = Live_BackgroundThread(channel_id)
                self.background_thread.finished.connect(self.background_thread_finished)
                self.background_thread.status_updated.connect(self.update_status)  # QTextBrowser 텍스트 업데이트 연결
                self.background_thread.start()
            else:
                print("Recording is already in progress.")
        elif video_num and download_type=='video':
            if not self.background_thread or not self.background_thread.isRunning():
                # 백그라운드 스레드 생성 및 실행
                self.background_thread = Video_BackgroundThread(video_num)
                self.background_thread.finished.connect(self.background_thread_finished)
                self.background_thread.status_updated.connect(self.update_status)  # QTextBrowser 텍스트 업데이트 연결
                self.background_thread.start()
            else:
                print("Downloading is already in progress.")

        else:
            print("Please enter a URL.")

    # 녹화 종료 함수
    def stop_recording(self):
        if self.background_thread and self.background_thread.isRunning():
            self.background_thread.stop_recording()
            self.background_thread.stop()
        else:
            print("No recording in progress.")

    #프로그램 종료 함수
    def end_program(self):
        self.background_thread.stop_recording()
        self.background_thread.stop()
        QApplication.quit()

    # 백그라운드 쓰레드 업데이트 메서드
    def update_status(self, status):
        if status.startswith("http"): # 썸네일을 받아오는 조건문
            status = status.replace('{type}', '480')
            response = requests.get(status)
            with open('temp.png', 'wb') as f:
                    f.write(response.content)
            pixmap = QPixmap('temp.png')
            self.label_4.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))  # 이미지 크기 조정
            self.label_4.setAlignment(Qt.AlignCenter)  # 이미지 중앙 정렬
            self.label_4.setScaledContents(True)  # 이미지 크기를 라벨 크기에 맞게 조정
            self.label_4.show()
            self.label_4.update()
        else:
            self.textBrowser.append(status)  # textBrowser에 정보 추가

    # 백그라운드 스레드가 작업을 완료했을 때 호출되는 함수
    def background_thread_finished(self):
        print("Background thread finished")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())
