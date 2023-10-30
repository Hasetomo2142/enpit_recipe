from cookpad.recipe_loader import RecipeLoader
import matplotlib.pyplot as plt
import japanize_matplotlib
import networkx as nx
import matplotlib


# 無向グラフの作成
G = nx.Graph()

index = 0


with RecipeLoader() as rl:
    recipes = rl.load_all_recipes()

    for recipe in recipes:
        if index >= 20:
            break
        ingredients = recipe.get_ingredients()
        for ingredient, quantity in ingredients:
            # print("{} : {}".format(ingredient, quantity))
            print(index)

            # ingredientがgraphに存在しない場合にのみノードを追加
            if ingredient not in G.nodes():
                G.add_node(ingredient)

        index += 1

        # 材料を結ぶエッジを追加
        for i in range(len(ingredients)-1):
            for j in range(i+1, len(ingredients)):
                # もしエッジが存在すれば
                if G.has_edge(ingredients[i][0], ingredients[j][0]):
                    # 重みを追加
                    G[ingredients[i][0]][ingredients[j][0]]['weight'] += 1
                else:
                    # エッジを追加
                    G.add_edge(ingredients[i][0], ingredients[j][0], weight=1)

# Draw the graph
pos = nx.spring_layout(G, k=1.5, iterations=100)  # k値を1.5に調整
nx.draw_networkx_nodes(G, pos, node_size=50, node_color='lightblue', alpha=0.8)  # ノードサイズを小さく
nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.5, edge_color='gray')  # エッジの太さを調整
nx.draw_networkx_labels(G, pos, font_size=6, font_family='IPAexGothic')  # フォントサイズを小さく
plt.axis('off')
plt.savefig('graph6.png')
