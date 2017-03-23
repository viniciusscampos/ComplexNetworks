import json
from graph_tool.all import *

class graph:
	def __init__(self):
		self.configuration = json.loads(open('../config/config.json').read())

	def calculate_metrics(self):
		"""Get the graphs paths from the configuration file and then generate a text file
		 containing it's calculated metrics."""
		graph_names = self.configuration["graph_names"]
		for graph_name in graph_names:
			g = load_graph(graph_name)
			graph_draw(g, vertex_text=g.vertex_index, vertex_font_size=11,
				output_size=(500,500), output="../results/images/polblogs.png")


g = graph()
g.calculate_metrics()