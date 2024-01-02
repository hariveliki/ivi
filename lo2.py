import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
from dash import html as html_components  # Import html from dash

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

# Create Dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("COVID-19 Dashboard", href="#"),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href="#")),
                    dbc.NavItem(dbc.NavLink("Region Cases", href="#region-cases")),
                    dbc.NavItem(dbc.NavLink("Age-Region Visualization", href="#age-region")),
                ],
                className="ml-auto",
            ),
        ],
    ),
    color="primary",
    dark=True,
)

# JavaScript code for smooth scrolling
javascript = """
<script>
    document.addEventListener("DOMContentLoaded", function() {
        var links = document.querySelectorAll('a.nav-link');
        links.forEach(function(link) {
            link.addEventListener("click", function(event) {
                event.preventDefault();
                var targetId = this.getAttribute("href").substring(1);
                var targetElement = document.getElementById(targetId);
                window.scrollTo({
                    top: targetElement.offsetTop,
                    behavior: "smooth"
                });
            });
        });
    });
</script>
"""

# App layout
app.layout = html.Div(
    [
        navbar,
        html_components.Div([  # Use html_components.Div for the JavaScript code
            html.Script(javascript),  # Include the JavaScript code using html.Script
            html.H1("COVID-19 Visualizations for Argentina", style={"textAlign": "center"}),
            html.Div(
                [
                    # Chart 1: Region vs. Cases
                    html.Div(
                        [
                            html.H2("COVID-19 Cases by Region"),
                            dcc.Graph(id="region-cases-graph", style={"height": "500px"}),
                        ],
                        className="six columns",
                        id="region-cases-graph-section",  # Add this ID
                    ),
                    # Chart 2: Gapminder-like Visualization
                    html.Div(
                        [
                            html.H2("Age-Region Frequency Visualization"),
                            dcc.Graph(id="age-region-graph", style={"height": "500px"}),
                        ],
                        className="six columns",
                        id="age-region-graph-section",  # Add this ID
                    ),
                ],
                className="row",
            ),
            html.Div(
                [
                    html.Label("Select Gender:"),
                    dcc.Dropdown(
                        id="gender-dropdown",
                        options=[
                            {"label": i, "value": i}
                            for i in covid_filtered["gender"].unique()
                        ],
                        value=covid_filtered["gender"].unique().tolist(),
                        multi=True,
                    ),
                ]
            ),
            # Age Range Slider for Brushing
            html.Div(
                [
                    html.Label("Select Age Range:"),
                    dcc.RangeSlider(
                        id="age-range-slider",
                        min=covid_filtered["age"].min(),
                        max=covid_filtered["age"].max(),
                        step=1,
                        value=[covid_filtered["age"].min(), covid_filtered["age"].max()],
                        marks={
                            i: str(i)
                            for i in range(
                                covid_filtered["age"].min(),
                                covid_filtered["age"].max() + 1,
                                10,
                            )
                        },
                    ),
                ],
                style={"padding": "20px 0 20px 0"},
            ),
        ]),
    ]
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
    fig1 = px.bar(
        region_cases_df,
        x="province",
        y="cases",
        title="COVID-19 Cases by Region",
    )

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
        title="Age-Region Frequency Visualization",
        hover_data=["cases"],
    )

    return fig1, fig2

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port="8051")
