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



# Read data
df = pd.read_csv('heart.csv')
# Separating out the features
features = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
# Get the correlation heatmap
corr = df.drop(["target"], axis = 1).corr()
heatmap_corr = np.array(corr.values)
corr_text = np.around(heatmap_corr, decimals=2)
heatmap_labels = list(corr.columns.values)
# Separating out the data without label(target)
x = df.loc[:, features].values
# Separating out the label(target)
y = df.loc[:,['target']].values
# Standardizing the features
x = StandardScaler().fit_transform(x)

# PCA model building
pca = PCA(random_state=222)
principalComponents = pca.fit_transform(x)
principalDf = pd.DataFrame(data = principalComponents
             , columns = ['principal component 1', 
                          'principal component 2',
                          'principal component 3',
                          'principal component 4',
                          'principal component 5',
                          'principal component 6',
                          'principal component 7',
                          'principal component 8',
                          'principal component 9',
                          'principal component 10',
                          'principal component 11',
                          'principal component 12',
                          'principal component 13',
                          ])

# The final model which will be used in next plottngs
finalDf = pd.concat([principalDf, df[['target']]], axis = 1)

# Keep eigan values for cumulative explained variance plot
eig_vals = pca.explained_variance_ratio_



# Used Functions
def pca_components_scatter_plot(dim_value):
	'''
	Plot the appropriate scatter plot depends on input value

	Parameters:
	dim_value (int): If 2 then plto will be 2 dimensional and will contain first 2 components of pca
					 and if 3 then first 3 components of pca

	Returns:
	figure(graph_obj) 2 or 3 dimensional scatter plot
	'''

	if dim_value == 3:
		data = []
		for i in [0, 1]:
		    trace = go.Scatter3d(x = finalDf[finalDf["target"] == i].iloc[:, 0],
		                         y = finalDf[finalDf["target"] == i].iloc[:, 1],
		                         z = finalDf[finalDf["target"] == i].iloc[:, 2],
		                         mode = 'markers',
		                         name = "class_{}".format(i),
		                         marker = dict(size = 3))
		    data.append(trace)
		    layout=dict(
		        title='Scatter plot between principal components',
		        xaxis=dict(
		            title='Principal component 1'
		        ),
		        yaxis=dict(
		            title='Principal component 2'
		        ),
		        zaxis=dict(
		            title='Principal component 3'
		        )
		    )

		figure = dict(data=data, layout=layout)
	else:
		data = []
		for i in [0, 1]:
		    trace = go.Scatter(x = finalDf[finalDf["target"] == i].iloc[:, 0],
		                         y = finalDf[finalDf["target"] == i].iloc[:, 1],
		                         mode = 'markers',
		                         name = "class_{}".format(i),
		                         marker = dict(size = 7))
		    data.append(trace)
		    layout=dict(
		        title='Scatter plot between principal components',
		        xaxis=dict(
		            title='Principal component 1'
		        ),
		        yaxis=dict(
		            title='Principal component 2'
		        )
		    )

		figure = dict(data=data, layout=layout)

	return figure

def cumulative_explained_variance_plot(eig_vals = eig_vals):
	# Plot the cumulative explained variance of pca components

	# Parameters:
	# eig_vals (array): eigan values of pca components (eigan vectors)

	# Returns:
	# figure(graph_obj): histogram and line graph on one plot
	
    
    tot = sum(eig_vals)
    var_exp = [(i / tot)*100 for i in sorted(eig_vals, reverse=True)]
    cum_var_exp = np.cumsum(var_exp)

    trace1 = dict(
        type='bar',
        x=['PC %s' %i for i in range(1,14)],
        y=var_exp,
        name='Individual'
    )

    trace2 = dict(
        type='scatter',
        x=['PC %s' %i for i in range(1,14)], 
        y=cum_var_exp,
        name='Cumulative'
    )

    data = [trace1, trace2]

    layout=dict(
        title='Explained variance by different principal components',
        yaxis=dict(
            title='Explained variance in percent'
        ),
    )

    figure = dict(data=data, layout=layout)
    return figure

def corr_heatmap_plot():
	# Plot the correlation matrix between initial variables

	# Returns:
	# figure(graph_obj): plotly heatmap 
    
	fig = ff.create_annotated_heatmap(heatmap_corr, x=heatmap_labels, y=heatmap_labels, annotation_text=corr_text, hoverinfo='z')

	for i in range(len(fig.layout.annotations)):
	    fig.layout.annotations[i].font.size = 8

	return fig


