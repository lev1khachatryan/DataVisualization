# Load dash components
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
from dash.dependencies import Input, Output

# Loading numpy and pandas libraries
import numpy as np
import pandas as pd

# Model deployment
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Data Visualization with plotly
import plotly.graph_objs as go
import plotly.figure_factory as ff

# graph visualization
from bs4 import BeautifulSoup
import requests
from operator import itemgetter
import networkx as nx


# Read the graph from disk.
G = nx.read_graphml("movies.graphml")

size_in = list(G.in_degree())
size_in = [j for i,j in size_in]

size_out = list(G.out_degree())
size_out = [j for i,j in size_out]

size_ = list(G.degree())
size_ = [j for i,j in size_]


def get_graph(G, size_, title_ ):

	pos=nx.circular_layout(G, scale=3)

	Xn=[pos[k][0] for k in list(pos.keys())]
	Yn=[pos[k][1] for k in list(pos.keys())]

	trace_nodes=dict(type='scatter',
	                 x=Xn, 
	                 y=Yn,
	                 mode='markers',
	                 marker=dict(
	                     size=size_ * 2, 
	                     color='#5ab4ac'
	                 ),
	                 text=list(pos.keys()),
	                 hoverinfo='text')

	Xe=[]
	Ye=[]
	for e in G.edges():
	    Xe.extend([pos[e[0]][0], pos[e[1]][0], None])
	    Ye.extend([pos[e[0]][1], pos[e[1]][1], None])
	    
	trace_edges=dict(type='scatter',
	                 mode='lines',
	                 x=Xe,
	                 y=Ye,
	                 line=dict(
	                     width=1, 
	                     color='#d8b365'
	                 ),
	                 hoverinfo='none' 
	                )

	axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
	          zeroline=False,
	          showgrid=False,
	          showticklabels=False,
	          title='' 
	          )
	layout=dict(title= title_,  
	            font= dict(family='Balto'),
	            width=600,
	            height=600,
	            autosize=False,
	            showlegend=False,
	            xaxis=axis,
	            yaxis=axis,
	            margin=dict(
	                l=40,
	                r=40,
	                b=85,
	                t=100,
	                pad=0,
	            ),
	    hovermode='closest',
	    plot_bgcolor='#efecea', #set background color            
	    )


	fig = dict(data=[trace_edges, trace_nodes], layout=layout)

	def make_annotations(pos, anno_text, font_size=14, font_color='rgb(10,10,10)'):
	    annotations = []
	    for k in list(pos.keys()):
	        annotations.append(dict(text=k, 
	                                x=pos[k][0], 
	                                y=pos[k][1] + 0.075,
	                                xref='x1', 
	                                yref='y1',
	                                font=dict(
	                                    color= font_color, 
	                                    size=font_size),
	                                showarrow=False)
	                          )
	    return annotations 

	fig['layout'].update(annotations=make_annotations(pos, list(pos.keys())))
	return fig


def get_table(movies, measure, title_):
	trace = go.Table(
	    header=dict(values=['Movie', 'Measure'],
	                line = dict(color='#7D7F80'),
	                fill = dict(color='#5ab4ac'),
	                align = ['left'] * 5),
	    cells=dict(values=[movies,
	                       measure],
	               line = dict(color='#7D7F80'),
	               fill = dict(color='#d8b365'),
	               align = ['left'] * 5))

	layout = dict(title = title_)
	data = [trace]
	fig = dict(data = data, layout = layout)
	return fig

# Graphs
in_degree_graph = get_graph(G, size_in, 'In degree movies network')
out_degree_graph = get_graph(G, size_out, 'Out degree movies network')
degree_graph = get_graph(G, size_, 'Degree movies network')

# Tables
top_in_degree = sorted(G.in_degree(),reverse=True, key=itemgetter(1))[:5]
top_in_degree_movies = []
top_in_degree_measures = []
for i in range(len(top_in_degree)):
    top_in_degree_movies.append(top_in_degree[i][0])
    top_in_degree_measures.append(top_in_degree[i][1])

top_out_degree = sorted(G.out_degree(),reverse=True, key=itemgetter(1))[:5]
top_out_degree_movies = []
top_out_degree_measures = []
for i in range(len(top_out_degree)):
    top_out_degree_movies.append(top_out_degree[i][0])
    top_out_degree_measures.append(top_out_degree[i][1])


top_degree = sorted(G.degree(),reverse=True, key=itemgetter(1))[:5]
top_degree_movies = []
top_degree_measures = []
for i in range(len(top_degree)):
    top_degree_movies.append(top_degree[i][0])
    top_degree_measures.append(top_degree[i][1])

in_degree_table = get_table(top_in_degree_movies, top_in_degree_measures, 'Top 5 movies by in degree')
out_degree_table = get_table(top_out_degree_movies, top_out_degree_measures, 'Top 5 movies by out degree')
degree_table = get_table(top_degree_movies, top_degree_measures, 'Top 5 movies by degree')


# Dash app declaration
app = dash.Dash()
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
app.layout = html.Div([
	html.H1(
        children='IMDB Network Visualization',
        style={
            'textAlign': 'center'
        }
    ),
			
	html.Div([

			html.Div([dcc.Markdown('''
									The task is From IMDB’s top rated 250 movies choose one movie, scrape the
								title of the movie, the summary text, and the urls for 12 similar movies from the 
								“More Like This” section. 
									For each of the 12 movies we must do the same (scrape the title, the summary text and the urls of their
								12 similar movies). This should be done for 3 layers. 
										* Layer 0: The dark knight  (the  movie I chose) , 
										* Layer 1: the “More Like This” movies from layer 0 movie, 
										* Layer 2: “More Like This” movies from layer 1 movies, 
										* Layer 3: “More Like This” movies from layer 2 movies.

									After collecting the appropriate data we will construct a directed network where each node is a movie 
								and each edge represents connection between nodes.
							''')], className = "row"),
			html.Div([
				html.Div([dcc.Graph(id='in_degree_', figure = in_degree_graph)], className = "six columns"),
				html.Div([dcc.Graph(id='in_degree_table', figure = in_degree_table)], className = "six columns"),
				], className = "row"),

			html.Div([
				html.Div([dcc.Graph(id='out_degree_', figure = out_degree_graph)], className = "six columns"),
				html.Div([dcc.Graph(id='out_degree_table', figure = out_degree_table)], className = "six columns"),
				], className = "row"),
			
			html.Div([
				html.Div([dcc.Graph(id='degree_', figure = degree_graph)], className = "six columns"),
				html.Div([dcc.Graph(id='degree_table', figure = degree_table)], className = "six columns"),
				], className = "row"),
			
			html.H3(
			        children='Conclusion',
			        style={
			            'textAlign': 'center'
			        }, className = "ten columns"
			    ),
			html.Div([dcc.Markdown('''
				 	According to above plotted graphs and tables of top movies we can say that 
				 	"Forrest Gump", "Fight Club", "Inception", "Pulp Fiction" and "LOTR" are 
				 	the most recommended movies as they have the top 5 degree (connection between movies).
				 	Also from out degree graph and table we notice, that probably "The dark knight", "Inceptio", "The dark knight Rises",
				 	"The SHawshank Redemptior" and "Fight Club" are in 0 or 1 level.

				 	''')], className = "twenty columns"),
		], className = "row")

	], style={
			'width': '90%',
            # 'flex-flow': 'row wrap',
            'padding': '5px',
           })

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port='8080')
