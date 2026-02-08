import requests
import json
import sys
import traceback
import os
import time
import pytest
from contextlib import contextmanager
from sshtunnel import SSHTunnelForwarder
import pymysql
import paramiko
import datetime

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import (TimeoutException, NoSuchElementException, WebDriverException)
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from appium.webdriver.common.appiumby import AppiumBy


##############################################
# 각종 식 간략화 
##############################################
class TM:      

    # 오브젝트 내부 클릭 위치 정하는 함수
    '''
    Default 값은 길이 기준 길이의 퍼센트 위치 w=50, h=50 로 중앙 클릭이고,
    왼쪽 상단을 (0,0) 기준으로 하여 h 는 아래로 w 는 우측으로 기준으로 함
    h 와 w 값은 퍼센트 기준으로 75 를 입력할 경우는 75% 지점을 지정 한다는 의미
    '''    
    @staticmethod
    def custom_click(driver, element, w=50, h=50):

        actions = ActionBuilder(driver)
        touch = PointerInput("touch", "finger1")
        actions.add_pointer_input("touch", touch)

        # element의 위치 (좌표), 사이즈 가져오기
        x, y = element.location['x'], element.location['y']
        width, height = element.size['width'], element.size['height']

        # 클릭할 실제 화면 좌표 계산
        tap_x = x + (width  * (w / 100.0))
        tap_y = y + (height * (h / 100.0))

        (actions.pointer_action
            .move_to_location(tap_x, tap_y)
            .pointer_down()
            .pointer_up())
        actions.perform()
    
    #문자 인증
    '''
    문자 인증 시 받은 숫자를 하나씩 버튼 종류별로 누르는 함수
    code_value = "12345" 일 경우
    1 버튼, 2 버튼... 5버튼 을 순서대로 한번씩 누름
    '''
    @staticmethod
    def input_code(driver, code_value):
        for digit in str(code_value):  # int로 넘어오더라도도 str로 변환
            el = driver.find_element(AppiumBy.XPATH, f"//android.view.View[@content-desc='{digit}']")
            el.click()
            time.sleep(0.5) 
    
    # view desc 오브젝트 click
    @staticmethod
    def view_desc_click(driver, desc):
        el = driver.find_element(
            AppiumBy.XPATH, f"//android.view.View[@content-desc='{desc}']"
        )
        el.click()
        
    # view desc 오브젝트 displayed
    @staticmethod
    def view_desc_displayed(driver, desc):    
        el_check = driver.find_element(
            AppiumBy.XPATH, f"//android.view.View[contains(@content-desc,'{desc}')]"
        )
        assert el_check.is_displayed()



######################################################
# 글로벌 변수- 실제 설정은 init_settings()에서
######################################################
env_key = None
CONFIG_PATH = None
bastion_key = None

TESTRAIL_URL = None
USER = None
API_KEY = None
project_id = None
suite_id = None
run_name = None
screenshot_file = None

RUN_ID = None  # Test Run ID, init_settings 후에 할당


BASTION_HOST = None
BASTION_PORT = None
BASTION_USER = None

RDS_HOST = None
RDS_PORT = None
RDS_USER = None
RDS_PASS = None
RDS_DB   = None
verification_no = None

package_name = None
activity_name = None




######################################################
# 1) josn, pem 위치 세팅
######################################################    
def set_path():
    global env_key, CONFIG_PATH, bastion_key

    base_dir = os.path.dirname(__file__)
    config_path = os.path.join(base_dir, "..", "config", "min_config.json")
    config_path = os.path.normpath(config_path)
    
    # 1) CONFIG_PATH 먼저 지정
    CONFIG_PATH = config_path

    # 2) JSON 로드
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        all_cfg = json.load(f)

    cfg = all_cfg[env_key]

    # 3) bastion_host 정보 있는지 체크
    bastion_host = cfg.get("bastion_host", "")
    if bastion_host:  # 값이 있고, SSH를 쓸 때만 pem 파일 로드
        pem_path = os.path.join(base_dir, "..", "config", f"{env_key}_Bastion-Key.pem")
        pem_path = os.path.normpath(pem_path)

        try:
            bastion_key = paramiko.RSAKey.from_private_key_file(pem_path)
        except Exception as e:
            print(f"Please check the bastion key file: {e}")
            bastion_key = None
    else:
        # SSH 정보가 없는 경우
        bastion_key = None

def init_settings():
    
    global env_key
    global TESTRAIL_URL, USER, API_KEY, project_id, suite_id, run_name
    global screenshot_file
    global BASTION_HOST, BASTION_PORT, BASTION_USER
    global RDS_HOST, RDS_PORT, RDS_USER, RDS_PASS, RDS_DB
    global verification_no, package_name, activity_name
        
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            all_cfg = json.load(f)
    cfg = all_cfg[env_key]

    TESTRAIL_URL = cfg["testrail_url"]
    USER = cfg["user"]
    API_KEY = cfg["api_key"]
    project_id = cfg["project_id"]
    suite_id = cfg["suite_id"]
    run_name = cfg["run_name"]
    screenshot_file = cfg["screenshot_file"]

    BASTION_HOST = cfg["bastion_host"]
    BASTION_PORT = cfg["bastion_port"]
    BASTION_USER = cfg["bastion_user"]

    RDS_HOST = cfg["rds_host"]
    RDS_PORT = cfg["rds_port"]
    RDS_USER = cfg["rds_user"]
    RDS_PASS = cfg["rds_pass"]
    RDS_DB   = cfg["rds_db"]
    
    verification_no = cfg["phonenumber"]
    
    package_name  = cfg["package_name"]
    activity_name = cfg["activity_name"]
    
    
    
    # # 위 세팅이 끝난 뒤, 테스트런 생성
    # RUN_ID = create_test_run()
    
    # RUN_ID = None

