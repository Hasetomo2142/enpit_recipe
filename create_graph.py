from pyvis.network import Network
import matplotlib.pyplot as plt
import japanize_matplotlib
import networkx as nx
import matplotlib
import pickle
from tqdm import tqdm
from unionization import Unionization
G = nx.Graph()

with open("sample.pickle", mode="rb") as f:
    loaded_recipes = pickle.load(f)

edge_weights = {}  # エッジの重みを管理する辞書

for recipe in tqdm(loaded_recipes, desc="Processing recipes"):
    ingredients = recipe.get_ingredients()

    for ingredient, _ in ingredients:
        G.add_node(ingredient)

    for i in range(len(ingredients)-1):
        for j in range(i+1, len(ingredients)):
            edge_key = tuple(sorted([ingredients[i][0], ingredients[j][0]]))
            edge_weights[edge_key] = edge_weights.get(edge_key, 0) + 1

for (src, dst), weight in edge_weights.items():
    G.add_edge(src, dst, weight=weight)

# NetworkXのグラフをPyVisのNetworkに変換
nt = Network(notebook=True)
nt.from_nx(G)
nt.show_buttons(True)

# グラフの保存
with open("sample.graph", mode="wb") as f:
    pickle.dump(G, f)

# エッジの重みに基づいてエッジの太さを調整
for edge in nt.edges:
    src, dst = edge["from"], edge["to"]
    edge_key = tuple(sorted([src, dst]))
    weight = edge_weights[edge_key]
    edge["value"] = weight  # PyVis uses 'value' attribute to determine thickness

# グラフの保存と表示
nt.show("graph.html")
