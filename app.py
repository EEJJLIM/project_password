from flask import Flask, request, redirect, send_from_directory, session, render_template_string
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션 사용을 위한 키

users = {}  # email: {username, password}
login_attempts = {}  # email: {'count': int, 'lock_until': timestamp}

MAX_ATTEMPTS = 5
LOCK_TIME = 5 * 60  # 5분 (초)

@app.route('/')
def home():
    return redirect('/index.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    if email in users:
        return '<h3>⚠️ 이미 가입된 이메일입니다.</h3><a href="/signup.html">← 돌아가기</a>'

    users[email] = {'username': username, 'password': password}
    return '<h3>✅ 회원가입 완료!</h3><a href="/login.html">→ 로그인</a>'

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    now = time.time()

    # 시도 정보 가져오기
    attempts = login_attempts.get(email, {'count': 0, 'lock_until': 0})

    # 잠금 상태인지 확인
    if now < attempts['lock_until']:
        remaining = int((attempts['lock_until'] - now) // 60) + 1
        return f'<h3>🚫 로그인 잠금 중입니다. {remaining}분 후 다시 시도해주세요.</h3><a href="/login.html">← 돌아가기</a>'

    # 사용자 존재 여부 확인
    user = users.get(email)
    if user and user['password'] == password:
        # 로그인 성공: 시도 초기화
        login_attempts[email] = {'count': 0, 'lock_until': 0}
        return redirect('/index.html')
    else:
        # 로그인 실패: 시도 수 증가
        attempts['count'] += 1
        if attempts['count'] >= MAX_ATTEMPTS:
            attempts['lock_until'] = now + LOCK_TIME
            attempts['count'] = 0  # 카운트 초기화
            msg = "❌ 로그인 5회 실패. 5분간 잠금되었습니다."
        else:
            msg = f"❌ 로그인 실패 ({attempts['count']}/{MAX_ATTEMPTS}회)"

        login_attempts[email] = attempts
        return f'<h3>{msg}</h3><a href="/login.html">← 다시 시도</a>'

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)
