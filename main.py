from app import app
from flask import Flask, flash, request, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename
import PyPDF2

ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('upload.html')


@app.route('/<path:path>')
def send_image(path):
	return send_from_directory('static', path)


@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			text = summarize(file)
			return text
			#flash('File successfully uploaded')
			#return redirect('/')
		else:
			flash('Upload not possible')
			return redirect('/summary')

def summarize(PDFfile):
    #return 'HI'
    pdfReader = PyPDF2.PdfFileReader(PDFfile)
    # ab hier TODO
    pages = pdfReader.getNumPages()

    whole_text = ''
    for i in range(pages):
        pageobj = pdfReader.getPage(i)
        text = pageobj.extractText()
        array = text.splitlines()
        newstring = ''
        for i in array:
            newstring += i
        whole_text += newstring
    return whole_text

if __name__ == "__main__":
    app.run(host='0.0.0.0')