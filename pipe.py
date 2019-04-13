import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path, convert_from_bytes
import unicodedata
import pandas as pd
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor
import genanki
import requests
import json

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

    def summarization(self, input):
        df = pd.DataFrame(columns=['sentence','page'])
        for index,key in enumerate(input):
            # Object of automatic summarization.
            auto_abstractor = AutoAbstractor()
            
            doc = key
            # Set tokenizer.
            auto_abstractor.tokenizable_doc = SimpleTokenizer()
            # Set delimiter for making a list of sentence.
            auto_abstractor.delimiter_list = ["."]
            # Object of abstracting and filtering document.
            abstractable_doc = TopNRankAbstractor()
            # Summarize document.
            result_dict = auto_abstractor.summarize(doc, abstractable_doc)

            

            df_new = pd.DataFrame(columns=['sentence','page'])

            sentences= []
            scores = []
            page = []


            for i,e in enumerate(result_dict['scoring_data']):
                sentences.append(result_dict['summarize_result'][i])
                scores.append(e[1])
                page.append(key)

            df_new['sentence']=[' '.join(sentences)]
            #df_new['score']= scores
            df_new['page'] = [index]
            df = df.append(df_new,ignore_index=True)
        return df

    def generateQuestions(self, df):
        questions = []
        my_deck = genanki.Deck(
        2059400110,
        'Summaries')

        my_model = genanki.Model(
        1607392319,
        'Simple Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ])
        url = "https://gs4ossx7yj.execute-api.us-east-1.amazonaws.com/dev/text"

        #payload = "Samsung is a South Korean multinational conglomerate headquartered in Samsung Town, Seoul.[1] It comprises numerous affiliated businesses,[1] most of them united under the Samsung brand, and is the largest South Korean chaebol (business conglomerate).Samsung was founded by Lee Byung-chul in 1938 as a trading company. Over the next three decades, the group diversified into areas including food processing, textiles, insurance, securities, and retail. Samsung entered the electronics industry in the late 1960s and the construction and shipbuilding industries in the mid-1970s; these areas would drive its subsequent growth. Following Lee's death in 1987, Samsung was separated into four business groups – Samsung Group, Shinsegae Group, CJ Group and Hansol Group. Since 1990, Samsung has increasingly globalised its activities and electronics; in particular, its mobile phones and semiconductors have become its most important source of income. As of 2017, Samsung has the 6th highest global brand value.[5] Notable Samsung industrial affiliates include Samsung Electronics (the world's largest information technology company, consumer electronics maker and chipmaker measured by 2017 revenues),[6][7] Samsung Heavy Industries (the world's 2nd largest shipbuilder measured by 2010 revenues),[8] and Samsung Engineering and Samsung C&T (respectively the world's 13th and 36th largest construction companies).[9] Other notable subsidiaries include Samsung Life Insurance (the world's 14th largest life insurance company),[10] Samsung Everland (operator of Everland Resort, the oldest theme park in South Korea)[11] and Cheil Worldwide (the world's 15th largest advertising agency measured by 2012 revenues).[12][13] Samsung has a powerful influence on South Korea's economic development, politics, media and culture and has been a major driving force behind the Miracle on the Han River.[14][15] Its affiliate companies produce around a fifth of South Korea's total exports.[16] Samsung's revenue was equal to 17% of South Korea's $1,082 billion GDP.[17]"
        headers = {
            'Accept': "/",
            'Referer': "http://deepquiz.com.s3-website-us-east-1.amazonaws.com/",
            'Origin': "http://deepquiz.com.s3-website-us-east-1.amazonaws.com",
            'Content-Type': "text/plain"
            }

        for index, row in df.iterrows():
            payload = row['sentence']
            response = requests.request("POST", url, data=payload.encode('utf-8'), headers=headers)
            d = json.loads(response.text)
            questions.append(d)

        for index, e in enumerate(questions):
            if e:
                question = '<p><h2>'
                answer = '<p><h2>'
                for i in e:
                    question += i['QuestionPrompt']+'</p><p>'
                    answer += str(i['CorrectAnswer'])+'</p><p>'
                
                    my_note = genanki.Note(
                    model=my_model,
                    fields=[question+'</h2></p>','<h2><p>'+df.sentence[index]+'</h2></p>'+"<p><h2>Answer: </p></h2>"+str(answer)+'</h2></p>'])
                    my_deck.add_note(my_note)
        genanki.Package(my_deck).write_to_file('output.apkg')

        length = 0
        for l in questions:
            length += len(l)
        return length

    def convert(self, filename):
        textl = []
        pages = convert_from_bytes(filename.read(), 500)

        for page in pages:
            page = page.filter(ImageFilter.MedianFilter())
            enhancer = ImageEnhance.Contrast(page)
            page = enhancer.enhance(2)
            page = page.convert('1')
            text = pytesseract.image_to_string(page)
            textl.append(text)

        # delete pages
        del pages
        
        text = []
        for e in textl:
            text.append(self.preprocess(e))
        df_summary = self.summarization(text)
        n_questions = self.generateQuestions(df_summary)
        del text
        del df_summary
        return n_questions