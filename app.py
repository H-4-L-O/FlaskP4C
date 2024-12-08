from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Docker MySQL 컨테이너 연결
# root: MySQL 사용자 이름
# 7931: MySQL 비밀번호
# localhost:3308: MySQL 호스트 및 포트 (Docker 컨테이너 매핑)
# p4cweb: 사용하려는 데이터베이스 이름
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:7931@localhost:3308/p4cweb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 불필요한 경고 메시지 방지

# SQLAlchemy 초기화 및 데이터베이스 연결
db = SQLAlchemy(app)

# 데이터베이스 테이블 정의
# Post 클래스는 게시글 테이블을 나타냄
# id, title, content는 테이블의 열(column)을 정의
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 고유 식별자 (Primary Key)
    title = db.Column(db.String(100), nullable=False)  # 제목 (최대 100자)
    content = db.Column(db.Text, nullable=False)  # 내용 (길이 제한 없음)

# 데이터베이스 초기화
# 정의된 모델(Post)에 따라 테이블을 생성
with app.app_context():
    db.create_all()

# 메인 페이지 - 게시글 목록
@app.route('/')
def index():
    posts = Post.query.all()  # 모든 게시글 가져오기
    return render_template('index.html', posts=posts)  # index.html 템플릿 렌더링

# 게시글 작성 및 수정 페이지
@app.route('/write', methods=['GET', 'POST'])
@app.route('/write/<int:post_id>', methods=['GET', 'POST'])
def write_post(post_id=None):
    # 수정 모드: post_id가 주어졌을 경우 해당 게시글 가져오기
    post = Post.query.get(post_id) if post_id else None

    if request.method == 'POST':
        # 사용자 입력 데이터 가져오기
        title = request.form['title']
        content = request.form['content']

        if post:  # 수정
            post.title = title
            post.content = content
        else:  # 새 게시글 작성
            new_post = Post(title=title, content=content)
            db.session.add(new_post)

        # 변경 사항 저장
        db.session.commit()
        return redirect('/')  # 메인 페이지로 리다이렉트

    return render_template('post.html', post=post)  # 작성/수정 페이지 렌더링

# 게시글 삭제
@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)  # 해당 게시글이 없으면 에러 반환
    db.session.delete(post)  # 게시글 삭제
    db.session.commit()  # 변경 사항 저장
    return redirect('/')  # 메인 페이지로 리다이렉트

if __name__ == "__main__":
    # Flask 개발 서버 실행
    app.run(debug=True)
