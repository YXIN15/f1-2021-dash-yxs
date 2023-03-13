from dash import dash_table as dt
from dash import dash, html, Dash, Output, Input, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import altair as alt

# Load the data
teams_df = pd.read_csv("data/formula1_2021season_teams.csv")
drivers_df = pd.read_csv("data/formula1_2021season_drivers.csv")
results = pd.read_csv('data/formula1_2021season_raceResults.csv')
qual_results = pd.read_csv('data/formula1_2021season_sprintQualifyingResults.csv')
df1 = pd.read_csv("data/f1_2021_videogame_driver_ratings_initial.csv")
df2 = pd.read_csv("data/f1_2021_videogame_driver_ratings_jan2022.csv")

# Get team names
teams = teams_df.Team.unique().tolist()

# Get driver names
d_info = drivers_df[['Team', 'Driver']]
d_names = drivers_df.Driver.unique().tolist()

# Driver information
dr_sum = drivers_df.iloc[:, [0, 2, 3, 5, 6, 7, 8, 12]]
dr_sum = dr_sum.merge(df1.iloc[:, [1, 7, 8, 9]], left_on='Driver', right_on='Driver')

# Data wrangling for Team Summary table
results = results.merge(
    d_info, left_on='Driver', right_on='Driver'
).drop(['Team_x'], axis=1)
results.rename(columns={'Team_y': 'Team'}, inplace=True)

qual_results = qual_results.merge(
    d_info, left_on='Driver', right_on='Driver'
).drop(['Team_x'], axis=1)
qual_results.rename(columns={'Team_y': 'Team'}, inplace=True)

t_pts = results.groupby('Team')['Points'].sum()
st_pts = qual_results.groupby('Team')['Points'].sum()
t_pts = (t_pts+st_pts).sort_values(ascending=False).reset_index()
t_pts = t_pts.reset_index().rename(columns={'index': 'Rank'})
t_pts['Rank'] = t_pts['Rank'] + 1

# Data wrangling for driver plot
df1 = df1.iloc[:, 1:7]
df1['Status'] = 'Before Season'
df2 = df2.iloc[:, 1:7]
df2['Status'] = 'After Season'

overall_df = pd.concat([df1, df2])
cols_ds=overall_df.columns.tolist()[1:-1]
melted_df = pd.melt(overall_df, id_vars=['Driver', 'Status'], value_vars=cols_ds,
                    var_name='Stat', value_name='Value')

# Format the driver information table
def format(x):
    return "${:.2f}M".format(x/1000000)

# Apply formatting to driving information table
dr_sum['Contract Cost'] = dr_sum['Contract Cost'].apply(format)
dr_sum['Salary'] = dr_sum['Salary'].apply(format)
dr_sum['Buyout'] = dr_sum['Buyout'].apply(format)

# Make the driver ratings plot
def plot_driver(driver_name):
    if driver_name is None:
        driver_name = "Lewis Hamilton"
    plot_df = melted_df.query('Driver == @driver_name')
    chart = alt.Chart(plot_df).mark_bar().encode(
        x=alt.X('Status', title="Time"),
        y=alt.Y('Value', title="Rating Value"),
        column=alt.Column('Stat', title="Driver Ratings"),
        color=alt.Color('Status', legend=None),
        tooltip=['Value']
        ).configure_axis(
            labelFontSize=14,
            titleFontSize=16
            ).configure_header(
                titleFontSize=16,
                labelFontSize=14).properties(
                    width=65)
    return chart.to_html()

app = dash.Dash(__name__,
                external_stylesheets = [dbc.themes.SIMPLEX])

