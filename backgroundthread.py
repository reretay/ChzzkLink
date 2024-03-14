import sys
import requests
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess
import time
import os
import re
import signal

# 백그라운드에서 주기적으로 작업을 처리하는 클래스
class BackgroundThread(QThread):
    # 작업 완료 시그널
    finished = pyqtSignal()
    # 상태 업데이트 시그널
    status_updated = pyqtSignal(str)

    # API 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    useragent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

    def __init__(self, channel_id):
        super().__init__()
        self.channel_id = channel_id
        self.recording_process = None
        self.is_recording_started = False  # 녹화 시작 여부를 나타내는 플래그
        self.is_interrupted = False  # 스레드 중단 요청을 나타내는 플래그

    def run(self):
        naver_api_url = f'https://api.chzzk.naver.com/service/v2/channels/{self.channel_id}/live-detail'
        while not self.is_interrupted:  # 스레드가 중단 요청을 받을 때까지 루프 실행
            naver_status = self.check_naver_status(naver_api_url)
            if naver_status == 'OPEN':
                if not self.recording_process and not self.is_recording_started:
                    self.start_recording(naver_api_url)
                print("Status:OPEN")
                self.status_updated.emit("녹화중...")  # 상태 업데이트 시그널 발생
            else:
                if self.recording_process:
                    self.stop_recording()
                print("Status:CLOSED, Retry in 10 seconds")
            time.sleep(10)  # 10초마다 상태 확인

    # 스레드를 중단시키는 메서드
    def stop(self):
        self.is_interrupted = True

    # Naver API에서 상태 확인 함수
    def check_naver_status(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('content', {}).get('status')
        else:
            print(f'Error Status code: {response.status_code}\nResponse: {response.text}')
            return None

    # 녹화 시작 함수
    def start_recording(self, api_url):
        response = requests.get(api_url, headers=self.headers)
        if response.status_code == 200:
            content = response.json().get('content', {})
            title = content.get('liveTitle', 'untitled')
            channel_name = content.get('channel', {}).get('channelName', 'unknown_channel')
            open_date = content.get('openDate', 'unknown_date')
            # 파일 이름 설정
            file_name = self.generate_file_name(channel_name, open_date, title)
            file_name = self.check_and_rename_file(file_name)
            file_path = f"recordings/{file_name}"
            record_command = f'streamlink-6.6.2-1-py312-x86_64/bin/streamlink --loglevel none --plugin-dirs streamlink-6.6.2-1-py312-x86_64 --http-header "User-Agent={self.useragent}" https://chzzk.naver.com/live/{self.channel_id} best --output "{file_path}"'
            # 녹화 시작 전에 필요한 정보를 메인 창으로 전달
            self.status_updated.emit(f"채널 ID: {self.channel_id}\n")
            self.status_updated.emit(f"채널명: {channel_name}\n")
            self.status_updated.emit(f"방송 제목: {title}\n")
            self.status_updated.emit(f"방송 시작 시간: {open_date}\n")
            # streamlink 명령 실행
            self.recording_process = subprocess.Popen(record_command)
            if self.recording_process.poll() is None:
                # 명령이 성공적으로 실행된 경우
                print("Start recording:", file_path)
            else:
                # 명령 실행이 실패한 경우 사용자에게 경고 메시지 표시
                QMessageBox.warning(None, "Recording Error", "Failed to start recording.")
                print("Failed to start recording.")

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
        new_file_name = file_name
        while os.path.exists(file_path_chk):
            new_file_name = f"{base}_{index}{ext}"
            file_path_chk = f"recordings/{new_file_name}"
            index += 1
        return new_file_name

    # 녹화 종료 함수
    def stop_recording(self):
        if self.recording_process:
            self.recording_process.terminate()
            #self.recording_process.wait()  # 녹화가 완전히 종료될 때까지 대기
            self.recording_process = None
            self.status_updated.emit("녹화중이 아닙니다.")  # 상태 업데이트 시그널 발생
            print("\nStop recording")

