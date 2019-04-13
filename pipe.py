import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path, convert_from_bytes
import unicodedata

class Pipe:

    def preprocess(self, sent):
        sent = re.sub('[!@$#]', '', sent)
        sent = re.sub(
            r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', sent)
        sent = re.sub(r"com\S+", "", sent)
        sent = re.sub('\s+',' ',sent)
        sent = sent.strip()
        sent = unicodedata.normalize("NFKD", sent)
        return sent

    def convert(self, filename):
        counter = 0
        textl = []
        pages = convert_from_bytes(filename.read(), 500)

        for page in pages:
            page.save('out'+str(counter)+'.jpg', 'JPEG')
            counter +=1

        for i in range(counter):
            im = Image.open("out"+str(i)+".jpg") # the second one 
            im = im.filter(ImageFilter.MedianFilter())
            enhancer = ImageEnhance.Contrast(im)
            im = enhancer.enhance(2)
            im = im.convert('1')
            im.save('temp2.jpg')
            text = pytesseract.image_to_string(Image.open('temp2.jpg'))
            textl.append(text)
        output = self.preprocess(textl[0])
        return output