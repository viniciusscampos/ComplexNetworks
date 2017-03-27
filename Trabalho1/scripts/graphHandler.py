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
			name = graph_name.split(".")[0]
			# Calculate graph degrees metrics
			data["degrees"] = self.calculate_degrees(g,name)
			# Calculate graph page rank metrics
			#data["page rank"] = self.calculate_page_rank(g,name)
			# Calculate graph components
			#data["page rank"] = self.calculate_page_rank(g,name)
			data["components"] = self.calculate_components(g,name)
			# Create a file to store the informations						
			with open('{}results/files/{}-results.json'.format(self.project_folder,graph_name.split(".")[0]),'w') as f:
				json.dump(str(data),f)

			
	def calculate_degrees(self,g,name):
		"""Receive a graph and a name as a parameter and return the degree metrics for the graph."""
		if(g.is_directed):
			outDegrees = g.get_out_degrees(g.get_vertices())
			inDegrees = g.get_in_degrees(g.get_vertices())

			outDegreesMetrics = self.get_metrics(outDegrees)
			inDegreesMetrics = self.get_metrics(inDegrees)

			# Generate the ECDF of the out degrees
			self.plot_ecdf(outDegrees,name,"outDegrees")
			
			# Generate the ECDF of the in degrees
			self.plot_ecdf(inDegrees,name,"inDegrees")			

			return {"outDegreesMetrics": outDegreesMetrics, "inDegreesMetrics": inDegreesMetrics}
		else:
			outDegrees = g.get_out_degrees(g.get_vertices())
			outDegreesMetrics = self.get_metrics(outDegrees)

			# Generate the ECDF of the out degrees
			self.plot_ecdf(outDegrees,name,"outDegrees")

			return {"outDegreesMetrics": outDegreesMetrics}

	def calculate_page_rank(self,g,name):
		"""Receive a graph and a name as a parameter and return the page rank metrics for the graph."""
		page_rank = pagerank(g).a
		page_rank_metrics = self.get_metrics(page_rank)
		# Generate the ECDF of the page rank
		self.plot_ecdf(page_rank,name,"page-rank")
		return page_rank_metrics

	def calculate_components(self,g,name):
		# Get an array containing the label of each component that the vertex i belongs.
		components = label_components(g)[0].a
		# Construct a dictionary mapping a component with it size.	
		data = {}
		for c in components:
			if c not in data:
				data[c] = 1
				continue
			elif c in data:
				data[c] = data[c] + 1
		components_metrics = self.get_metrics(data.values())
		self.plot_ecdf(components,name,"components")
		return components_metrics
		
	def get_metrics(self,a):
		"""Receives an array as parameters and return an dictionary containing their min,max,mean and standard deviation metrics. """
		return {"min": np.amin(a),"max":np.amax(a),"mean": np.mean(a), "standard-deviation": np.std(a) }

	def plot_ecdf(self,a,name,p):
		"""Create and save the respectively ecdf to an given array with given name."""
		ecdf = ECDF(a)
		x = np.linspace(min(a),max(a))
		y = ecdf(x)
		plt.step(x,y)
		plt.xlabel("empirical cdf {}".format(p))
		plt.savefig('{}results/images/{}-{}-ecdf.png'.format(self.project_folder,name,p))


g = graph()
g.save_graphs_metrics_file()
