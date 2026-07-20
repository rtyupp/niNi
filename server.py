from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import subprocess
import uuid

app = Flask(__name__, static_folder='static', template_folder='.')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# إنشاء مجلد الرفع إذا لم يكن موجوداً
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/process/<task_type>', methods=['POST'])
def process_video(task_type):
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'لم يتم رفع أي ملف'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'اسم الملف فارغ'}), 400

    # حفظ الملف المؤقت
    input_filename = f"input_{uuid.uuid4().hex}.mp4"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    file.save(input_path)

    output_filename = f"output_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    try:
        if task_type == 'interpolate':
            target_fps = request.form.get('target_fps', '60')
            quality = request.form.get('quality', 'high')
            
            # إعداد فلتر minterpolate حسب الجودة
            if quality == 'high':
                filter_cmd = f"minterpolate='fps={target_fps}:mi_mode=mci:mc_mode=aobmc'"
            else:
                filter_cmd = f"fps=fps={target_fps}" # تكرار إطارات (أسرع)

            cmd = [
                'ffmpeg', '-y', '-i', input_path,
                '-vf', filter_cmd,
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                '-c:a', 'copy', output_path
            ]

        elif task_type == 'spoof':
            target_fps = request.form.get('target_fps', '30')
            method = request.form.get('method', 'reencode')
            
            if method == 'reencode':
                cmd = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-r', str(target_fps),
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                    '-c:a', 'copy', output_path
                ]
            else:
                # تغيير البيانات الوصفية فقط (سريع جداً لكن بعض المنصات قد تكتشفه)
                cmd = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-c', 'copy', '-r', str(target_fps), output_path
                ]

        # تنفيذ الأمر
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({'success': False, 'error': f'فشل FFmpeg: {result.stderr}'}), 500

        # تنظيف الملف الأصلي لتوفير المساحة
        os.remove(input_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'message': 'تمت المعالجة بنجاح!'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("⚡ 3SR Server is running!")
    print("🌐 افتح المتصفح على: http://localhost:8000")
    print("=" * 50)
    app.run(host='127.0.0.1', port=8000, debug=False)