# Dash app declaration
app = dash.Dash()
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})



heatmap_plot = corr_heatmap_plot()
scatter_plot = pca_components_scatter_plot(dim_value = 2)
explained_variance_plot = cumulative_explained_variance_plot(eig_vals = eig_vals)




app.layout = html.Div([
	html.H1(
        children='Heart Disease Dataset Analysys',
        style={
            'textAlign': 'center'
        }
    ),
			
	html.Div([
			html.Div([dcc.Markdown('''
							This dataset gives a number of variables along with a target condition of having or not having heart disease.

							The features are the following:

							age: The person's age in years
							sex: The person's sex (1 = male, 0 = female)
							cp: The chest pain experienced 
								Value 1: typical angina, 
								Value 2: atypical angina, 
								Value 3: non-anginal pain, 
								Value 4: asymptomatic
							trestbps: The person's resting blood pressure ,mm Hg on admission to the hospital
							chol: The person's cholesterol measurement in mg/dl
							fbs: The person's fasting blood sugar (> 120 mg/dl, 1 = true; 0 = false)
							restecg: Resting electrocardiographic measurement 
								0 = normal, 
								1 = having ST-T wave abnormality, 
								2 = showing probable or definite left ventricular hypertrophy by Estes'
							thalach: The person's maximum heart rate achieved
							exang: Exercise induced angina (1 = yes; 0 = no)
							oldpeak: ST depression induced by exercise relative to rest 
							slope: the slope of the peak exercise ST segment 
								Value 1: upsloping, 
								Value 2: flat, 
								Value 3: downsloping
							ca: The number of major vessels (0-3)
							thal: A blood disorder called thalassemia 
								3 = normal,
								6 = fixed defect
								7 = reversable defect
							target: Heart disease (0 = no, 1 = yes)
				''')], className = "row"),

			html.Div([dcc.Markdown('''
							The task of this project is to use some techniques such as 
							visualizing correlation and pca analysis to find some basic knowledge about dataset.
							So first we will plot correlation heatmap to see linear correlation between features.
							Then by using pca analysis, visualize dependency between 2 or 3 (depending on toggle switch ) principal components. 

							''')], className = "row"),

			html.Div([dcc.Graph(id='heatmap_plot_id', figure = heatmap_plot)], className = "row"),
			html.Div([
				    daq.ToggleSwitch(
				    	id='graph-switch',
					    label='Switch 2D or 3D',
					    labelPosition='bottom'
					)
				], className = "ten columns"),
			html.Div([dcc.Graph(id='explained_variance_plot_id', figure = explained_variance_plot)], className = "five columns"),
			html.Div([dcc.Graph(id='scatter_plot_id', figure = scatter_plot)], className = "five columns"),

			html.H3(
			        children='Conclusion',
			        style={
			            'textAlign': 'center'
			        }, className = "ten columns"
			    ),
			html.Div([dcc.Markdown('''
								According to above plotted graphs we can make some decisions about data set.
							At first let's look at the correlation between the features.
							Actually there is no perfect (strong) linear relationship between them but comparing with others,
							some of them have in some sence good correlation , for example the following features have 
							negative correlation lesser than -0.3 (as a threshold I chose -0.3)
							"age" and "thalach": -0.4,
							"exang" and "cp: -.39
							"thalach" and "oldpeack": -0.34
							"thalach" and "exang": -0.38

							Also let;s notice that some of them have positive correlation greather than 0.3
							"thalach" and "slope" have positive correlation: 0.39
							"thalach" and "cp": 0.31

							The rest of them have correlation lesser (in case of positive correlation) and greather (in case of negative correlation)
							than +- 0.3.


							And the second point that I would like to take into consideration is principal components visualization.
							As the result of non perfect correlation between initial features, only first component has a significant explained variance which is 21.23 %,
							all the other 12 components have from 11.8 to 2.8 explained variance. PCA helps us to notice that in some sense there is a 
							possibility to cluster our data into 2 parts.

				 ''')], className = "twenty columns"),
		], className = "row")

	], style={
			'width': '90%',
            # 'flex-flow': 'row wrap',
            'padding': '5px',
           })
@app.callback(
    Output(component_id='scatter_plot_id', component_property='figure'),
    [Input(component_id='graph-switch', component_property='value')]
)
def update_text_output(value_):
	if value_:
		return pca_components_scatter_plot(3)
	return pca_components_scatter_plot(2)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port='8080')
