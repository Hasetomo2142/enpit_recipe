import sys
from creategraph import CreateGraph
from graphAnalyzer import GraphAnalyzer

# コマンドライン引数を解析
if len(sys.argv) != 3:
    print("Usage: python script.py ingredients,number_of_recommendations")
    sys.exit(1)

# コマンドライン引数からingredientsと数を取得
ingredients_list = sys.argv[1].split(',')
number_of_recommendations = int(sys.argv[2])

# オブジェクト生成
graph_builder = CreateGraph()

# recipeの読み込み
graph_builder.load_recipes_from_cookpad()

# graphの作成
graph_builder.build_graph()

# 分析用のオブジェクト生成
analyzer = GraphAnalyzer(graph_builder.G)

# おすすめの食材を出力
recommended = analyzer.recommend_ingredients(ingredients_list, number_of_recommendations)

# 入力されたingredientsとおすすめの食材を結合
combined_list = ingredients_list + recommended

# 結合したリストを表示
print(combined_list)

# スクリプト実行時には次のようにコマンドラインから実行します:
# python script.py beef,rice 10
