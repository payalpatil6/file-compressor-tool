from flask import Flask, render_template, request, jsonify, send_file
import PyPDF2
import os
import tempfile

app = Flask(__name__, template_folder='templates')

# Serve compressed file for download
app.config['UPLOAD_FOLDER'] = 'uploads'

# Render index.html template on accessing the root URL


@app.route('/')
def index():
    return render_template('index.html')

# Handle file compression


@app.route('/compress', methods=['POST'])
def compress_files():
    try:
        files = request.files.getlist('files[]')
        target_size = int(request.form['targetSize'])
        compressed_files = []
        # Compress PDF files
        for file in files:
            if file.filename.lower().endswith('.pdf'):
                compressed_file = compress_pdf(file, target_size)
                compressed_files.append(compressed_file)
        return jsonify({'message': 'Files compressed successfully.', 'compressed_files': compressed_files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Function to compress PDF files


def compress_pdf(file, target_size):
    try:
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        compressed_file_path = 'compressed_' + file.filename
        output_file_path = os.path.join(temp_dir, compressed_file_path)
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            pdf_writer = PyPDF2.PdfWriter()
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            with open(output_file_path, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)
        return output_file_path
    except Exception as e:
        return str(e)


@app.route('/download/<path:filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
