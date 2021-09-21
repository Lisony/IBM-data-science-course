# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_site = spacex_df[['Launch Site', 'class']]
launch_site = launch_site.groupby('Launch Site')['class'].value_counts(normalize = True) * 100
all_sites = launch_site[:, 1]
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                options=[
                                        {'label': 'All Sites', 'value': 'All Sites'}, 
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}],
                                        value = 'All Sites',
                                        placeholder = 'Select a Launch Site here',
                                        searchable = True
                                        ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                                id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                value=[min_payload, max_payload]
                                            ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'))

def generate_chart(value):
    if value == 'All Sites':
        all_sites_df = all_sites.to_frame().transpose()
        fig = px.pie(data_frame = all_sites_df, names=all_sites_df.columns, values  = all_sites.values)
    else:
        launch_site_df = launch_site
        fig = px.pie(data_frame = launch_site_df, names=launch_site_df[value].index, values = launch_site_df[value].values)
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    dash.dependencies.Output('success-payload-scatter-chart', 'figure'),
    [dash.dependencies.Input('site-dropdown', 'value'),
    dash.dependencies.Input('payload-slider', 'value')])
def update_scatter_plot(value, slider_range):
    if value == 'All Sites':
        low, high = slider_range
        mask = (spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)
        fig = px.scatter(
        spacex_df[mask], x="Payload Mass (kg)", y="class", 
        color="Booster Version Category")
        return fig
    else:
        filtered_spacex_df = spacex_df[spacex_df['Launch Site'] == value]
        low, high = slider_range
        mask = (filtered_spacex_df['Payload Mass (kg)'] > low) & (filtered_spacex_df['Payload Mass (kg)'] < high)
        fig = px.scatter(
        filtered_spacex_df[mask], x="Payload Mass (kg)", y="class", 
        color="Booster Version Category")
        return fig
    

# Run the app
if __name__ == '__main__':
    app.run_server()
