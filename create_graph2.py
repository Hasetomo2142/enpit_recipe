from pyvis.network import Network
import networkx as nx
import pickle
from tqdm import tqdm
from cookpad.recipe_loader import RecipeLoader
import sys
import os


class CreateGraph:
    def __init__(self):
        self.G = nx.Graph()
        self.loaded_recipes = []
        self.edge_weights = {}
        self.nt = Network(notebook=True)
        self.number_of_recipes = 0

    def isRecipeCashAvailable(self, num):
        file_path = os.path.join(
            "app/cash/recipes", "recipes.pickle_" + str(num))

        if os.path.exists(file_path) and os.path.isfile(file_path):
            return True
        else:
            return False

    def isGraphCashAvailable(self, num):
        file_path = os.path.join(
            "app/cash/graphs", "graphs.pickle_" + str(num))

        if os.path.exists(file_path) and os.path.isfile(file_path):
            return True
        else:
            return False

    def load_recipes_from_cookpad(self):
        # 学習するレシピの数を指定し、自身に格納
        self.number_of_recipes = self.get_integer_from_command_line()

        # キャッシュが存在しなければ新規作成
        if not self.isRecipeCashAvailable(self.number_of_recipes):
            # レシピの読み込み
            with RecipeLoader() as rl:
                recipes_gen = rl.load_all_recipes()
                self.loaded_recipes = [next(recipes_gen)
                                    for _ in range(self.number_of_recipes)]

            with open("app/cash/recipes/recipes.pickle_" + str(self.number_of_recipes), mode="wb") as f:
                pickle.dump(self.loaded_recipes, f)

        # キャッシュが存在すればキャッシュから読み込み
        else:
            with open("app/cash/recipes/recipes.pickle_" + str(self.number_of_recipes), mode="rb") as f:
                self.loaded_recipes = pickle.load(f)


    def build_graph(self):
        # キャッシュが存在しなければ新規作成
        if not self.isGraphCashAvailable(self.number_of_recipes):
            # レシピがまだ読み込まれていない場合、読み込む
            if not self.loaded_recipes:
                self.load_recipes_from_cookpad()

            # レシピからグラフを構築
            for recipe in tqdm(self.loaded_recipes, desc="Processing recipes"):
                ingredients = recipe.get_ingredients()

                for ingredient, _ in ingredients:
                    self.G.add_node(ingredient)

                for i in range(len(ingredients) - 1):
                    for j in range(i + 1, len(ingredients)):
                        edge_key = tuple(sorted([ingredients[i][0], ingredients[j][0]]))
                        self.edge_weights[edge_key] = self.edge_weights.get(edge_key, 0) + 1

            # エッジの重みをもとにグラフにエッジを追加
            for (src, dst), weight in self.edge_weights.items():
                self.G.add_edge(src, dst, weight=weight)

            # 新規に作成したグラフをキャッシュとして保存
            with open("app/cash/graphs/graphs.pickle_" + str(self.number_of_recipes), mode="wb") as f:
                pickle.dump((self.G, self.edge_weights), f)

        # キャッシュが存在すればキャッシュから読み込み
        else:
            with open("app/cash/graphs/graphs.pickle_" + str(self.number_of_recipes), mode="rb") as f:
                loaded_data = pickle.load(f)
                # print("DEBUG: Loaded data:", loaded_data)  # ここで読み込んだデータの内容を表示

                if not isinstance(loaded_data, tuple) or len(loaded_data) != 2:
                    raise ValueError("キャッシュファイルのフォーマットが不正です。")

                self.G, self.edge_weights = loaded_data

    def convert_to_pyvis(self):
        self.nt.from_nx(self.G)
        self.nt.show_buttons(True)

        for edge in self.nt.edges:
            src, dst = edge["from"], edge["to"]
            edge_key = tuple(sorted([src, dst]))
            weight = self.edge_weights[edge_key]
            # PyVis uses 'value' attribute to determine thickness
            edge["value"] = weight

    def show_graph(self):
        self.nt.show("graph_" + str(self.number_of_recipes) + ".html")

    @staticmethod
    def get_integer_from_command_line():
        while True:
            try:
                # ユーザーに整数の入力を促す
                number = int(input("整数を入力してください: "))

                # 入力された整数を返す
                return number
            except ValueError:
                # 有効な整数が入力されなかった場合のエラーメッセージ
                print("有効な整数を入力してください。")

# 使い方
# graph = CreateGraph()
# graph.load_recipes_from_cookpad()
# graph.save_recipes_to_pickle()
# graph.build_graph()
# graph.convert_to_pyvis()
# graph.save_graph_to_pickle()
# graph.show_graph()
