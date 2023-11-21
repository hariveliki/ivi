import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc
from dash.dependencies import Input, Output

# Load the dataset
covid_data = pd.read_csv('data/covid_arg_0_1.csv')

# Filter relevant data
covid_filtered = covid_data[['sexo', 'edad', 'residencia_provincia_nombre']].dropna()

# Prepare data for the Gapminder-like visualization
gapminder_data = covid_filtered.groupby(['edad', 'residencia_provincia_nombre', 'sexo']).size().reset_index(name='cases')

# Create Dash application
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("COVID-19 Visualizations for Argentina"),
    
    # Chart 1: Region vs. Cases
    html.H2("COVID-19 Cases by Region"),
    dcc.Graph(id='region-cases-graph'),
    
    # Chart 2: Gapminder-like Visualization
    html.H2("Age-Region Frequency Visualization"),
    dcc.Graph(id='age-region-graph'),
    
    html.Label("Select Gender:"),
    dcc.Dropdown(
        id='gender-dropdown',
        options=[{'label': i, 'value': i} for i in covid_filtered['sexo'].unique()],
        value=covid_filtered['sexo'].unique().tolist(),
        multi=True
    )
])

# Callback for updating the region-cases graph
@app.callback(
    Output('region-cases-graph', 'figure'),
    [Input('gender-dropdown', 'value')]
)
def update_region_cases(selected_genders):
    filtered_df = covid_filtered[covid_filtered['sexo'].isin(selected_genders)]
    sorted_df = filtered_df.groupby('residencia_provincia_nombre').size().reset_index(name='cases')
    sorted_df = sorted_df.sort_values('cases', ascending=False)  # Sort by cases in descending order
    fig1 = px.bar(sorted_df, x='residencia_provincia_nombre', y='cases', title='COVID-19 Cases by Region')
    return fig1

# Callback for updating the age-region graph
@app.callback(
    Output('age-region-graph', 'figure'),
    [Input('gender-dropdown', 'value')]
)
def update_age_region(selected_genders):
    filtered_df = gapminder_data[gapminder_data['sexo'].isin(selected_genders)]
    fig2 = px.scatter(filtered_df, x='edad', y='residencia_provincia_nombre', size='cases', color='sexo',
                      title='Age-Region Frequency Visualization', render_mode='webgl')
    return fig2

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
