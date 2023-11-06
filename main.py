from creategraph import CreateGraph
from graphAnalyzer import GraphAnalyzer
import community  # Louvain method
from networkx.algorithms import community


# オブジェクト生成
graph_builder = CreateGraph()

#recipeの読み込み
graph_builder.load_recipes_from_cookpad()

#graphの作成
graph_builder.build_graph()

# 分析用のオブジェクト生成
analyzer = GraphAnalyzer(graph_builder.G)
# print(analyzer.get_most_common_ingredients())

# 指定したノードの最短パスを取得
# print(analyzer.find_shortest_path_between_ingredients("wasabi", "egg"))
# analyzer.analyze_clusters()

ingredients = ['beef','rice']

# おすすめの食材を出力
recommended = analyzer.recommend_ingredients(ingredients,5)
# analyzer.print_communities_and_top_ingredients()
print(recommended)

# recommended2 = analyzer.recommend_cooccurring_ingredients(ingredients,5)
# print(recommended2)


# #graphの表示
# subgraph.convert_to_pyvis()
# subgraph.show_graph()



