import networkx as nx
from collections import Counter, defaultdict
from networkx.algorithms import community
import community as louvain_community  # Louvain method のインポート
import networkx.algorithms.community
from tqdm import tqdm
import community as community_louvain
import itertools


class GraphAnalyzer:
    def __init__(self, graph):
        self.G = graph
        
        
    def find_common_neighbors(self, ingredient1, ingredient2):
        # Check if both ingredients are in the graph
        if ingredient1 not in self.G or ingredient2 not in self.G:
            return []
        # Find the common neighbors of the two ingredients
        neighbors1 = set(self.G[ingredient1])
        neighbors2 = set(self.G[ingredient2])
        return list(neighbors1 & neighbors2)  # Intersection gives the common neighbors


    def get_most_common_ingredients(self, top_n=10):
        """
        グラフのノードの中から、最も多くのエッジを持つ材料を返す。
        """
        degree_sequence = sorted(
            [(node, degree) for node, degree in self.G.degree()], key=lambda x: x[1], reverse=True)
        return degree_sequence[:top_n]

    def find_shortest_path_between_ingredients(self, ingredient1, ingredient2):
        """
        2つの材料間の最短パスを見つける。
        """
        if ingredient1 not in self.G or ingredient2 not in self.G:
            print(f"{ingredient1} または {ingredient2} はグラフに存在しません。")
            return

        try:
            path = nx.shortest_path(
                self.G, source=ingredient1, target=ingredient2)
            return path
        except nx.NetworkXNoPath:
            print(f"{ingredient1} と {ingredient2} の間にはパスが存在しません。")
            return

    def get_clusters(self):
        """
        グラフ内のクラスタ（連結成分）を返す。
        """
        return [list(cluster) for cluster in nx.connected_components(self.G)]

    def analyze_clusters(self):
        """
        グラフ内のクラスタを分析し、それぞれのクラスタのサイズと最も一般的な材料を表示する。
        """
        clusters = self.get_clusters()
        for i, cluster in enumerate(clusters):
            subgraph = self.G.subgraph(cluster)
            common_ingredients = self.get_most_common_ingredients_within_subgraph(
                subgraph)
            print(f"Cluster {i + 1}:")
            print(f"Size: {len(cluster)}")
            print(f"Most common ingredients: {common_ingredients}")
            print("-" * 50)

    def get_most_common_ingredients_within_subgraph(self, subgraph, top_n=5):
        """
        サブグラフ内の最も一般的な材料を返す。
        """
        degree_sequence = sorted([(node, degree) for node, degree in subgraph.degree(
        )], key=lambda x: x[1], reverse=True)
        return degree_sequence[:top_n]

    def extract_subgraph_with_elements(self, ingredients):
        """
        指定された材料を含む部分グラフを抽出して返す。
        """
        nodes_to_include = set()

        for ingredient in ingredients:
            if ingredient in self.G:
                nodes_to_include.add(ingredient)
                for neighbor in self.G.neighbors(ingredient):
                    nodes_to_include.add(neighbor)

        subgraph = self.G.subgraph(nodes_to_include)
        return subgraph

    def recommend_ingredients(self, ingredients, num_recommendations):
        # 各食材の隣接ノードと、それらとのエッジの重さを取得
        adjacent_nodes_weights = {}

        # コミュニティの検出（和風、洋風などでカテゴライズ）
        community_map = louvain_community.best_partition(
            self.G)  # コミュニティIDに基づいてノードをマッピング

        # 与えられた食材が所属するコミュニティを特定
        ingredient_communities = {ingredient: community_map[ingredient]
                                  for ingredient in ingredients if ingredient in community_map}
        target_communities = set(ingredient_communities.values())

        for ingredient in ingredients:
            if ingredient in self.G:
                for neighbor in self.G.neighbors(ingredient):
                    # ここでコミュニティの情報を利用して推薦をフィルタリング
                    if neighbor in community_map and community_map[neighbor] not in target_communities:
                        continue  # この隣接ノードはターゲットのコミュニティに属していないのでスキップ

                    weight = self.G[ingredient][neighbor].get(
                        'weight', 1)  # 重さが設定されていないエッジは重さを1とする
                    if neighbor in adjacent_nodes_weights:
                        adjacent_nodes_weights[neighbor] += weight
                    else:
                        adjacent_nodes_weights[neighbor] = weight

        # 入力された食材を除外
        for ingredient in ingredients:
            if ingredient in adjacent_nodes_weights:
                del adjacent_nodes_weights[ingredient]

        # グラフの中心性を取得（より一般的な食材が候補に上がるように補正）
        centrality = nx.degree_centrality(self.G)
        for node, weight in adjacent_nodes_weights.items():
            # 中心性の値で重さを補正する
            adjusted_weight = weight * centrality.get(node, 1)
            adjacent_nodes_weights[node] = adjusted_weight

        # 最も関連の深い食材を返す（エッジの重さの合計に基づいて）
        recommended = sorted(adjacent_nodes_weights.items(),
                             key=lambda x: x[1], reverse=True)
        return [item[0] for item in recommended[:num_recommendations]]

    def detect_communities(self):
        """
        グラフ内のコミュニティを検出し、ノードのリストとして返します。
        """
        # Louvain法を用いたコミュニティ検出
        communities_generator = community.greedy_modularity_communities(self.G)

        # 各コミュニティを番号付きで返す
        return {idx: list(community) for idx, community in enumerate(communities_generator)}


    def print_communities_and_top_ingredients(self, top_n=5):
        """
        コミュニティの一覧を出力し、それぞれのコミュニティで最も一般的な材料を上位から表示する。
        """
        # コミュニティの検出
        communities = self.detect_communities()

        # コミュニティとそのトップ食材の出力
        for idx, community in communities.items():
            print(f"Community {idx + 1}: Size {len(community)}")
            # そのコミュニティのサブグラフを作成
            subgraph = self.G.subgraph(community)
            # サブグラフから上位N個の最も一般的な食材を取得
            top_ingredients = self.get_most_common_ingredients_within_subgraph(subgraph, top_n=top_n)
            top_ingredients_names = [ingredient for ingredient, _ in top_ingredients]
            print(f"Top {top_n} ingredients: {top_ingredients_names}")
            print("-" * 50)
            
            

    def recommend_cooccurring_ingredients(self, ingredients, num_recommendations):
        # 入力のバリデーション
        if not isinstance(ingredients, list) or not ingredients:
            raise ValueError("食材は非空のリストでなければなりません。")

        # 食材間の共通の隣接ノードと重みを格納する辞書
        adjacent_nodes_weights = defaultdict(int)
        common_neighbors_found = False

        # コミュニティマップと中心性を計算
        community_map = community_louvain.best_partition(self.G)
        centrality = nx.degree_centrality(self.G)

        # 与えられた食材のコミュニティを特定
        ingredient_communities = {ingredient: community_map[ingredient]
                                for ingredient in ingredients if ingredient in community_map}
        target_communities = set(ingredient_communities.values())

        # 食材リストのすべての組み合わせを繰り返す
        for pair in itertools.combinations(ingredients, 2):
            common_neighbors = set(self.G.neighbors(pair[0])).intersection(set(self.G.neighbors(pair[1])))
            if common_neighbors:
                common_neighbors_found = True
                for neighbor in common_neighbors:
                    if community_map[neighbor] in target_communities:
                        weight = self.G[pair[0]][neighbor].get('weight', 1) + self.G[pair[1]][neighbor].get('weight', 1)
                        adjusted_weight = weight * centrality[neighbor]
                        adjacent_nodes_weights[neighbor] += adjusted_weight

        # 共通の隣接ノードが見つからない場合は中心性とコミュニティのみで評価
        if not common_neighbors_found:
            for ingredient in ingredients:
                for neighbor in self.G.neighbors(ingredient):
                    if neighbor in ingredients or community_map[neighbor] not in target_communities:
                        continue
                    weight = self.G[ingredient][neighbor].get('weight', 1)
                    adjusted_weight = weight * centrality[neighbor]
                    adjacent_nodes_weights[neighbor] += adjusted_weight

        # 推薦から入力された食材を除外
        for ingredient in ingredients:
            adjacent_nodes_weights.pop(ingredient, None)

        # エッジの重さの合計に基づいて関連の深い食材をソート
        recommended = sorted(adjacent_nodes_weights.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in recommended[:num_recommendations]]
