import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
import requests
import subprocess
import time
import os
import re

# UI 파일 연결
form_class = uic.loadUiType("untitled.ui")[0]

# 백그라운드에서 주기적으로 작업을 처리하는 클래스
class BackgroundThread(QThread):
    # 작업 완료 시그널
    finished = pyqtSignal()

    def __init__(self, channel_id):
        super().__init__()
        self.channel_id = channel_id
        self.recording_process = None

    def run(self):
        naver_api_url = f'https://api.chzzk.naver.com/service/v2/channels/{self.channel_id}/live-detail'
        while True:
            naver_status = self.check_naver_status(naver_api_url)
            if naver_status == 'OPEN':
                if not self.recording_process:
                    self.start_recording(naver_api_url)
            else:
                if self.recording_process:
                    self.stop_recording()
            time.sleep(10)  # 10초마다 상태 확인 (조절 가능)

    # Naver API에서 상태 확인 함수
    def check_naver_status(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('content', {}).get('status')
        else:
            print(f'Error Status code: {response.status_code}\nResponse: {response.text}')
            return None

    # 녹화 시작 함수
    def start_recording(self, api_url):
        response = requests.get(api_url)
        if response.status_code == 200:
            content = response.json().get('content', {})
            title = content.get('liveTitle', 'untitled')
            channel_name = content.get('channel', {}).get('channelName', 'unknown_channel')
            open_date = content.get('openDate', 'unknown_date')
            # 파일 이름 설정
            file_name = self.generate_file_name(channel_name, open_date, title)
            file_name = self.check_and_rename_file(file_name)
            file_path = f"recordings/{file_name}"
            record_command = f'streamlink --loglevel none https://chzzk.naver.com/live/{self.channel_id} best --output "{file_path}"'
            self.recording_process = subprocess.Popen(record_command, shell=True)
            print("Start recording:", file_path)
        else:
            print(f"Failed to get API data: {response.status_code}")

    # 파일 이름 생성 함수
    def generate_file_name(self, channel_name, open_date, title):
        channel_name = self.remove_special_characters(channel_name)
        open_date = self.remove_special_characters(open_date)
        title = self.remove_special_characters(title)
        return f"{channel_name}_{open_date}_{title}.ts"

    # 특수문자 제거 함수
    def remove_special_characters(self, text):
        return re.sub(r'[^\w\s]', '', text)

    # 파일 이름 중복 확인 및 변경 함수
    def check_and_rename_file(self, file_name):
        file_path_chk = f"recordings/{file_name}"
        base, ext = os.path.splitext(file_name)
        index = 1
        while os.path.exists(file_path_chk):
            new_file_name = f"{base}_{index}{ext}"
            file_path_chk = f"recordings/{new_file_name}"
            index += 1
        return new_file_name

    # 녹화 종료 함수
    def stop_recording(self):
        if self.recording_process:
            self.recording_process.terminate()
            self.recording_process = None
            print("Stop recording")

# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # QPushButton에 대한 이벤트 핸들러 연결
        self.pushButton_start.clicked.connect(self.start_recording)
        self.pushButton_stop.clicked.connect(self.stop_recording)

    # 녹화 시작 함수
    def start_recording(self):
        channel_id = self.lineEdit_channel_id.text().strip()
        if channel_id:
            # 백그라운드 스레드 생성 및 실행
            self.background_thread = BackgroundThread(channel_id)
            self.background_thread.finished.connect(self.background_thread_finished)
            self.background_thread.start()
        else:
            print("Please enter a channel ID.")

    # 녹화 종료 함수
    def stop_recording(self):
        if hasattr(self, 'background_thread') and self.background_thread:
            self.background_thread.stop_recording()
        QApplication.quit()

    # 백그라운드 스레드가 작업을 완료했을 때 호출되는 함수
    def background_thread_finished(self):
        print("Background thread finished")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())
