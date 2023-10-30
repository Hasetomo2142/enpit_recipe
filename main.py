from create_graph2 import CreateGraph

graph = CreateGraph()
graph.load_recipes_from_cookpad()
graph.build_graph()
graph.convert_to_pyvis()
graph.show_graph()
