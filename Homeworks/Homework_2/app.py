import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash()

app.layout = html.Div([
    dcc.Input(id='text_in', value='Name Surname', type='text'),
    dcc.Dropdown(
        id = 'option_in',
        options=[
            {'label': 'Facebook', 'value': 'www.fb.com'},
            {'label': 'Twitter', 'value': 'www.twitter.com'},
            {'label': 'AUA', 'value': 'www.aua.am'}
        ],
        value='www.fb.com'),
    html.Div(id='text_out')
])


@app.callback(
    Output(component_id='text_out', component_property='children'),
    [Input(component_id='text_in', component_property='value'),
     Input(component_id='option_in', component_property='value')]
)
def update_text_output(input_value_1,input_value_2):
    return input_value_1 + ", please follow me on " + input_value_2

if __name__ == '__main__':
    app.run_server()