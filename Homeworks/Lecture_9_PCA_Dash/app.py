import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import sklearn.datasets

import plotly.graph_objs as go

wine_data = sklearn.datasets.load_wine()
Y = wine_data["target"]
wine_data = pd.DataFrame(wine_data["data"], columns=wine_data["feature_names"])
wine_data["target"] = Y
scaler = StandardScaler()
wine_scaled = scaler.fit_transform(wine_data.drop(["target"], axis = 1))
wine_scaled = pd.DataFrame(wine_scaled, columns=wine_data.drop(["target"], axis = 1).columns)
pca = PCA(random_state=42)
principalComponents = pca.fit_transform(wine_scaled)
comp_df = pd.DataFrame(principalComponents)
comp_df["target"] = wine_data["target"]



def get_plot(num_value):
	if num_value == 3:
		data = []
		for i in [0, 1, 2]:
		    trace = go.Scatter3d(x = comp_df[comp_df["target"] == i][0],
		                         y = comp_df[comp_df["target"] == i][1],
		                         z = comp_df[comp_df["target"] == i][2],
		                         mode = 'markers',
		                         name = "class_{}".format(i),
		                         marker = dict(size = 3))
		    data.append(trace)

		figure = dict(data=data)
	else:
		data = []
		for i in [0, 1, 2]:
		    trace = go.Scatter(x = comp_df[comp_df["target"] == i][0],
		                         y = comp_df[comp_df["target"] == i][1],
		                         mode = 'markers',
		                         name = "class_{}".format(i),
		                         marker = dict(size = 3))
		    data.append(trace)

		figure = dict(data=data)
	return figure


figure_ = get_plot(num_value = 3)


exp_var = pca.explained_variance_ratio_
exp_var_trace = go.Line(y = exp_var.cumsum(),
               x = np.arange(1, len(exp_var) + 1))
exp_var_data = [exp_var_trace]
exp_var_figure = dict(data = exp_var_data)



app = dash.Dash()
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})



app.layout = html.Div([
	html.Div([dcc.Dropdown(
        id = 'graph_option',
        options=[
            {'label': '3D', 'value': 3},
            {'label': '2D', 'value': 2},
        ],
        value = 3)], className = "row"),
			
			html.Div([
					html.Div([dcc.Graph(id='exp_var', figure = exp_var_figure)], className = "six columns"),
					html.Div([dcc.Graph(id='scatter', figure = figure_)], className = "six columns")
				], className = "row")],


	className = "container")


@app.callback(
    Output(component_id='scatter', component_property='figure'),
    [Input(component_id='graph_option', component_property='value')]
)
def update_text_output(value_):
    return get_plot(num_value = value_)


if __name__ == '__main__':
    app.run_server(debug=True)