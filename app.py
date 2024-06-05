from flask import Flask, request, render_template
import easyocr
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# EasyOCR reader 초기화
reader = easyocr.Reader(['en', 'ko'])  # 필요한 언어로 설정


@app.route('/', methods=['GET', 'POST'])
def index():
    itemOptionList = []
    file_path = None

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', itemOptionList=itemOptionList, file_path=file_path)

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', itemOptionList=itemOptionList, file_path=file_path)

        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # EasyOCR로 이미지 처리
            results = reader.readtext(file_path)

            # 결과를 itemOptionList에 추가
            itemOptionList = [result[1] for result in results]

    return render_template('index.html', itemOptionList=itemOptionList, file_path=file_path)


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)