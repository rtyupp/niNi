"""
3SR Server
سيرفر Flask الرئيسي
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='static', template_folder='.')

# إعدادات
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """فحص حالة السيرفر"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'service': '3SR'
    })

# TODO: إضافة endpoints للمعالجة
# @app.route('/api/interpolate', methods=['POST'])
# @app.route('/api/spoof', methods=['POST'])

if __name__ == '__main__':
    # إنشاء مجلد uploads إذا ما موجود
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("=" * 50)
    print("⚡ 3SR Server is running!")
    print("🌐 Open: http://localhost:8000")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8000, debug=True)
