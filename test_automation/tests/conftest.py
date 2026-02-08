# conftest.py (TestAutomation/ 경로에 생성)

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
import json
import os
import lib.auto_module as am

# 전역 변수
app_version = None

# custom CLI 옵션 입력
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="input --env (ex H2 or H3)"
    )

#CLI 옵션 fixture 세팅
@pytest.fixture(scope="session", autouse=True)
def setup_env(pytestconfig):
    env_key = pytestconfig.getoption("env")
    # CLI 명령어 전역변수에 반영
    am.env_key = env_key
    if not env_key:
        # pytest.exit을 이용해 종료하거나, ValueError 등 예외를 발생시킴
        pytest.exit("please input env keycode (ex pytest --env=H3)", returncode=1)

    # 이제 set_path() / init_settings() 호출
    am.set_path()
    am.init_settings()

    # 필요하면 env_key를 반환 가능
    return env_key

#앱 새로 실행하기
@pytest.fixture(scope="session")
def driver_new():        
    
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.skip_unlock = False
    options.app_package = am.package_name
    options.app_activity = am.activity_name
    options.event_timings = True
    options.new_command_timeout = 1000
    options.uiautomator2_server_install_timeout = 60000
    options.adb_exec_timeout = 600000
    # options.no_reset = True

    drv = webdriver.Remote("http://localhost:4723", options=options)
    drv.implicitly_wait(15)
    
    # 앱 버전 조회
    app_version = am.get_installed_app_version(drv, am.package_name)
    
    
    #print("conftest_DEBUG:", app_version)
    
    yield drv, app_version
    drv.quit()
    
#앱 실행 하지 않기기 테스트 용
@pytest.fixture(scope="session")
def driver_exist():    
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.skip_unlock = False
    options.event_timings = True
    options.new_command_timeout = 1000
    options.uiautomator2_server_install_timeout = 60000
    options.adb_exec_timeout = 600000

    drv = webdriver.Remote("http://localhost:4723", options=options)
    drv.implicitly_wait(15)
    yield drv
    drv.quit()
