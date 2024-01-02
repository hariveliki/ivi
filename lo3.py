import time
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc

# Load the dataset
covid_data = pd.read_csv("data/covid_arg_0_1.csv")

# Filter relevant data
covid_filtered = covid_data[["gender", "age", "province"]].dropna()

# Convert 'age' column to integers
covid_filtered["age"] = covid_filtered["age"].astype(int)

# Prepare data for the Gapminder-like visualization
gapminder_data = (
    covid_filtered.groupby(["age", "province", "gender"])
    .size()
    .reset_index(name="cases")
)

# Create Dash application with Bootstrap components for better mobile responsiveness
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# Function to create tooltip
def create_tooltip(id, text):
    return dbc.Tooltip(text, target=id)

help_legend = dbc.Row(
    dbc.Col(
        [
            html.H4("Need Help?"),
            html.P("Here are some tips to help you interact with the dashboard:"),
            html.Ul([
                html.Li("Move the mouse pointer over the diagrams or filters to see more details. Click through the various options in the diagram and familiarize yourself with the possibilities."),
                html.Li("For example: Select an area with the mouse to enlarge the diagram. Double-click to zoom back out."),
                html.Li("If something does not work, try pressing the 'Reload' button in your browser. In most browsers, the button can be found in the top left-hand corner in the form of a circled arrow."),
            ]),
            html.P("For more assistance, contact the dashboard administrator."),
        ],
        className="mb-4"
    )
)

# App layout with added tooltips and improved layout for mobile responsiveness
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "COVID-19 Visualizations for Argentina",
                    className="text-center mb-4",
                )
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("COVID-19 Cases by Region"),
                        dcc.Loading(
                            id="loading-region",
                            type="default",
                            children=dcc.Graph(
                                id="region-cases-graph", style={"height": "500px"}
                            ),
                        ),
                        create_tooltip(
                            "region-cases-graph",
                            "Select an area with the mouse to enlarge the diagram. Double-click to zoom back out.",
                        ),
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        html.H2("Age-Region Frequency Visualization"),
                        dcc.Loading(
                            id="loading-age-region",
                            type="default",
                            children=dcc.Graph(
                                id="age-region-graph", style={"height": "500px"}
                            ),
                        ),
                        create_tooltip(
                            "age-region-graph",
                            "Select an area with the mouse to enlarge the diagram. Double-click to zoom back out.",
                        ),
                    ],
                    md=6,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select Gender:", id="gender-label"),
                        dcc.Dropdown(
                            id="gender-dropdown",
                            options=[
                                {"label": i, "value": i}
                                for i in covid_filtered["gender"].unique()
                            ],
                            value=covid_filtered["gender"].unique().tolist(),
                            multi=True,
                        ),
                        create_tooltip("gender-label", "Filter data by gender."),
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select Age Range:", id="age-range-label"),
                        dcc.RangeSlider(
                            id="age-range-slider",
                            min=covid_filtered["age"].min(),
                            max=covid_filtered["age"].max(),
                            step=1,
                            value=[
                                covid_filtered["age"].min(),
                                covid_filtered["age"].max(),
                            ],
                            marks={
                                i: str(i)
                                for i in range(
                                    covid_filtered["age"].min(),
                                    covid_filtered["age"].max() + 1,
                                    10,
                                )
                            },
                        ),
                        create_tooltip(
                            "age-range-label",
                            "Adjust the slider to filter data by age range.",
                        ),
                    ],
                    style={"padding": "20px 0 20px 0"},
                ),
            ]
        ),
        help_legend,
    ],
    fluid=True,
)


# Callback for updating both graphs
@app.callback(
    [Output("region-cases-graph", "figure"), Output("age-region-graph", "figure")],
    [Input("gender-dropdown", "value"), Input("age-range-slider", "value")],
)
def update_graphs(selected_genders, age_range):

    # Filter data based on gender and age range
    filtered_df = covid_filtered[
        (covid_filtered["gender"].isin(selected_genders))
        & (covid_filtered["age"] >= age_range[0])
        & (covid_filtered["age"] <= age_range[1])
    ]

    # Update region-cases graph
    region_cases_df = (
        filtered_df.groupby("province")
        .size()
        .reset_index(name="cases")
    )
    region_cases_df = region_cases_df.sort_values(
        "cases", ascending=False
    )  # Sort in descending order
    fig1 = px.bar(region_cases_df, x="province", y="cases")

    # Update age-region graph
    age_region_df = (
        filtered_df.groupby(["age", "province", "gender"])
        .size()
        .reset_index(name="cases")
    )
    fig2 = px.scatter(
        age_region_df,
        x="age",
        y="province",
        size="cases",
        color="gender",
        hover_data=["cases"],
    )

    # Update the legend labels for the 'gender' variable
    fig2.update_traces(
        name="Female",
        selector=dict(name="F"),
    )
    fig2.update_traces(
        name="Male",
        selector=dict(name="M"),
    )
    fig2.update_traces(
        name="Unknown",
        selector=dict(name="NR"),
    )
    # Implement animated transitions
    fig1.update_layout(transition_duration=500)
    fig2.update_layout(transition_duration=500)

    return fig1, fig2


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port="8050")
