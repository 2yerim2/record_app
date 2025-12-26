# record_app
음성 녹음하고 텍스트로 변환해 요약해주는 녹음기

# 목적 설명
- 대학 수업 강의를 듣는 학생들이 수업의 중요한 내용을 놓치거나 공부를 위해 수업 내용을 복기해야하는 상황에서 이를 돕고 , 효율적이고 정확한 학습을 돕기 위해서 이 자동 번역 녹음기 아이디어를 떠올리고, 구현하게 되었음.

# 기능 설명
## 1.녹음 기능
-녹음기 앱을 사용하는 기기의 마이크와 연결하여 녹음을 진행하고 'audio' 파일을 저장함.
```recordBtn.addEventListener('click', async () => {
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
```

## 2.텍스트 변환 기능
```filename = secure_filename(audio_file.filename)
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
        # 에러 발생 시 파일 삭제(변수e에 에러 저장)
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500
```
-request 객체를 이용해서 음성 녹음이 저장된 'audio' 파일을 찾고 OpenAI Whisper API를 사용해 음성을 텍스트로 변환함.

## 3. 3줄 요약 기능
```@app.route('/summarize', methods=['POST'])
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
```
-음성을 텍스트로 변환한 파일을 gpt-3.5-turbo모델을 이용해 내용 핵심을 3줄로 요약함. gpt에게 '간결하고 명확하게 작성해달라'고 프롬프트를 주어 변환. max_tokens은 200으로 설정하여 딱 3줄 정도 분량으로 작성하게 만들었고 temperature는 0.3으로 창의성을 설정함.

# 부연 설명
-UI는 HTML을 이용해서 구현함.
-녹음 시작,녹음 번역, 3줄 요약 버튼이 각각 있고 이를 누르면 각각의 기능이 순차적으로 실행됨.
-번역 결과, 요약 결과 칸이 각각 있어서 음성을 텍스트로 변환한 전체 결과를 윗 칸에서 보여주고, gpt를 이용해 이를 3줄 요약한 결과를 밑 칸에서 보여줌.
<img width="754" height="504" alt="image" src="https://github.com/user-attachments/assets/87739dea-08d3-4b3d-90c7-91a539d5dc1f" />
<img width="753" height="630" alt="image" src="https://github.com/user-attachments/assets/1b7d081e-fc67-4fcd-a14c-ffaadc09ef0f" />




