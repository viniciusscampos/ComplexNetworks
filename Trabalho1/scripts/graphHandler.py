import json
import glob
from graph_tool.all import *
from numpy import *

class graph:
	def __init__(self):
		self.configuration = json.loads(open('../config/config.json').read())
		self.project_folder = self.configuration["project_folder"]
		self.datasets = self.configuration["datasets"]

	def file_converter(self):
		for file_name in self.datasets:
			file = open("{}datasets/{}.txt".format(self.project_folder,file_name), "read")		
			g = Graph()
			v_id = g.new_vertex_property("int")
			for line in file:
				if "# Nodes:" in line:
					total_nodes = int(line.split(" ")[2])
					g.add_vertex(total_nodes)
				if not line.startswith("#"):
					nodes = line.split("	")
					v1 = int(nodes[0]) - 1 
					v2 = int(nodes[1]) - 1
					g.add_edge(v1,v2)
			g.save("{}datasets/converted/{}.gt".format(self.project_folder,file_name))


	def save_graphs_metrics_file(self):		
		graph_files = glob.glob("{}/datasets/converted/*.gt".format(self.project_folder))
		for graph_absolute_path in graph_files:
			graph_name = graph_absolute_path.split("/")[-1]
			g = load_graph(graph_absolute_path)						
			data = {"name": graph_name, "isDirected": g.is_directed()}
			# Calculate the strongly connected components
			#l = gt.label_largest_component(g)
			#u = gt.GraphView(g,vfilt=l)
			# Calculate graph degrees metrics
			data["degrees"] = self.calculate_degrees(g)			
			# Create a file to store the informations						
			with open('{}results/files/{}-results.json'.format(self.project_folder,graph_name.split(".")[0]),'w') as f:
				json.dump(str(data),f)

			
	def calculate_degrees(self,g):
		"""Receive a graph as a parameter and return the degree metrics for the graph."""
		if(g.is_directed):
			outDegrees = g.get_out_degrees(g.get_vertices())
			inDegrees = g.get_in_degrees(g.get_vertices())

			outDegreesMetrics = self.get_metrics(outDegrees)
			inDegreesMetrics = self.get_metrics(inDegrees)
			return {"outDegreesMetrics": outDegreesMetrics, "inDegreesMetrics": inDegreesMetrics}
		else:
			outDegrees = g.get_out_degrees(g.get_vertices())
			outDegreesMetrics = self.get_metrics(outDegrees)
			return {"outDegreesMetrics": outDegreesMetrics}

	def get_metrics(self,a):
		"""Receives an array as parameters and return an dictionary containing their min,max,mean and standard deviation metrics. """
		return {"min": amin(a),"max":amax(a),"mean": mean(a), "standard-deviation": std(a) }


g = graph()
g.save_graphs_metrics_file()
