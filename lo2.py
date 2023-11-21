import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq

# Load the dataset
covid_data = pd.read_csv('data/covid_arg_0_1.csv')

# Filter relevant data
covid_filtered = covid_data[['sexo', 'edad', 'residencia_provincia_nombre']].dropna()

# Convert 'edad' column to integers
covid_filtered['edad'] = covid_filtered['edad'].astype(int)

# Prepare data for the Gapminder-like visualization
gapminder_data = covid_filtered.groupby(['edad', 'residencia_provincia_nombre', 'sexo']).size().reset_index(name='cases')

# Create Dash application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("COVID-19 Visualizations for Argentina", style={'textAlign': 'center'}),
    
    html.Div([
        # Chart 1: Region vs. Cases
        html.Div([
            html.H2("COVID-19 Cases by Region"),
            dcc.Graph(id='region-cases-graph', style={'height': '500px'}),
        ], className='six columns'),

        # Chart 2: Gapminder-like Visualization
        html.Div([
            html.H2("Age-Region Frequency Visualization"),
            dcc.Graph(id='age-region-graph', style={'height': '500px'}),
        ], className='six columns'),
    ], className='row'),

    html.Div([
        html.Label("Select Gender:"),
        dcc.Dropdown(
            id='gender-dropdown',
            options=[{'label': i, 'value': i} for i in covid_filtered['sexo'].unique()],
            value=covid_filtered['sexo'].unique().tolist(),
            multi=True
        )
    ]),

    # Age Range Slider for Brushing
    html.Div([
        html.Label("Select Age Range:"),
        dcc.RangeSlider(
            id='age-range-slider',
            min=covid_filtered['edad'].min(),
            max=covid_filtered['edad'].max(),
            step=1,
            value=[covid_filtered['edad'].min(), covid_filtered['edad'].max()],
            marks={i: str(i) for i in range(covid_filtered['edad'].min(), covid_filtered['edad'].max() + 1, 10)},
        )
    ], style={'padding': '20px 0 20px 0'})
])

# Callback for updating both graphs
@app.callback(
    [Output('region-cases-graph', 'figure'),
     Output('age-region-graph', 'figure')],
    [Input('gender-dropdown', 'value'),
     Input('age-range-slider', 'value')]
)
def update_graphs(selected_genders, age_range):
    # Filter data based on gender and age range
    filtered_df = covid_filtered[(covid_filtered['sexo'].isin(selected_genders)) &
                                 (covid_filtered['edad'] >= age_range[0]) &
                                 (covid_filtered['edad'] <= age_range[1])]
    
    # Update region-cases graph
    region_cases_df = filtered_df.groupby('residencia_provincia_nombre').size().reset_index(name='cases')
    region_cases_df = region_cases_df.sort_values('cases', ascending=False)  # Sort in descending order
    fig1 = px.bar(region_cases_df, x='residencia_provincia_nombre', y='cases', title='COVID-19 Cases by Region')

    # Update age-region graph
    age_region_df = filtered_df.groupby(['edad', 'residencia_provincia_nombre', 'sexo']).size().reset_index(name='cases')
    fig2 = px.scatter(age_region_df, x='edad', y='residencia_provincia_nombre', size='cases', color='sexo',
                      title='Age-Region Frequency Visualization', hover_data=['cases'])

    return fig1, fig2

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
