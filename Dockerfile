FROM python:3.7
RUN apt-get install libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev
RUN pip install -U pip
RUN pip install --no-binary pillow pillow
RUN apt-get update && apt-get -y install poppler-utils tesseract-ocr
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install pandas
CMD ["python", "main.py"]