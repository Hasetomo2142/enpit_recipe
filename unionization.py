from googletrans import Translator #pip3 install googletrans==4.0.0-rc1
import spacy # python3 -m spacy download en_core_web_sm

class Unionization:
    def __init__(self, text):
        self.ingredient = text
        self.translatedIngredient = self.translate(self.ingredient)
        self.formattedIngredient = self.phraseDrawing(self.ingredient)
        
    def translate(self):
      translator = Translator()
      text_ja = self.ingredient
      text_en = translator.translate(text_ja, src='ja', dest='en').text
      return text_en
    
    def phraseDrawing(self):
      # spacyモデルを読み込む
      nlp = spacy.load("en_core_web_sm")

      # 解析対象のテキスト
      text = self.translatedIngredient

      # テキストを解析する
      doc = nlp(text)

      # NOUN（名詞）のみを抽出して出力
      for token in doc:
          if token.pos_ == "NOUN":
            return token.text
