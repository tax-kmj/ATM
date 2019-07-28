import time
import os
import sys
import zipfile
import json
import PyQt5
# from PyQt5.Qt import QApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QWidget, QPushButton, QRadioButton, QLabel, QLineEdit, QAction, qApp 
from PyQt5.QtWidgets import QMessageBox, QTabWidget, QGridLayout, QGroupBox, QHBoxLayout, QVBoxLayout, QFormLayout
from PyQt5.QtGui import QIcon, QRegExpValidator, QDoubleValidator, QIntValidator
from PyQt5.QtCore import pyqtSlot, Qt, QRegExp

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import data
import Util
from Util import *

'''배포판 실행파일(exe) 만들기 https://wikidocs.net/21952  https://winterj.me/pyinstaller/
pyinstaller 디코딩에러 수정 https://stackoverflow.com/questions/47692960/error-when-using-pyinstaller-unicodedecodeerror-utf-8-codec-cant-decode-byt
I found an answer on another forum. I change the line number 427 in the Python\Lib\site-packages\Pyinstaller\compat.py file
'''
# 처음시작시 경로설정
base_path = "C:\\"
main_dir = "ATM"
main_path = os.path.join(base_path, main_dir)          # APP 저장경로
st1_app_dir = ['loginAPP', 'data']
st1_app_path = os.path.join(main_path, st1_app_dir[0]) # 첫번째앱 저장경로
driver_path = os.path.join(st1_app_path, "driver")    # 크롬드라이버 저장경로
data_path = os.path.join(st1_app_path, "data")        # json 파일 등 저장경로
json_fn = "data.json"                                 # 
full_json_fn = os.path.join(data_path, json_fn)       # json 파일 full 경로

def set_path_make_json():
    """ 앱 경로설정
    """
    try:
        if not os.path.isdir(main_path):
            Util.make_sub_dirs(base_path, main_dir)
    except:
        pass

    # 앱 경로에 하위 경로 설정하고 json 파일 생성후 생성된 json 파일에서 변수로 활용할 파이썬 객체 (nts_dict) 생성
    try:
        if not os.path.isdir(st1_app_path):
            # 1. 하위 APP 디렉토리 없으면 만들고
            Util.make_sub_dirs(main_path, *st1_app_dir)
            Util.make_sub_dirs(st1_app_path, "driver") 

            # 1.1 크롬드라이버 설치(exe 파일과 zip 파일을 같은 경로에...)
            try:
                with zipfile.ZipFile(os.path.join(os.getcwd(), "chromedriver.zip")) as zf:
                    zf.extractall(driver_path)
            except:
                pass

            # 2. 딕셔너리를 json 파일로 만들어 저장
            nts_dict = data.get_nts_dict()
            nts_dict['secret']['크롬경로'] = driver_path      
            with open(full_json_fn, 'w', encoding='utf-8') as fn:
                json.dump(nts_dict, fn, ensure_ascii=False, indent=4)
                # json_data = json.dumps(_dict_data, ensure_ascii=False, indent=4)

            # 3. 저장된 json 파일을 파이썬 객체(딕셔너리)로...
            with open(full_json_fn, encoding='utf-8') as fn:
                nts_dict = json.load(fn)

        elif os.path.isdir(st1_app_path):
            if not os.path.isfile(full_json_fn):
            # 2. 딕셔너리를 json 파일로 만들어 저장
                nts_dict = data.get_nts_dict()        
                with open(full_json_fn, 'w', encoding='utf-8') as fn:
                    json.dump(nts_dict, fn, ensure_ascii=False, indent=4)
                    # json_data = json.dumps(_dict_data, ensure_ascii=False, indent=4)

                # 3. 저장된 json 파일을 파이썬 객체(딕셔너리)로...
                with open(full_json_fn, encoding='utf-8') as fn:
                    nts_dict = json.load(fn) 

            elif os.path.isfile(full_json_fn):
                # 3. 저장된 json 파일을 파이썬 객체(딕셔너리)로...
                with open(full_json_fn, encoding='utf-8') as fn:
                    nts_dict = json.load(fn) 
    except:
        pass
    finally:
        return nts_dict

nts_dict = set_path_make_json() 

# 브라우저 높이에 따른 크롬 실행환경 변경 flag
flag_window_height = True

