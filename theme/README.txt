EDS Compare Studio — CSS 변경안

보라색·라벤더 스타일의 CSS와 독립적인 화면 표시 예시입니다.
이 패키지에는 기존 EDS 프로그램의 소스나 실행 파일이 포함되어 있지 않습니다.
기존 프로그램에는 아직 적용되지 않았으며, 실제 EDS 기능 및 Windows 실행 검증은 미완료입니다.

lavender-refresh.css: 기존 web/studio.css 뒤에 추가할 스타일
input-preview.html / result-preview.html: 디자인 표시 예시. 실제 앱 화면이 아닙니다.
apply_theme.py: CSS 백업 및 HTML·JavaScript 동일성 확인을 포함한 적용 도구

실행 형식: python apply_theme.py <기존_프로그램_폴더>
원본 CSS는 studio.css.before_lavender.bak으로 보존됩니다.
