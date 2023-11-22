import os
import sys
import time
import mss
import mss.tools
import pyautogui
import natsort
import shutil

from pynput import mouse
from pynput.keyboard import Key, Controller
from PIL import Image

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMainWindow, QVBoxLayout, \
    QHBoxLayout, QSlider


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.num = 1
        self.posX1 = 0
        self.posY1 = 0
        self.posX2 = 0
        self.posY2 = 0
        self.total_page = 1
        self.speed = 0.1
        self.region = {}
        self.file_list = []

        # 앱 타이틀
        self.setWindowTitle("eBookToPdf")

        # 버튼 생성
        self.button1 = QPushButton("좌표 위치 클릭")
        self.button2 = QPushButton("좌표 위치 클릭")
        self.button3 = QPushButton("PDF로 만들기")
        self.button3.setFixedSize(QSize(430, 60))
        self.button4 = QPushButton("초기화")

        # 버튼 클릭 이벤트
        self.button1.clicked.connect(self.좌측상단_좌표_클릭)
        self.button2.clicked.connect(self.우측하단_좌표_클릭)
        self.button3.clicked.connect(self.btn_click)
        self.button4.clicked.connect(self.초기화)

        # 속도 slider
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(20)
        self.speed_slider.setValue(1)
        self.speed_slider.valueChanged.connect(self.속도_변경)

        self.speed_label = QLabel(f'캡쳐 속도: {self.speed:.1f}초')
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        font_speed = self.speed_label.font()
        font_speed.setPointSize(10)
        self.speed_label.setFont(font_speed)

        self.title = QLabel('E-Book PDF 생성기', self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_title = self.title.font()
        font_title.setPointSize(20)
        self.title.setFont(font_title)

        self.stat = QLabel('', self)
        self.stat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_stat = self.stat.font()
        font_stat.setPointSize(18)
        font_stat.setBold(True)
        self.stat.setFont(font_stat)

        self.sign = QLabel('Made By EastShine', self)
        self.sign.setAlignment(Qt.AlignmentFlag.AlignRight)
        font_sign = self.stat.font()
        font_sign.setPointSize(10)
        font_sign.setItalic(True)
        self.sign.setFont(font_sign)

        self.label1 = QLabel('이미지 좌측상단 좌표   ==>   ', self)
        self.label1_1 = QLabel('(0, 0)', self)
        self.label2 = QLabel('이미지 우측하단 좌표   ==>   ', self)
        self.label2_1 = QLabel('(0, 0)', self)
        self.label3 = QLabel('총 페이지 수                       ', self)
        self.label4 = QLabel('PDF 이름                         ', self)

        self.input1 = QLineEdit()
        self.input1.setPlaceholderText("총 페이지 수를 입력하세요.")

        self.input2 = QLineEdit()
        self.input2.setPlaceholderText("생성할 PDF의 이름을 입력하세요.")

        # Box 설정
        box1 = QHBoxLayout()
        box1.addWidget(self.label1)
        box1.addWidget(self.label1_1)
        box1.addWidget(self.button1)

        box2 = QHBoxLayout()
        box2.addWidget(self.label2)
        box2.addWidget(self.label2_1)
        box2.addWidget(self.button2)

        box3 = QHBoxLayout()
        box3.addWidget(self.label3)
        box3.addWidget(self.input1)

        box4 = QHBoxLayout()
        box4.addWidget(self.label4)
        box4.addWidget(self.input2)

        box5 = QHBoxLayout()
        box5.addWidget(self.speed_label)
        box5.addWidget(self.speed_slider)


        box6 = QHBoxLayout()
        box6.addWidget(self.stat)
        box6.addWidget(self.button4)
        box6.addWidget(self.sign)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addStretch(2)
        layout.addLayout(box1)
        layout.addStretch(1)
        layout.addLayout(box2)
        layout.addStretch(1)
        layout.addLayout(box3)
        layout.addStretch(1)
        layout.addLayout(box4)
        layout.addStretch(4)
        layout.addLayout(box5)
        layout.addLayout(box6)
        layout.addWidget(self.button3)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        # 창 크기 고정
        self.setFixedSize(QSize(450, 320))

    def 초기화(self):
        self.num = 1
        self.posX1 = 0
        self.posY1 = 0
        self.posX2 = 0
        self.posY2 = 0
        self.speed = 0.1
        self.total_page = 1
        self.region = {}
        self.label1_1.setText('(0, 0)')
        self.label2_1.setText('(0, 0)')
        self.input1.clear()
        self.input2.clear()
        self.stat.clear()
        self.speed_slider.setValue(1)

    def 좌측상단_좌표_클릭(self):
        def on_click(x, y, button, pressed):
            self.posX1 = int(x)
            self.posY1 = int(y)
            self.label1_1.setText(str(f'({int(x)}, {int(y)})'))
            print('Button: %s, Position: (%s, %s), Pressed: %s ' % (button, x, y, pressed))
            if not pressed:
                return False

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    def 우측하단_좌표_클릭(self):
        def on_click(x, y, button, pressed):
            self.posX2 = int(x)
            self.posY2 = int(y)
            self.label2_1.setText(str(f'({int(x)}, {int(y)})'))
            print('Button: %s, Position: (%s, %s), Pressed: %s ' % (button, x, y, pressed))
            if not pressed:
                return False

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
    def 속도_변경(self):
        self.speed = self.speed_slider.value() / 10.0
        self.speed_label.setText(f'캡쳐 속도: {self.speed:.1f}초')

    def btn_click(self):

        if self.input1.text() == '':
            self.stat.setText('페이지 수를 입력하세요.')
            self.input1.setFocus()
            return

        if self.input2.text() == '':
            self.stat.setText('PDF 제목을 입력하세요.')
            self.input2.setFocus()
            return

        pos_x, pos_y = pyautogui.position()

        if not(os.path.isdir('pdf_images')):
            os.mkdir(os.path.join('pdf_images'))

        self.total_page = int(self.input1.text())

        # The screen part to capture
        self.region = {'top': self.posY1, 'left': self.posX1, 'width': self.posX2 - self.posX1,
                  'height': self.posY2 - self.posY1}

        m = mouse.Controller()
        mouse_left = mouse.Button.left
        kb_control = Controller()

        try:
            # 화면 전환 위해 한번 클릭
            time.sleep(2)
            m.position = (self.posX1, self.posY1)

            time.sleep(2)
            m.click(mouse_left)
            time.sleep(2)
            m.position = (pos_x, pos_y)

            # 파일 저장
            while self.num <= self.total_page:

                time.sleep(self.speed)

                # 캡쳐하기
                with mss.mss() as sct:
                    # Grab the data
                    img = sct.grab(self.region)
                    # Save to the picture file
                    mss.tools.to_png(img.rgb, img.size, output=f'pdf_images/img_{str(self.num).zfill(4)}.png')

                # 페이지 넘기기
                kb_control.press(Key.right)
                kb_control.release(Key.right)

                self.num += 1

            print("캡쳐 완료!")
            self.stat.setText('PDF 변환 중..')
            path = 'pdf_images'
            # 이미지 파일 리스트
            self.file_list = os.listdir(path)
            self.file_list = natsort.natsorted(self.file_list)

            # .DS_Store 파일이름 삭제
            if '.DS_Store' in self.file_list:
                del self.file_list[0]

            img_list = []

            # PDF 첫 페이지 만들어두기
            img_path = 'pdf_images/' + self.file_list[0]
            im_buf = Image.open(img_path)
            cvt_rgb_0 = im_buf.convert('RGB')

            for i in self.file_list:
                img_path = 'pdf_images/' + i
                im_buf = Image.open(img_path)
                cvt_rgb = im_buf.convert('RGB')
                img_list.append(cvt_rgb)

            del img_list[0]

            pdf_name = self.input2.text()
            if pdf_name == '':
                pdf_name = 'default'

            cvt_rgb_0.save(pdf_name+'.pdf', save_all=True, append_images=img_list, quality=100)
            print("PDF 변환 완료!")
            self.stat.setText('PDF 변환 완료!')
            shutil.rmtree('pdf_images/')

        except Exception as e:
            print('예외 발생. ', e)
            self.stat.setText('오류 발생. 종료 후 다시 시도해주세요.')

        finally:
            self.num = 1
            self.file_list = []


app = QApplication(sys.argv)

window = MainWindow()
window.show()

# 이벤트 루프 시작
app.exec()