# 셀레니움 Xpath element 반환함수
def get_element(driver, id):
    try:
        if "세무법인이노택스테헤" not in id:
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((By.XPATH, f"//*[@id=\'{id}\']")))
        elif "세무법인이노택스테헤" in id:
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((By.XPATH, f"//*[@title=\'{id}\']")))
        return element

    except Exception as e:
        err_class_name = e.__class__.__name__
        msg = f"selenium id < {id} >에서 예외 < {err_class_name} >가 발생 하였습니다."
        errmsg = Errpop().critical_pop(msg)


class Ui_nts_ligin(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        # super(QWidget,self).__init__(parent)
        self.bs_id = nts_dict['secret']['부서아이디']   
        self.delay_time = float(nts_dict['secret']['딜레이타임']) 
            
        self.initUI()

    def initUI(self):

        grid = QGridLayout()
        grid.addWidget(self.firstGroup(), 0, 0)
        grid.addWidget(self.secondGroup(), 0, 1)

        self.setLayout(grid)
       
    def firstGroup(self):
        groupbox = QGroupBox('CTA ID 로그인')
        self.radio1 = QRadioButton('W15960')
        self.radio2 = QRadioButton('P27687')
        self.radio1.setChecked(True)

        # QRadioButton 예제 https://wikidocs.net/5237
        self.radio1.clicked.connect(self.radioButtonClicked)
        self.radio2.clicked.connect(self.radioButtonClicked)

        btn1 = QPushButton('홈택스 로그인')
        btn1.setToolTip('HomeTax Login')
        btn1.clicked.connect(self.btn1_click)

        vbox = QVBoxLayout()
        vbox.addWidget(self.radio1)
        vbox.addWidget(self.radio2)
        vbox.addWidget(btn1)
        groupbox.setLayout(vbox)

        return groupbox

    def secondGroup(self):
        # QLineEdit 총괄 : https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget
        groupbox = QGroupBox('부서 ID 및 딜레이 변경 ')

        le1 = QLineEdit()
        le2 = QLineEdit()
        le1.setPlaceholderText(nts_dict['secret']['부서아이디'])
        le2.setPlaceholderText(str(nts_dict['secret']['딜레이타임']))
      
        # 입력제한 http://bitly.kr/wmonM2
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, le2)
        # double_validator = QDoubleValidator(-999.0, 999.0, 2)   ### http://bitly.kr/wmonM2
        le2.setValidator(input_validator)      # double_validator)  
        le2.setMaxLength(3)  

        le1.textChanged[str].connect(self.le1Changed)
        le2.textChanged[str].connect(self.le2Changed)

        btn2 = QPushButton('변경사항저장', self)
        btn2.setToolTip('저장하기')
        btn2.clicked.connect(self.btn2_click)

        flo = QFormLayout()
        flo.addRow("부서아이디", le1)
        flo.addRow("딜레이타임", le2)
        flo.addRow(btn2)
        groupbox.setLayout(flo)

        return groupbox

    def radioButtonClicked(self):
      
        if self.radio1.isChecked():
            if self.radio1.text() != nts_dict['secret']['세무사관리번호']:
                nts_dict['secret']['세무사관리번호'] = self.radio1.text()
                
        elif self.radio2.isChecked():
            if self.radio2.text() != nts_dict['secret']['세무사관리번호']:
                nts_dict['secret']['세무사관리번호'] = self.radio2.text()
        else:
            pass
        # 2. 수정된 딕셔너리를 json 파일로 만들어 저장      
        with open(full_json_fn, 'w', encoding='utf-8') as fn:
            json.dump(nts_dict, fn, ensure_ascii=False, indent=4)
    
    def btn1_click(self):
        if self.radio1.isChecked():
            if self.radio1.text() != nts_dict['secret']['세무사관리번호']:
                nts_dict['secret']['세무사관리번호'] = self.radio1.text()
                
        elif self.radio2.isChecked():
            if self.radio2.text() != nts_dict['secret']['세무사관리번호']:
                nts_dict['secret']['세무사관리번호'] = self.radio2.text()
        else:
            pass
        # 2. 수정된 딕셔너리를 json 파일로 만들어 저장      
        with open(full_json_fn, 'w', encoding='utf-8') as fn:
            json.dump(nts_dict, fn, ensure_ascii=False, indent=4)

        login = Nts_Login()
        login.path2()

    def le1Changed(self, text):
        self.bs_id = text
      
    def le2Changed(self, text):
        self.delay_time = text
       

    def btn2_click(self):
        # 2. 수정된 딕셔너리를 json 파일로 만들어 저장      
        with open(full_json_fn, 'w', encoding='utf-8') as fn:
            nts_dict['secret']['부서아이디'] = self.bs_id
            nts_dict['secret']['딜레이타임'] = str(self.delay_time)
            json.dump(nts_dict, fn, ensure_ascii=False, indent=4)

