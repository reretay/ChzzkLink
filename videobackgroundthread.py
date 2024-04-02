import sys
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
import subprocess
import time
import os
import re
import signal

# 백그라운드에서 주기적으로 작업을 처리하는 클래스
class Video_BackgroundThread(QThread):
    # 작업 완료 시그널
    finished = pyqtSignal()
    # 상태 업데이트 시그널
    status_updated = pyqtSignal(str)

    # API 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    useragent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

    def __init__(self, video_num, OAUTH, NID_SES, NID_AUT):
        super().__init__()
        self.video_num = video_num
        self.OAUTH = OAUTH # NID 값 가져오기
        self.NID_SES = NID_SES
        self.NID_AUT = NID_AUT
        self.recording_process = None
        self.is_recording_started = False  # 녹화 시작 여부를 나타내는 플래그
        self.is_interrupted = False  # 스레드 중단 요청을 나타내는 플래그

    def run(self):
        naver_api_url = f'https://api.chzzk.naver.com/service/v2/videos/{self.video_num}'
        while not self.is_interrupted:  # 스레드가 중단 요청을 받을 때까지 루프 실행
            naver_status = self.check_naver_status(naver_api_url)
            if naver_status == 'OPEN':
                if not self.recording_process and not self.is_recording_started:
                    self.start_recording(naver_api_url)
                    if self.recording_process:
                        print("Status:OPEN")
                        self.status_updated.emit("녹화 시작")  # 상태 업데이트 시그널 발생
                    else:
                        print("OPENED BUT SOMETHING WAS WRONG. Fail to start recording")
                        self.stop_recording()
                        self.stop()
            else:
                if self.recording_process:
                    self.stop_recording()
                print("Error, Retry in 10 seconds. Please Check your URL")
            time.sleep(10)  # 10초마다 상태 확인

    # 스레드를 중단시키는 메서드
    def stop(self):
        self.is_interrupted = True

    # Naver API에서 상태 확인 함수
    def check_naver_status(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200: # API 200 응답만 확인
            return 'OPEN'
        else:
            print(f'Error Status code: {response.status_code}\nResponse: {response.text}')
            return None

    # 녹화 시작 함수
    def start_recording(self, api_url):
        continuedownload=0
        if self.OAUTH == 'true': #OAUTH 사용 여부에 따른 request 헤더 설정 및 유저 상태와 방송상태 확인
            self.oauth_headers = self.headers
            self.oauth_headers['Cookie'] = f"NID_AUT={self.NID_AUT}; NID_SES={self.NID_SES};"
            response = requests.get(api_url, headers=self.oauth_headers)
            content = response.json().get('content', {})
            if content.get('adult') == True and content.get('userAdultStatus') == 'ADULT':
                continuedownload=1
            elif content.get('adult') == False:
                continuedownload=1
            else:
                self.status_updated.emit("NID_Error")
                continuedownload=0
        else:
            response = requests.get(api_url, headers=self.headers)
            content = response.json().get('content', {})
            if content.get('adult') == True and content.get('userAdultStatus') == 'ADULT':
                continuedownload=1
            elif content.get('adult') == False:
                continuedownload=1
            else:
                self.status_updated.emit("NID_Error")
                continuedownload=0
        
        if response.status_code == 200 and continuedownload == 1:
            title = content.get('videoTitle', 'untitled')
            channel_name = content.get('channel', {}).get('channelName', 'unknown_channel')
            publish_date = content.get('publishDate', 'unknown_date')
            image_url = content.get('thumbnailImageUrl') # 썸네일 이미지 URL을 시그널로 전달
            self.status_updated.emit(image_url)
            # 파일 이름 설정
            file_name = self.generate_file_name(channel_name, publish_date, title)
            file_name = self.check_and_rename_file(file_name)
            file_path = f"recordings/{file_name}"
            if self.OAUTH == "false":
                record_command = (f'streamlink-6.6.2-1-py312-x86_64/bin/streamlink --loglevel none --ffmpeg-copyts --plugin-dirs streamlink-6.6.2-1-py312-x86_64 --http-header "User-Agent={self.useragent}" https://chzzk.naver.com/video/{self.video_num} best --output "{file_path}"')
            else:
                record_command = (f'streamlink-6.6.2-1-py312-x86_64/bin/streamlink --loglevel none --ffmpeg-copyts --plugin-dirs streamlink-6.6.2-1-py312-x86_64 --http-header "User-Agent={self.useragent}" https://chzzk.naver.com/video/{self.video_num} best --ChzzkPlugin-cookie "NID_AUT={self.NID_AUT}; NID_SES={self.NID_SES};" --output "{file_path}"')
            # 녹화 시작 전에 필요한 정보를 메인 창으로 전달
            self.status_updated.emit(f"NID 사용 여부: {self.OAUTH}\n")
            self.status_updated.emit(f"영상 번호: {self.video_num}\n")
            self.status_updated.emit(f"채널명: {channel_name}\n")
            self.status_updated.emit(f"영상 제목: {title}\n")
            self.status_updated.emit(f"영상 업로드 날짜: {publish_date}\n")
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
    def generate_file_name(self, channel_name, publish_date, title):
        channel_name = self.remove_special_characters(channel_name)
        publish_date = self.remove_special_characters(publish_date)
        title = self.remove_special_characters(title)
        return f"{channel_name}_{publish_date}_{title}.ts"

    # 특수문자 제거 및 이스케이프 시퀀스 제거 함수
    def remove_special_characters(self, text):
        return re.sub(r'[^\w\s]', '', text).replace('\n', '')

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
            self.status_updated.emit("다운로드중이 아닙니다.")  # 상태 업데이트 시그널 발생
            print("\nStop downloading")

