from pyvis.network import Network
import networkx as nx
import pickle
from tqdm import tqdm
from cookpad.recipe_loader import RecipeLoader
import os
from unionization_tmp import Unionization

class CreateGraph:
    BASE_PATH = "/home/group1/app/cash"  # 絶対パスの基準点
    
    def __init__(self):
        # グラフの初期化
        self.G = nx.Graph()
        # 読み込んだレシピのリスト
        self.loaded_recipes = []
        # グラフのエッジの重みを保持する辞書
        self.edge_weights = {}
        # PyVisのネットワークの初期化
        self.nt = Network(notebook=True)
        # 読み込むレシピの数
        self.number_of_recipes = 0

    def isRecipeCashAvailable(self, num):
        # 指定した数のレシピに関連するキャッシュファイルの存在を確認
        file_path = os.path.join(self.BASE_PATH, "recipes", f"recipes.pickle_{num}")
        return os.path.exists(file_path)

    def isGraphCashAvailable(self, num):
        # 指定した数のレシピに関連するグラフのキャッシュファイルの存在を確認
        file_path = os.path.join(self.BASE_PATH, "graphs", f"graphs.pickle_{num}")
        return os.path.exists(file_path)

    def ensure_directory_exists(self, dir_path):
        # 指定したディレクトリが存在しない場合、ディレクトリを作成
        full_dir_path = os.path.join(self.BASE_PATH, dir_path)
        if not os.path.exists(full_dir_path):
            os.makedirs(full_dir_path)

    def load_recipes_from_cookpad(self):
        # コマンドラインから読み込むレシピの数を取得
        # self.number_of_recipes = self.get_integer_from_command_line()
        self.number_of_recipes = 10000

        # レシピのキャッシュディレクトリのパスを作成し、存在しない場合はディレクトリを作成
        recipe_dir = os.path.join(self.BASE_PATH, "recipes")
        self.ensure_directory_exists(recipe_dir)

        # レシピのキャッシュファイルのパスを作成
        recipe_file_path = os.path.join(recipe_dir, f"recipes.pickle_{self.number_of_recipes}")

        # キャッシュが存在しない場合、レシピを読み込みとキャッシュの保存を行う
        if not self.isRecipeCashAvailable(self.number_of_recipes):
            with RecipeLoader() as rl:
                recipes_gen = rl.load_all_recipes()
                self.loaded_recipes = [next(recipes_gen) for _ in range(self.number_of_recipes)]

            with open(recipe_file_path, mode="wb") as f:
                pickle.dump(self.loaded_recipes, f)
        # キャッシュが存在する場合、キャッシュからレシピを読み込む
        else:
            with open(recipe_file_path, mode="rb") as f:
                self.loaded_recipes = pickle.load(f)

    def build_graph(self):
        # グラフのキャッシュディレクトリのパスを作成し、存在しない場合はディレクトリを作成
        graph_dir = os.path.join(self.BASE_PATH, "graphs")
        self.ensure_directory_exists(graph_dir)

        # グラフのキャッシュファイルのパスを作成
        graph_file_path = os.path.join(graph_dir, f"graphs.pickle_{self.number_of_recipes}")

        # キャッシュが存在しない場合、レシピからグラフを構築し、キャッシュとして保存
        if not self.isGraphCashAvailable(self.number_of_recipes):
            if not self.loaded_recipes:
                self.load_recipes_from_cookpad()

            for recipe in tqdm(self.loaded_recipes, desc="Processing recipes"):
                ingredients = recipe.get_ingredients()
                
                # Unionization インスタンスの作成
                unionization = Unionization()
                
                # 材料を英語に翻訳した上で統一化
                ingredients = unionization.translate_given_ingredients(ingredients)
                
                # print(ingredients)
                
                for ingredient, _ in ingredients:
                    self.G.add_node(ingredient)

                for i in range(len(ingredients) - 1):
                    for j in range(i + 1, len(ingredients)):
                        edge_key = tuple(sorted([ingredients[i][0], ingredients[j][0]]))
                        self.edge_weights[edge_key] = self.edge_weights.get(edge_key, 0) + 1

            for (src, dst), weight in self.edge_weights.items():
                self.G.add_edge(src, dst, weight=weight)

            with open(graph_file_path, mode="wb") as f:
                pickle.dump((self.G, self.edge_weights), f)
        # キャッシュが存在する場合、キャッシュからグラフを読み込む
        else:
            with open(graph_file_path, mode="rb") as f:
                loaded_data = pickle.load(f)

                if not isinstance(loaded_data, tuple) or len(loaded_data) != 2:
                    raise ValueError("キャッシュファイルのフォーマットが不正です。")

                self.G, self.edge_weights = loaded_data

    def convert_to_pyvis(self):
        # NetworkXのグラフをPyVisのネットワークに変換
        self.nt.from_nx(self.G)
        self.nt.show_buttons(True)

        for edge in self.nt.edges:
            src, dst = edge["from"], edge["to"]
            edge_key = tuple(sorted([src, dst]))
            weight = self.edge_weights.get(edge_key, 0)
            edge["value"] = weight

    def show_graph(self):
        # PyVisのネットワークをHTMLファイルとして表示
        self.nt.show(f"graph_{self.number_of_recipes}.html")

    @staticmethod
    def get_integer_from_command_line():
        # コマンドラインから整数を取得
        while True:
            try:
                number = int(input("学習させたいレシピ数を整数を入力してください: "))
                return number
            except ValueError:
                print("有効な整数を入力してください。")
