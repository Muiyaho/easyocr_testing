from flask import Flask, request, render_template, send_from_directory, redirect, url_for, jsonify
import easyocr
import os
import json
import torch

app = Flask(__name__)

# 업로드된 파일을 저장할 폴더 경로 설정
UPLOAD_FOLDER = 'static/uploads/'
DATA_FOLDER = 'data/'
MODEL_FOLDER = 'model/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
app.config['MODEL_FOLDER'] = MODEL_FOLDER

# EasyOCR reader 초기화 (영어와 한글 지원)
reader = easyocr.Reader(['en', 'ko'], gpu=False)


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


@app.route('/correct', methods=['POST'])
def correct():
    # 수정된 텍스트를 받아서 처리하는 엔드포인트
    data = request.json
    corrected_text = data['correctedText']
    file_path = data['file_path']

    # 원본 이미지 파일 이름 추출
    filename = file_path.split('/')[-1]

    # 수정된 텍스트와 파일 경로를 JSON 파일로 저장
    correction_data = {
        'file_path': file_path,
        'corrected_text': corrected_text
    }
    with open(os.path.join(app.config['DATA_FOLDER'], f'{filename}.json'), 'w') as f:
        json.dump(correction_data, f)

    # 수정된 텍스트를 다시 렌더링
    return render_template('index.html', itemOptionList=corrected_text, file_path=file_path)


@app.route('/reset', methods=['POST'])
def reset():
    # 업로드된 파일을 삭제하는 엔드포인트
    file_path = request.form.get('file_path')
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # 업로드된 파일을 제공하는 라우트
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/train', methods=['POST'])
def train():
    # 모델을 재학습시키는 엔드포인트
    train_data = []
    for filename in os.listdir(app.config['DATA_FOLDER']):
        if filename.endswith('.json'):
            with open(os.path.join(app.config['DATA_FOLDER'], filename), 'r') as f:
                correction_data = json.load(f)
                image_path = correction_data['file_path']
                corrected_text = correction_data['corrected_text']
                train_data.append((image_path, corrected_text))

    # 모델 학습
    reader.train(train_data, train_data, batch_size=8, num_epochs=10, learning_rate=1e-4)

    # 모델 저장
    if not os.path.exists(app.config['MODEL_FOLDER']):
        os.makedirs(app.config['MODEL_FOLDER'])
    torch.save(reader.model.state_dict(), os.path.join(app.config['MODEL_FOLDER'], 'model.pth'))

    return jsonify({"status": "Model training completed"})


if __name__ == '__main__':
    # 업로드 폴더가 없을 경우 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if not os.path.exists(MODEL_FOLDER):
        os.makedirs(MODEL_FOLDER)
    app.run(debug=True)  # 디버그 모드로 Flask 앱 실행
