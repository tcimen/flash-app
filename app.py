from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import bcrypt
from datetime import datetime
from sqlalchemy import text
import logging
logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret_key')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DomainCertificate(db.Model):
    __tablename__ = 'domain_certificates'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    osb = db.Column(db.String(100))
    ug = db.Column(db.String(100))
    certificate_owner = db.Column(db.String(255))
    expire_date = db.Column(db.Date)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            flash('Başarıyla giriş yaptınız.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Giriş bilgileri hatalı. Tekrar deneyin.', 'error')
    return render_template('login.html')

@app.route('/test_db')
def test_db():
    try:
        result = db.session.execute(text('SELECT 1'))
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Çıkış yaptınız.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/certifications')
@login_required
def certifications():
    certificates = DomainCertificate.query.all()
    return render_template('certifications.html', certificates=certificates)

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/add', methods=['POST'])
@login_required
def add_certificate():
    try:
        data = request.form
        new_cert = DomainCertificate(
            domain=data['domain'],
            osb=data['osb'],
            ug=data['ug'],
            certificate_owner=data['certificate_owner'],
            expire_date=datetime.strptime(data['expire_date'], '%Y-%m-%d').date()
        )
        db.session.add(new_cert)
        db.session.commit()
        return jsonify({"success": True, "message": "Sertifika başarıyla eklendi."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/update/<int:id>', methods=['PUT'])
@login_required
def update_certificate(id):
    try:
        cert = DomainCertificate.query.get_or_404(id)
        data = request.form
        cert.domain = data['domain']
        cert.osb = data['osb']
        cert.ug = data['ug']
        cert.certificate_owner = data['certificate_owner']
        cert.expire_date = datetime.strptime(data['expire_date'], '%Y-%m-%d').date()
        db.session.commit()
        return jsonify({"success": True, "message": "Sertifika başarıyla güncellendi."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_certificate(id):
    try:
        cert = DomainCertificate.query.get_or_404(id)
        db.session.delete(cert)
        db.session.commit()
        return jsonify({"success": True, "message": "Sertifika başarıyla silindi."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

@app.errorhandler(401)
def unauthorized(error):
    flash('Bu sayfayı görüntülemek için giriş yapmalısınız.', 'error')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)