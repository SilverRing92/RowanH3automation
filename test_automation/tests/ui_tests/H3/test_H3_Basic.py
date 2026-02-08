import pytest
import time
import os
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from lib.auto_module import case_context, TM, get_code, create_test_run
import datetime
import lib.auto_module as am

def test_h3_login_flow(driver_new):
    driver, app_version = driver_new   
    create_test_run(app_version)
    tm = TM
    
    # C181115 접속
    with case_context(driver, 181115):
        time.sleep(2)
        el = driver.find_element(AppiumBy.XPATH, "//android.view.View[@content-desc='병원 계정 번호를\n눌러주세요']")
        assert el.is_displayed(), "병원 계정 번호 표시 안 됨"

    # C181116 병원 계정 번호 입력
    with case_context(driver, 181116):
        for i in range(5):
            el = driver.find_element(AppiumBy.XPATH, "//android.view.View[@content-desc='0']")
            el.click()
            time.sleep(0.5)
            
        driver.implicitly_wait(5)
        el_next = driver.find_element(AppiumBy.XPATH, "//android.view.View[@content-desc='다음']")
        assert el_next.is_displayed(), "5자리 입력시 다음 버튼 노출 안됨"       
    
    # C181117 다음 버튼 클릭
    with case_context(driver, 181117):
        driver.implicitly_wait(5)
        el_next = driver.find_element(AppiumBy.XPATH, "//android.view.View[@content-desc='다음']")
        el_next.click()
        
        time.sleep(2)
        
        title_check = driver.find_element(AppiumBy.XPATH,
                                          "//android.view.View[@content-desc='본인 핸드폰 번호를\n눌러주세요']")
        assert title_check.is_displayed(), "핸드폰 입력 화면 전환 실패"
    
    # C181118 전화 번호 입력 후 접속 버튼 확인   
    with case_context(driver, 181118):
        
        code_value = am.verification_no
        
        tm.input_code(driver, code_value)
        
        el_next = driver.find_element(AppiumBy.XPATH,
                                      "//android.view.View[@content-desc='접속하기']")
        assert el_next.is_displayed(), "접속하기 버튼 노출 안됨"
        
    
    # C181119 접속 하기 버튼 후 문자 인증 화면 확인
    with case_context(driver, 181119):
        el_next = driver.find_element(AppiumBy.XPATH,
                                      "//android.view.View[@content-desc='접속하기']")
        el_next.click()
        
        time.sleep(2)
        
        title_check = driver.find_element(AppiumBy.XPATH,
                                          "//android.view.View[contains(@content-desc,'번호로\n수신된 인증번호 5자리를\n입력해 주세요')]")
        assert title_check.is_displayed(), "문자인증 화면 노출 안됨"
    
        
    # C181120 문자인증 번호 입력
    with case_context(driver, 181120):
        # 문자 전송 대기 시간(서버가 아픈 경우 느린 경우가 있어서 10초로 세팅)
        time.sleep(7)
        
        # helpers 에서 db code 돌리고 문자 인증 code 만 땡겨옴
        code_value = get_code()      
        
        time.sleep(3)
        
        if not code_value:
            raise AssertionError
        
        tm.input_code(driver, code_value)

        # 혹은 필요하면 추가 로직(예: '다음' 버튼 누르기)을 이어서 처리
        el = driver.find_element(AppiumBy.XPATH, 
                                    "//android.view.View[@content-desc='인증하기']")
        assert el.is_displayed(), "인증하기 버튼 노출 되지 않음"
        
    # C181121 문자인증 완료 후 진입
    with case_context(driver, 181121):
        el = driver.find_element(AppiumBy.XPATH, 
                                    "//android.view.View[@content-desc='인증하기']")
        el.click()
        
        el_check = el = driver.find_element(AppiumBy.XPATH, 
                                            "//android.view.View[contains(@content-desc,'안녕하세요')]")
        assert el_check.is_displayed()
        
    # C181503 접속 첫 화면
    with case_context(driver, 181503):
        tm.view_desc_displayed(driver, '안녕하세요')
        
    time.sleep(30)
    
    # C181504 이루고 싶은 목표 선택 화면
    with case_context(driver, 181504):
        tm.view_desc_displayed(driver, '먼저 이루고 싶은 목표를 눌러주세요')
        
    # C181505 푹 잘 자고 싶어 클릭
    with case_context(driver, 181505):
        tm.view_desc_click(driver, '푹 잘 자고 싶어')
        tm.view_desc_displayed(driver, '편안하게 잘 자고 싶으시군요!')   
        
    time.sleep(10) 
    
    # C181506 날짜 입력 화면
    with case_context(driver, 181506):
        tm.view_desc_displayed(driver, '오늘 날짜는 어떻게 되나요?\n년')
    
    
    # 날짜 관련 코딩
    today = datetime.date.today()
    year = today.year
    month = f"{today.month:02d}" 
    day = f"{today.day:02d}" 
    
    # 연도 입력 후 다음 클릭, 일 화면 체크
    # C181507 연도 입력
    with case_context(driver, 181507):
        TM.input_code(driver, year)
        tm.view_desc_click(driver, '다음')
        tm.view_desc_displayed(driver, '오늘 날짜는 어떻게 되나요?\n월')
    
    # C181508 월 입력
    with case_context(driver, 181508):
        TM.input_code(driver, month)
        tm.view_desc_click(driver, '다음')
        tm.view_desc_displayed(driver, '오늘 날짜는 어떻게 되나요?\n일')    
    
    # C181509 일 입력
    with case_context(driver, 181509):
        TM.input_code(driver, day)
        tm.view_desc_click(driver, '다음')
        driver.implicitly_wait(10)
        tm.view_desc_displayed(driver, '하루 시작이 좋네요')

    time.sleep(10)

    # C181510 날씨 입력 화면
    with case_context(driver, 181510):
        tm.view_desc_displayed(driver, '오늘 날씨는 어떤가요')
    
    # C181511 맑아 클릭
    with case_context(driver, 181511):
        el = driver.find_element(AppiumBy.XPATH,
                                       "//android.widget.ImageView[@content-desc='맑아']")
        el.click()
        
        ()
        
        tm.view_desc_displayed(driver, '맑은 날')
        
    time.sleep(10)
        
    # C181513 어제 몇 시간 주무셨나요? 진입
    with case_context(driver, 181513):
        tm.view_desc_displayed(driver, '어제 몇 시간 주무셨나요?\n시간')
        
    # C181514 수면 시간 입력
    with case_context(driver, 181514):
        tm.view_desc_click(driver, '0')
        tm.view_desc_click(driver, '8')
        tm.view_desc_click(driver, '다음')
        tm.view_desc_displayed(driver, '어제 밤에 잘 주무셨나요?')
    
    # C181515 잘 잤어 클릭 
    with case_context(driver, 181515):
        el = driver.find_element(AppiumBy.XPATH,
                                       "//android.widget.ImageView[@content-desc='잘 잤어']")
        el.click()
        
        el_check = driver.find_element(AppiumBy.XPATH,
                                       "//android.view.View[contains(@content-desc,'잘 주무셨다니') or contains(@content-desc,'푹 자고 일어나면')]")
        assert el_check.is_displayed()
        
    time.sleep(10)
        
    # C181516 오늘 식사는 잘 드셨나요 진입
    with case_context(driver, 181516):
        tm.view_desc_displayed(driver, '오늘 식사는 잘 드셨나요?')
    
    # C181517 잘 먹었어 클릭
    with case_context(driver, 181517):
        el = driver.find_element(AppiumBy.XPATH,
                                       "//android.widget.ImageView[@content-desc='잘 먹었어']")
        el.click()
        
        el_check = driver.find_element(AppiumBy.XPATH,
                                       "//android.view.View[contains(@content-desc,'식사를 잘 드셨다니') or contains(@content-desc,'정말 대단해요')]")
        assert el_check.is_displayed()
        
    time.sleep(10)
        
    # C181518 오늘 기분은 어떠신가요 진입
    with case_context(driver, 181518):
        tm.view_desc_displayed(driver, '오늘 기분은 어떠신가요?')
        
    # C181519 좋아 클릭
    with case_context(driver, 181519):
        el = driver.find_element(AppiumBy.XPATH,
                                       "//android.widget.ImageView[@content-desc='좋아']")
        el.click()
        
        el_check = driver.find_element(AppiumBy.XPATH,
                                       "//android.view.View[contains(@content-desc,'기분이 좋으시다니') or contains(@content-desc,'기분 좋은 하루를')]")
        assert el_check.is_displayed()
        
    time.sleep(10)
        
    # C181520 오늘 몸 상태는 어떠신가요 진입
    with case_context(driver, 181520):
        tm.view_desc_displayed(driver, '오늘 몸 상태는 어떠신가요')
        
    # C181521 좋아 클릭
    with case_context(driver, 181521):
        el = driver.find_element(AppiumBy.XPATH,
                                       "//android.widget.ImageView[@content-desc='좋아']")
        el.click()
        el_check = driver.find_element(AppiumBy.XPATH,
                                       "//android.view.View[contains(@content-desc,'좋다') or contains(@content-desc,'좋은 몸')]")
        assert el_check.is_displayed()
        
    time.sleep(5)
        
    # C181522 하루 기록 완료
    with case_context(driver, 181522):
        driver.implicitly_wait(15)
        tm.view_desc_displayed(driver, '하루 기록을 모두 완료했어요')
                