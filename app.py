from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Docker host IP'sini kullanın (genellikle host.docker.internal)
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'host.docker.internal')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'domain_certificates')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'devops')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'devops')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
db = SQLAlchemy(app)

class DomainCertificate(db.Model):
    __tablename__ = 'domain_certificates'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(100), nullable=False)
    osb = db.Column(db.String(50))
    ug = db.Column(db.String(50))
    certificate_owner = db.Column(db.String(100))
    expire_date = db.Column(db.Date)

@app.route('/')
def index():
    certificates = DomainCertificate.query.all()
    return render_template('index.html', certificates=certificates)

@app.route('/add', methods=['POST'])
def add_certificate():
    data = request.json
    new_cert = DomainCertificate(
        domain=data['domain'],
        osb=data['osb'],
        ug=data['ug'],
        certificate_owner=data['certificate_owner'],
        expire_date=data['expire_date']
    )
    db.session.add(new_cert)
    db.session.commit()
    return jsonify({"message": "Certificate added successfully"}), 201

@app.route('/update/<int:id>', methods=['PUT'])
def update_certificate(id):
    cert = DomainCertificate.query.get_or_404(id)
    data = request.json
    cert.domain = data['domain']
    cert.osb = data['osb']
    cert.ug = data['ug']
    cert.certificate_owner = data['certificate_owner']
    cert.expire_date = data['expire_date']
    db.session.commit()
    return jsonify({"message": "Certificate updated successfully"})

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_certificate(id):
    cert = DomainCertificate.query.get_or_404(id)
    db.session.delete(cert)
    db.session.commit()
    return jsonify({"message": "Certificate deleted successfully"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

