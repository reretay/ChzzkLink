# ChzzkLink - Chzzk VOD/LIVE Downloader

streamlink-6.6.2-1-py312-x86_64 <br>
With  NaverChzzk.py plugin <br>
https://github.com/reretay/Chzzk_Tool_Auto_Record

# Beta Release
![image](https://github.com/reretay/ChzzkLink/assets/31172353/c8d07210-cea1-406d-b2d5-a11d0884630c)
부족한점이 많아 좀 더 완성도를 올려서 공개하려고 했지만 요즘 너무 바빠서 도저히 손댈 시간이 나질 않네요.
URL란에 라이브 혹은 VOD 링크를 넣어주시면 됩니다.

VOD같은 경우에는 바로 다운로드가 시작되고 라이브 같은 경우에는 10초마다 방송 여부를 확인하여 방송중이라면 다운로드가 시작됩니다. (당연히 방종되면 다운로드도 종료되고, 다음에 다시 방온되면 다시 다운로드가 시작됩니다.)
따라서 크롬 플러그인과 다르게 매번 수동으로 녹화를 시작하지 않아도 됩니다.

또한 중복 실행이 가능합니다. 그래서 여러개를 동시에 돌리셔도 됩니다. (그냥 exe로 여러개 띄우시면 됩니다.)

영상 이름은 닉네임, 방송시작시간, 방송제목 순으로 정의되며 중복된 이름이 있을 경우 파일명 뒤에 숫자를 붙입니다.
또한 영상은 recordings 폴더 밑에 저장됩니다.

성인제한 방송은 NID_SES와 AUT 정보를 입력해야 합니다. << 웹 브라우저로 치지직에 로그인 된 상태에서 F12를 누르거나 빈곳을 우클릭하여 개발자창을 엽니다. 그리고 application(응용 프로그램) - 왼쪽 탭에서 저장소 아래 쿠키 확장 - chzzk.naver.com 선택 하셔서 보시면 NID_AUT 와 NID_SES가 있습니다. 각각 클릭하시면 밑에 Cookie Value에 전체 값이 뜹니다. 이걸 붙여넣기 해주시면 성인 제한 방송도 다운로드가 가능합니다.

[https://github.com/reretay/ChzzkLink/releases/tag/Alpha](https://github.com/reretay/ChzzkLink/releases/tag/Beta)

# To Do List
<del>다시보기 다운로드 기능 추가</del> <br> 
영상 길이 문제 수정 <br>
<del>StreamLink 플러그인 교체</del> <br>
<del>연령제한 방송 다운로드 목적 NID_AUT, NID_SES 입력란 추가</del> <br>
status 확인 - 종료 함수 //녹화중지 - already recording<br>
동시성 문제 확인<br>
썸네일 이미지 갱신<br>
경고들 Qmessege로 변경<br>
화질선택 / 포맷선택 / 파일경로이동 / 패키징-ico / chzzklink.com Qlabel 클릭<br>
프로그램 종료 버튼 확인 (지연발생문제)<br>
