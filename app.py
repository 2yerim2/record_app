from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 업로드 폴더 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# OpenAI 클라이언트 초기화
client = OpenAI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """녹음된 오디오를 텍스트로 변환"""
    if 'audio' not in request.files:
        return jsonify({'error': '오디오 파일이 없습니다'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
    
    # 파일 저장
    filename = secure_filename(audio_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(filepath)
    
    try:
        # OpenAI Whisper API를 사용하여 음성을 텍스트로 변환
        with open(filepath, 'rb') as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="ko"  # 한국어로 지정
            )
        
        text = transcript.text
        
        # 파일 삭제
        os.remove(filepath)
        
        return jsonify({'text': text})
    
    except Exception as e:
        # 에러 발생 시 파일 삭제
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    """텍스트를 3줄로 요약"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    try:
        # GPT를 사용하여 3줄 요약
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "다음 텍스트의 핵심을 3줄로 요약해주세요. 각 줄은 간결하고 명확하게 작성해주세요."},
                {"role": "user", "content": text}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip()
        
        return jsonify({'summary': summary})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)

