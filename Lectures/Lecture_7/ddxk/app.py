import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go 

app = dash.Dash()
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

x = [1, 2, 3, 4, 5]
y = [10, 15, 12, 13]

trace = go.Scatter(x=x, y=y)
data = [trace]
my_figure = dict(data = data)

app.layout = html.Div([
	html.H1("Dash App"),
	html.Div([dcc.Dropdown(options = [
		{"label":"one", 'value':1},
		{"label":"two", "value":2}], value = "one"

		)]),
	html.Div([html.Div([dcc.Graph(figure = my_figure)], className = "six columns"),
				html.Div([dcc.Graph(figure = my_figure)], className = "six columns")


		], className = "row"),
	html.Div([html.P("Some text goes here")])
	
	], className = 'container')

if __name__ == '__main__':
    app.run_server(debug=True)