class Ui_nts_task(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        # super(QWidget,self).__init__(parent)
        
        self.initUi()

    def initUi(self):

        grid = QGridLayout()
        btn1 = QPushButton()
        grid.addWidget(btn1)
        btn1.clicked.connect(self.btn1_click)

        self.setLayout(grid) 

    def btn1_click(self):
        print("btn1 clicked") 

class Ui_web_task(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        # super(QWidget,self).__init__(parent) 
        label = QLabel('개발중...') 
        layout = QVBoxLayout()
        layout.addWidget(label) 

        self.setLayout(layout)  

class Main(QMainWindow):  # (QWidget): #
    def __init__(self):
        """ QMainWindow 에서는 QHBoxLayout, QVBoxLayout 같은 layout 사용못함.
            QWidget, QDialog 와 달리 QMainWindow 는 자체적으로 layout 가지고 있다. central widget 을 반드시 필요로함.
            https://freeprog.tistory.com/326"""
        super().__init__()
        
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowTitleHint)  # | Qt.FramelessWindowHint)  항상 위에
        # 우하단 위젯
        rect = QDesktopWidget().availableGeometry()   # 작업표시줄 제외한 화면크기 반환
        max_x = rect.width()
        max_y = rect.height()
        # 브라우저 높이에 따른 크롬 실행환경 변경 flag
        global flag_window_height
        if max_y <= 900:
            flag_window_height = False

        width, height = 350 , 220
        # width, height = 350 , 250
        left = max_x - width 
        top = max_y - height 

        self.setGeometry(left, top, width, height)

        # 탭 위젯
        tab1 = Ui_nts_ligin(self)
        tab2 = Ui_nts_task(self)
        tab3 = Ui_web_task(self)

        tabs = QTabWidget()
        tabs.addTab(tab1, '홈택스 로그인')
        tabs.addTab(tab2, '홈택스 작업')
        tabs.addTab(tab3, '웹 작업')

        self.setCentralWidget(tabs)         
        self.setWindowTitle('ATM(자동화)')
        self.setWindowFlags(Qt.FramelessWindowHint)   # windowtitle 제외
        #>>> 메뉴바 https://wikidocs.net/21866
        exitAction = QAction(QIcon('exit.png'), '종료', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        # self.statusBar()

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('&메뉴')
        fileMenu.addAction(exitAction)
        #<<< 메뉴바
        self.statusBar().showMessage('Ready')

        self.show()

# class Errpop(QWidget):
#     def __init__(self):
#         super().__init__()   
#         rect = QDesktopWidget().availableGeometry()   # 작업표시줄 제외한 화면크기 반환
#         max_x = rect.width()
#         max_y = rect.height()

#         width, height = 350 , 250
#         left = max_x - width 
#         top = max_y - height
#         self.setGeometry(left, top, width, height)     

#     def critical_pop(self, msg):    
#         msg = msg
#         QMessageBox.critical(self, '에러 메세지', msg, QMessageBox.Ok)

# class Get_driver:
#     def __init__(self, driver_path, driver_name):
#         self.driver_path = driver_path
#         self.driver_name = driver_name
#         self.full_driver_name = os.path.join(self.driver_path, self.driver_name)

#     def set_driver(self):
        
#         if "chrome" in self.full_driver_name:
#             try:
#                 chrome_options = webdriver.ChromeOptions()

#                 driver = webdriver.Chrome(self.full_driver_name, options=chrome_options)
#                 return driver
#             except:
#                 msg = "드라이버 경로( {0} )에 {1}이(가) 없습니다 !!!".format(self.driver_path, self.driver_name)
#                 errmsg = Errpop().critical_pop(msg)
                
#         elif True :
#             pass          

class Nts_Login:
    def __init__(self):
        driver_path = nts_dict['secret']['크롬경로']    
        driver_name = nts_dict['secret']['크롬드라이버'] 
        chrome_driver = Get_driver(driver_path, driver_name)
        self.driver = chrome_driver.set_driver()
        self.driver.get('https://www.hometax.go.kr/')
        # 모니터 작은 경우
        global flag_window_height
        if flag_window_height == False:
            self.driver.maximize_window()
        self.delay_time = float(nts_dict['secret']['딜레이타임'])
        time.sleep(self.delay_time)

    # 홈택스 별도페이지
    def path2(self):
        try:
            _ST1BOX = self.driver.find_element_by_id("ST1BOX")  # 종합소득세 신고
            _ST1BOX.click()
            time.sleep(self.delay_time)
            self.loginnts()
        except:
            self.loginnts()
            time.sleep(self.delay_time + 1)

    def loginnts(self):
        
        # 홈텍스로 이동, 상단 로그인
        get_element(self.driver, nts_dict['elem_id']['login']['최상단로그인']).click()
        # self.driver.implicitly_wait(delay_time)

        # 메인영역
        elem = get_element(self.driver, nts_dict['메인영역'])
        self.driver.switch_to_frame(elem)
        time.sleep(self.delay_time)
        
        # 관리자인 경우 공인인증서 직접로그인
        if nts_dict['secret']['부서아이디'] == nts_dict['secret']['수퍼아이디']:

            get_element(self.driver, nts_dict['elem_id']['login']['인증서로그인']).click()
            time.sleep(self.delay_time)

            # 공인인증서 영역
            elem = get_element(self.driver, nts_dict['elem_id']['login']['공인인증서영역'])
            self.driver.switch_to_frame(elem)
            time.sleep(self.delay_time + 0.5)
            
            # 공인인증서 선택
            get_element(self.driver, nts_dict['elem_id']['login']['공인인증서명칭']).click()
            time.sleep(self.delay_time)

            # 인증서 비밀번호 입력
            cert_pw = nts_dict['secret']['공인인증서비번']
            get_element(self.driver, nts_dict['elem_id']['login']['공인인증서비번']).send_keys(cert_pw)
            get_element(self.driver, nts_dict['elem_id']['login']['공인인증서확인']).click()
            time.sleep(self.delay_time)
            self.driver.switch_to_alert.accept()

            # 메인영역
            elem = get_element(self.driver, nts_dict['메인영역'])
            self.driver.switch_to_frame(elem)
            time.sleep(self.delay_time)

            # 세무대리인 관리번호 비번
            cta_id = nts_dict['secret']['세무사관리번호']
            cta_pw = nts_dict['secret']['세무사비번']
            get_element(self.driver, nts_dict['elem_id']['login']['세무사관리번호']).send_keys(cta_id)
            get_element(self.driver, nts_dict['elem_id']['login']['세무사비번']).send_keys(cta_pw)
            # 로그인 버튼
            get_element(self.driver, nts_dict['elem_id']['login']['최종로그인']).click()

        else:
            # 부서아이디 비번 로그인
            bs_id = nts_dict['secret']['부서아이디']
            bs_pw = nts_dict['secret']['부서비번']
            get_element(self.driver, nts_dict['elem_id']['login']['부서아이디']).send_keys(bs_id)
            get_element(self.driver, nts_dict['elem_id']['login']['부서비번']).send_keys(bs_pw)
            # 부서아이디로그인 버튼
            get_element(self.driver, nts_dict['elem_id']['login']['부서아이디로그인']).click()
            time.sleep(self.delay_time + 1)

            # 공인인증서 영역
            elem = get_element(self.driver, nts_dict['elem_id']['login']['공인인증서영역'])
            self.driver.switch_to_frame(elem)
            time.sleep(self.delay_time + 1)

            # 공인인증서 선택
            get_element(self.driver, nts_dict['elem_id']['login']['공인인증서명칭']).click()
            time.sleep(self.delay_time)

            # 인증서 비밀번호 입력
            cert_pw = nts_dict['secret']['공인인증서비번']
            get_element(self.driver, nts_dict['elem_id']['login']['공인인증서비번']).send_keys(cert_pw)
            get_element(self.driver, nts_dict['elem_id']['login']['공인인증서확인']).click()
            time.sleep(self.delay_time + 1)
            self.driver.switch_to.alert.accept()

            # 메인영역
            elem = get_element(self.driver, nts_dict['메인영역'])
            self.driver.switch_to_frame(elem)
            time.sleep(self.delay_time)

            # 세무대리인 관리번호 비번
            cta_id = nts_dict['secret']['세무사관리번호']
            cta_pw = nts_dict['secret']['세무사비번']
            get_element(self.driver, nts_dict['elem_id']['login']['세무사관리번호']).send_keys(cta_id)
            get_element(self.driver, nts_dict['elem_id']['login']['세무사비번']).send_keys(cta_pw)
            # 로그인 버튼
            get_element(self.driver, nts_dict['elem_id']['login']['최종로그인']).click()

if __name__ == "__main__":
    # login = Nts_Login()
    # login.path2()

    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())

