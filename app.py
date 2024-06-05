from flask import Flask, request, render_template, send_from_directory
import easyocr
import os

app = Flask(__name__)

# 업로드된 파일을 저장할 폴더 경로 설정
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# EasyOCR reader 초기화 (영어와 한글 지원)
reader = easyocr.Reader(['en', 'ko'])


@app.route('/', methods=['GET', 'POST'])
def index():
    # OCR 결과를 저장할 리스트 초기화
    itemOptionList = []
    file_path = None

    # POST 요청일 경우 파일 업로드 처리
    if request.method == 'POST':
        if 'file' not in request.files:
            # 파일이 없을 경우 초기 화면으로 렌더링
            return render_template('index.html', itemOptionList=itemOptionList, file_path=file_path)

        file = request.files['file']

        if file.filename == '':
            # 파일 이름이 없을 경우 초기 화면으로 렌더링
            return render_template('index.html', itemOptionList=itemOptionList, file_path=file_path)

        if file:
            # 파일 경로 설정 후 저장
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # EasyOCR을 사용하여 이미지에서 텍스트 추출
            results = reader.readtext(file_path)

            # 추출된 텍스트를 리스트에 추가
            itemOptionList = [result[1] for result in results]

    # 결과와 함께 초기 화면 렌더링
    return render_template('index.html', itemOptionList=itemOptionList, file_path=file_path)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # 업로드된 파일을 제공하는 라우트
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    # 업로드 폴더가 없을 경우 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)  # 디버그 모드로 Flask 앱 실행