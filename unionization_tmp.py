from googletrans import Translator
import MeCab
from cookpad.recipe_loader import RecipeLoader

class Unionization:
    def translate_given_ingredients(self, ingredients):
        translated_ingredients_list = []  # 翻訳された材料を格納するリスト
        for ingredient, quantity in ingredients:
            cleaned_ingredient = self.clean_ingredient(ingredient)
            if cleaned_ingredient:
                translated_ingredient_name = self.process_ingredient(cleaned_ingredient)
                # 翻訳された材料の名前と元の量をタプルとしてリストに追加
                translated_ingredients_list.append((translated_ingredient_name, quantity))
        return translated_ingredients_list

    def clean_ingredient(self, ingredient): #カッコ以下を消す
        for char in ["（", "("]:
            if char in ingredient:
                return ingredient.split(char)[0].strip()
        return ingredient

    def process_ingredient(self, ingredient): #Mecabと翻訳処理
        parsed_text = self.mecab_parse(ingredient)
        translated_text = self.translate(parsed_text)
        translated_text_lower = translated_text.lower().replace('\u200b', '')  # 英語の出力をすべて小文字にし、ゼロ幅スペースを削除
        return translated_text_lower

    def mecab_parse(self, text): #Mecab
        mc = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
        mc.parse('')
        node = mc.parse(text)
        nouns = []

        for line in node.split('\n'):
            if "名詞" in line:
                noun = line.split('\t')[0]
                if noun:
                    nouns.append(noun)

        return " ".join(nouns)

    def translate(self, text): #翻訳
        translator = Translator()
        text_ja = text
        try:
            translation_result = translator.translate(text_ja, src='ja', dest='en')
            if translation_result:
                text_en = translation_result.text
            else:
                text_en = "Translation not available"  # 翻訳結果がない場合に代替のメッセージを表示
        except Exception as e:
            print(f"Translation error: {e}")
            text_en = "Translation error"  # エラーが発生した場合に代替のメッセージを表示
        return text_en
