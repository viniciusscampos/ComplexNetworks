import json
import glob
from statsmodels.distributions.empirical_distribution import ECDF
import matplotlib
matplotlib.use('gtk3agg')
from matplotlib import pyplot as plt
from graph_tool.all import *
import numpy as np

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
			# Calculate graph degrees metrics
			data["degrees"] = self.calculate_degrees(g,graph_name.split(".")[0])
			# Create a file to store the informations						
			with open('{}results/files/{}-results.json'.format(self.project_folder,graph_name.split(".")[0]),'w') as f:
				json.dump(str(data),f)

			
	def calculate_degrees(self,g,name):
		"""Receive a graph as a parameter and return the degree metrics for the graph."""
		if(g.is_directed):
			outDegrees = g.get_out_degrees(g.get_vertices())
			inDegrees = g.get_in_degrees(g.get_vertices())

			outDegreesMetrics = self.get_metrics(outDegrees)
			inDegreesMetrics = self.get_metrics(inDegrees)

			# Generate the ECDF of the out degrees
			ecdf = ECDF(outDegrees)
			x = np.linspace(min(outDegrees),max(outDegrees))
			y = ecdf(x)
			plt.step(x,y)
			plt.xlabel("empirical cdf outDegree")
			plt.savefig('{}results/images/{}-{}-ecdf.png'.format(self.project_folder,name,"outDegrees"))

			# Generate the ECDF of the in degrees
			ecdf = ECDF(inDegrees)
			x = np.linspace(min(inDegrees),max(inDegrees))
			y = ecdf(x)
			plt.step(x,y)
			plt.xlabel("empirical cdf inDegree")
			plt.savefig('{}results/images/{}-{}-ecdf.png'.format(self.project_folder,name,"inDegrees"))

			return {"outDegreesMetrics": outDegreesMetrics, "inDegreesMetrics": inDegreesMetrics}
		else:
			outDegrees = g.get_out_degrees(g.get_vertices())
			outDegreesMetrics = self.get_metrics(outDegrees)

			# Generate the ECDF of the out degrees
			ecdf = ECDF(outDegrees)
			x = np.linspace(min(outDegrees),max(outDegrees))
			y = ecdf(x)
			plt.step(x,y)
			plt.xlabel("empirical cdf outDegree")
			plt.savefig('{}results/images/{}-{}-ecdf.png'.format(self.project_folder,name,"outDegrees"))


			return {"outDegreesMetrics": outDegreesMetrics}
		
	def get_metrics(self,a):
		"""Receives an array as parameters and return an dictionary containing their min,max,mean and standard deviation metrics. """
		return {"min": np.amin(a),"max":np.amax(a),"mean": np.mean(a), "standard-deviation": np.std(a) }


g = graph()
g.save_graphs_metrics_file()