app.layout = html.Div([
    # First section -- title, info
    html.H1('Formula 1 Season 2021 Teams and Drivers'),
    html.Div([
        html.P('Welcome! This dashboard is based on the Formula 1 2021 Season statistics.'),
        html.P("Click on the tabs below to navigate between Team and Driver information.")],
             style={'margin-left': 50,
                    'margin-top': 25}
             ),
    dbc.Container(
        dbc.Tabs([
            # First page - Team info
            dbc.Tab([
                dbc.Row([
                    html.P('The table below shows the total points each team earned in the 2021 Season.'),
                    # Table summarizing team season performance
                    dbc.Col([
                        html.Div([
                            html.P('Select a row to learn more about a team:'),
                            dbc.Card([
                                dbc.CardHeader('Overall Team Rankings',
                                               style={'textAlign': 'center'}),
                                dbc.CardBody(
                                    dt.DataTable(
                                        id='teams_all',
                                        columns=[{"name": i, "id": i} for i in t_pts.columns],
                                        data=t_pts.to_dict("records"),
                                        style_data={
                                        'whiteSpace': 'normal',
                                        'height': 'auto'},
                                        style_cell={'textAlign': 'center'},
                                        style_header={
                                            'backgroundColor': 'rgb(255, 102, 102)',
                                            'color': 'black',
                                            'fontWeight': 'bold'
                                        },
                                        style_table={'height': '400px'},
                                        row_selectable = 'single'
                                        ),
                                        )
                                ])
                            ])
                        ], width=6),
                    # Table summaring specific team info
                    dbc.Col([
                        html.Br(),
                        html.Div([
                            dbc.Card([
                                dbc.CardHeader('Team Information',
                                               style={'textAlign': 'center'}),
                                dbc.CardBody(
                                    dt.DataTable(
                                        id='teams_table',
                                        style_cell={
                                            'textAlign': 'left',
                                            'height': 'auto',
                                            'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                                            'whiteSpace': 'normal'
                                        },
                                        style_header={
                                                'backgroundColor': 'rgb(255, 102, 102)',
                                                'color': 'black',
                                                'fontWeight': 'bold'
                                            },
                                        style_data={
                                            'whiteSpace': 'normal',
                                            'height': 'auto'},
                                        style_table={'height': '400px'}
                                        )
                                    )
                                ])
                            ], style = {'margin-top': 15})
                        ],
                            style={'width': '100%'}, id='table_cont1'
                            )
                    ])
            ], label='Teams Summary'),
            # Second tab - Driver information
            dbc.Tab([
                # Dropdown for selecting a driver
                html.Div([
                    'Select a name to learn more about a driver:',
                    dcc.Dropdown(
                        id="driver_selection",
                        options = [{"label": n, "value": n} for n in d_names],
                        placeholder = 'Select a team'),
                    ]),
                # Two sections in this column: image and table
                dbc.Row([
                    dbc.Col([
                        # Driver photo
                        html.Div([
                            dbc.Card([
                            dbc.CardHeader('Driver Information'),
                            dbc.CardBody(
                            html.Img(id='driver_img')
                            )
                        ])
                        ], 
                                 style={'textAlign': 'center'}, id='img_show'
                                 ),
                        # Driver information
                        html.Div([
                            dt.DataTable(
                            id='driver_info',
                            style_cell={'textAlign': 'center'},
                            style_header={
                                    'backgroundColor': 'rgb(255, 102, 102)',
                                    'color': 'black',
                                    'fontWeight': 'bold'
                                },
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'})
                        ], style={'width': '100%'}, id='table_cont2'
                                 )
                    ]),
                    # Other column shows a plot of driver rating info
                    dbc.Col([
                        html.Div([
                            html.Iframe(
                                id='driver_plot',
                                style={'border-width': '0', 'width': '600px', 'height': '600px'}
                            )
                        ],
                                 id='plot_id'
                                 )
                    ])
                ])
            ], label='Drivers Summary'),
            ])
                )
])

# Callback for updating team information
@app.callback(
    Output('table_cont1', 'style'),
    Output('teams_table', 'columns'),
    Output("teams_table", "data"),
    Input("teams_all", "selected_rows")
)
# Function to change team information to display
def teams_display(selected_rows):
    if selected_rows is None:
        style = {'display': 'none'}
        columns =[{"name": "Team", "id": "Team"}, 
                  {"name": "Team Information", "id": "Team Information"}]
        data = [{"Team": "", "Team Information":""}]
        return style, columns, data
    else:
        style = {'display': 'block'}
        team_name = t_pts.iloc[selected_rows[0],1]
        df = teams_df.query('Team == @team_name').T.reset_index()
        df.columns = df.iloc[0]
        df = df[1:]
        columns = [{"name": i, "id": i} for i in df.columns]
        data = df.to_dict("records")
        return style, columns, data

# Callback to change driver information to display
@app.callback(
    Output('table_cont2', 'style'),
    Output('driver_info', 'columns'),
    Output("driver_info", "data"),
    Input("driver_selection", "value")
)
# Function to change driver info table
def driver_summary(value):
    if value is None:
        style = {'display': 'none'}
        columns =[{"name": "Team", "id": "Team"}, 
                  {"name": "Team Information", "id": "Team Information"}]
        data = [{"Team": "", "Team Information":""}]
        return style, columns, data
    else:
        style = {'display': 'block'}
        df = dr_sum.query('Driver == @value').T.reset_index()
        df.columns = df.iloc[0]
        df = df[1:]
        columns = [{"name": i, "id": i} for i in df.columns]
        data = df.to_dict("records")
        return style, columns, data

# Callback to change driver photo
@app.callback(
    Output('driver_img', 'src'),
    Output('img_show', 'style'),
    Input('driver_selection', 'value')
)
# Function to change driver photo
def image_choice(value):
    if value is None:
        style = {'display': 'none'}
        image_path = ""
    else:
        style = {'display': 'block', 
                 'textAlign': 'center'}
        image_path = f"assets/drivers/{value}.png"
    return image_path, style

# Callback to change driver plot to display
@app.callback(
    Output('plot_id', 'style'),
    Output('driver_plot', 'srcDoc'),
    Input('driver_selection', 'value')
)
# Function to change data to plot
def plot_select(value):
    if value is None:
        style = {'display': 'none'}
    else:
        style = {'display': 'block',
                #  'margin': '50px',
                'margin-right': -80,
                'margin-top': 30}
    return style, plot_driver(value)


if __name__ == '__main__':
    app.run_server(debug=True)