######################################################
# 3) TestRail / DB
######################################################
def create_test_run(app_version=None):
    
    global RUN_ID
    
    endpoint = f"{TESTRAIL_URL}index.php?/api/v2/add_run/{project_id}"
    headers = {"Content-Type": "application/json"}

    # 날짜 문자열
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # version_info가 있으면 run_name 뒤에 추가
    final_run_name = run_name
    if app_version:
        final_run_name += f" (v{app_version})"

    # description 필드에 버전과 날짜를 기록
    desc_text = ""
    if app_version:
        desc_text += f"앱 버전 : v{app_version}\n"
    desc_text += f"수행 날짜 : {today_str}"

    data = {
        "suite_id": suite_id,
        "name": final_run_name,
        "include_all": True,
        "description": desc_text
    }

    resp = requests.post(endpoint, headers=headers, auth=(USER, API_KEY), data=json.dumps(data))
    resp.raise_for_status()
    created_run = resp.json()
    
    RUN_ID = created_run["id"]  # 전역 변수에 저장
    return RUN_ID

def add_result_for_case(run_id, case_id, status_id, comment=""):
    endpoint = f"{TESTRAIL_URL}index.php?/api/v2/add_result_for_case/{run_id}/{case_id}"
    headers = {"Content-Type": "application/json"}
    data = {
        "status_id": status_id,
        "comment": comment
    }
    response = requests.post(endpoint, auth=(USER, API_KEY), headers=headers, data=json.dumps(data))
    response.raise_for_status()

    result_obj = response.json()
    return result_obj["id"]

def add_attachment_to_result(result_id, file_path):
    endpoint = f"{TESTRAIL_URL}index.php?/api/v2/add_attachment_to_result/{result_id}"
    with open(file_path, "rb") as f:
        files = {"attachment": f}
        response = requests.post(endpoint, auth=(USER, API_KEY), files=files)
        response.raise_for_status()

# DB 불러오기
def get_code():
    # SSH 포트 포워딩 설정
    with SSHTunnelForwarder(
        (BASTION_HOST, BASTION_PORT),
        ssh_username=BASTION_USER,
        ssh_private_key=bastion_key,
        remote_bind_address=(RDS_HOST, RDS_PORT)
        
    ) as tunnel:
        
        # SSHTunnelForwarder가 생성해 준 포트 (tunnel.local_bind_port)를 통해 RDS 접속
        conn = pymysql.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user=RDS_USER,
            password=RDS_PASS,
            db=RDS_DB,
            charset='utf8'
        )
        
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT code 
                    FROM user_verification 
                    WHERE verification_no = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                cursor.execute(sql, (f"010{verification_no}",))
                result = cursor.fetchone()
                
                if result:
                    return result[0]  # code 값
                else:
                    return None
        finally:
            conn.close()
        


######################################################
# 4) appium driver fixture
######################################################
# conftest.py 로 이동




######################################################
# 고정 사용
######################################################

# 앱 버전 가져오기 appium 2.0 이상 에서만 사용 가능
def get_installed_app_version(driver, package_name: str) -> str:
    """
    Appium 2.x의 mobile: shell 사용
    adb shell dumpsys package <package_name> → versionName 파싱
    """
    shell_result = driver.execute_script("mobile: shell", {
        "command": "dumpsys",
        "args": ["package", package_name],
        "includeStderr": True,
        "timeout": 5000
    })
    dumpsys_output = shell_result.get("stdout", "")

    for line in dumpsys_output.splitlines():
        if "versionName=" in line:
            return line.strip().split("=")[-1]
    return "Unknown"

# 스크린샷 생성 삭제
def cleanup_screenshot_file():
    if screenshot_file and os.path.exists(screenshot_file):
        os.remove(screenshot_file)        

# Case 코드에 들어가는 with 간략화
# Default 값은 실패 시 중단, raise_on_fail=False 입력 시 실패해도 테스트 진행
@contextmanager
def case_context(driver, case_id, raise_on_fail=True):
    try:
        yield
        # No exception => Pass
        add_result_for_case(RUN_ID, case_id, 1, "Pass")
    except (TimeoutException, NoSuchElementException, AssertionError, WebDriverException) as e:
        driver.save_screenshot(screenshot_file)

        exception_name = type(e).__name__
        tb = traceback.extract_tb(sys.exc_info()[2])
        if tb:
            first_frame = tb[0]
            err_code = first_frame.line
        else:
            err_code = "N/A"

        comment_message = f"Fail\nErrorcode: {exception_name}\nCode: {err_code}"
        result_id = add_result_for_case(RUN_ID, case_id, 5, comment_message)
        add_attachment_to_result(result_id, screenshot_file)

        if raise_on_fail:
            raise
        else:
            print(f"[WARNING] test_case({case_id}) failed but 'raise_on_fail=False'; continuing.")
    finally:
        cleanup_screenshot_file()
        
