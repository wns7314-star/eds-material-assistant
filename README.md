# EDS Material Assistant

디스플레이 공정의 EDS 원소 조성으로 물질 후보를 비교하는 Python 프로그램입니다.

## 다운로드

[Windows 실행 프로그램 · 소스 · 제작 프롬프트 다운로드](https://github.com/wns7314-star/eds-material-assistant/releases/tag/v1.1.0)

릴리스의 **Assets → EDS_Assistant_Windows.zip**을 선택하세요. 전체 압축을 해제한 뒤 `EDS_Assistant.exe`를 실행합니다. `app`과 `runtime` 폴더를 함께 유지하세요. `START_HERE.html`에 사용법이 있습니다.

- `EDS_Assistant_Python_Source.zip`: Python 소스와 테스트
- `EDS_Development_Prompt.txt`: 제작 요구사항 및 프롬프트
- `QA_REPORT.md`: 검증 결과와 범위

GitHub 자동 생성 `Source code (zip)` 또는 저장소의 `Download ZIP`은 실행 패키지가 아닙니다. 릴리스 첨부 파일을 다운로드하세요.

## 기능

원소기호·한글명·영문명 선택, Mass 단독 입력, 합계·정규화 자동 계산, 디스플레이 관련 물질 후보 및 추가 확인 항목, 분석 이력·Trend, 결과 내보내기를 지원합니다.

## 검증 상태

Linux에서 코어 테스트 56개 및 GUI 시나리오 41개를 통과했습니다. Windows 네이티브 EXE 실행과 실제 생산 시료 식별 정확도는 아직 검증하지 않았으므로 검증용 Pre-release로 배포합니다.

EDS 조성 유사도 점수는 정답 확률이 아닙니다. EDS 정량표만으로 화학구조·결정상·오염 발생원을 확정할 수 없습니다. 표준시료 및 추가 분석과 함께 사용하세요.
