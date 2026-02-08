@echo off
chcp 65001 > nul

@echo off
echo 휴대폰 번호 수정은 min_config.json 파일에서 H3에 있는 phonenumber 를 수정하세요.

@echo off
cd /d "%~dp0"
python -m pytest -s tests\ui_tests\H3\test_H3_Basic.py --env=H3
pause