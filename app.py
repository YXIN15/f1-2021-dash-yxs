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

# Data wrangling for driver points
d_pts = results.groupby(['Driver', 'Team'])['Points'].sum()
sd_pts = qual_results.groupby(['Driver', 'Team'])['Points'].sum()
d_pts = (d_pts+sd_pts).sort_values(ascending=False).reset_index()

# Data wrangling for driver plot
df1 = df1.iloc[:, 1:7]
df1['Status'] = 'Before Season'
df2 = df2.iloc[:, 1:7]
df2['Status'] = 'After Season'

overall_df = pd.concat([df1, df2])
cols_ds=overall_df.columns.tolist()[1:-1]
melted_df = pd.melt(overall_df, id_vars=['Driver', 'Status'], value_vars=cols_ds,
                    var_name='Stat', value_name='Value')

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
        )
    return chart.to_html()

app = dash.Dash(__name__,
                external_stylesheets = [dbc.themes.SIMPLEX])

app.layout = html.Div([
    html.H1('Formula 1 Season 2021 Teams and Drivers'),
    html.Div([
        html.P('Dash converts Python classes into HTML'),
        html.P("This conversion happens behind the scenes by Dash's JavaScript front-end")]),
    dbc.Container(
        dbc.Tabs([
            dbc.Tab([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            'Select a row to learn more about a team:',
                            dt.DataTable(
                                id='teams_all',
                                columns=[{"name": i, "id": i} for i in t_pts.columns],
                                data=t_pts.to_dict("records"),
                                # fixed_columns={'headers': True, 'data': 1},
                                # style_table={'minWidth': '100%'},
                                style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'},
                                style_cell={'textAlign': 'left'},
                                style_header={
                                    'backgroundColor': 'rgb(255, 102, 102)',
                                    'color': 'black',
                                    'fontWeight': 'bold'
                                },
                                row_selectable = 'single'
                                ),
                            ])
                        ], width=6),
                    dbc.Col([
                        html.Br(),
                        # html.Br(),
                        html.Div([
                        dt.DataTable(
                            id='teams_table',
                            # columns=[{"name": i, "id": i} for i in teams_df.columns],
                            # data=teams_df.to_dict("records"),
                            # fixed_columns={'headers': True, 'data': 1},
                            # style_table={'minWidth': '100%'},
                            style_cell={'textAlign': 'left'},
                            style_header={
                                    'backgroundColor': 'rgb(255, 102, 102)',
                                    'color': 'black',
                                    'fontWeight': 'bold'
                                },
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'})
                        ])
                        ],
                            style={'width': '100%'}, id='table_cont1'
                            )
                    ])
            ], label='Teams Summary'),
            dbc.Tab([
                html.Div([
                    'Select a name to learn more about a driver:',
                    dcc.Dropdown(
                        id="driver_selection",
                        options = [{"label": n, "value": n} for n in d_names],
                        # value =  drivers_df.Driver.values,
                        placeholder = 'Select a team'),
                    ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Img(id='driver_img')
                        ], 
                                 id='img_show'
                                 ),
                        html.Div([
                            dt.DataTable(
                            id='driver_info',
                            # columns=[{"name": i, "id": i} for i in teams_df.columns],
                            # data=teams_df.to_dict("records"),
                            # fixed_columns={'headers': True, 'data': 1},
                            # style_table={'minWidth': '100%'},
                            style_cell={'textAlign': 'left'},
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
                    dbc.Col([
                        html.Div([
                            html.Iframe(
                                id='driver_plot',
                                style={'border-width': '0', 'width': '100%', 'height': '400px'}
                            )
                        ],
                                 id='plot_id'
                                 )
                    ])
                ])
                    # dbc.Col([
                    #     html.Br(),
                    #     html.Br(),
                    #     # dt.DataTable(
                    #     #     id='teams_table',
                    #     #     columns=[{"name": i, "id": i} for i in teams_df.columns],
                    #     #     data=teams_df.to_dict("records"),
                    #     #     fixed_columns={'headers': True, 'data': 1},
                    #     #     style_table={'minWidth': '100%'},
                    #     #     style_data={
                    #     #         'whiteSpace': 'normal',
                    #     #         'height': 'auto'}),
                    # ])
            ], label='Drivers Summary'),
            ])
                ),
    # html.Div([
    #     'Choose a team:',
    #     dcc.Dropdown(
    #         id="team_selection",
    #         options = [{"label": t, "value": t} for t in teams],
    #         value =  teams_df.Team.values,
    #         placeholder = 'Select a team'),
    #     dt.DataTable(
    #         id='teams_table',
    #         columns=[{"name": i, "id": i} for i in teams_df.columns],
    #         data=teams_df.to_dict("records"),
    #         fixed_columns={'headers': True, 'data': 1},
    #         style_table={'minWidth': '100%'},
    #         style_data={
    #         'whiteSpace': 'normal',
    #         'height': 'auto'}
    #         ),
    # ]),
    # html.Div([
    #     'Choose a driver:',
    #     dcc.RadioItems(
    #         options=['New York City', 'Montreal', 'San Francisco'],
    #         value='Montreal'
    #     )
    # ])
])

@app.callback(
    Output('table_cont1', 'style'),
    Output('teams_table', 'columns'),
    Output("teams_table", "data"),
    Input("teams_all", "selected_rows")
)
def teams_display(selected_rows):
    if selected_rows is None:
        style = {'display': 'none'}
        columns =[{"name": "Team", "id": "Team"}, 
                  {"name": "Team Information", "id": "Team Information"}]
        data = [{"Team": "", "Team Information":""}]
        return style, columns, data
    else:
        style = {'display': 'block'}
        team_name = t_pts.iloc[selected_rows[0],0]
        df = teams_df.query('Team == @team_name').T.reset_index()
        df.columns = df.iloc[0]
        df = df[1:]
        columns = [{"name": i, "id": i} for i in df.columns]
        data = df.to_dict("records")
        # [{"name": i, "id": i} for i in t_pts.columns]
        return style, columns, data

@app.callback(
    Output('table_cont2', 'style'),
    Output('driver_info', 'columns'),
    Output("driver_info", "data"),
    Input("driver_selection", "value")
)
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
        # [{"name": i, "id": i} for i in t_pts.columns]
        return style, columns, data

@app.callback(
    Output('driver_img', 'src'),
    Output('img_show', 'style'),
    Input('driver_selection', 'value')
)
def image_choice(value):
    if value is None:
        style = {'display': 'none'}
        image_path = ""
    else:
        style = {'display': 'block'}
        image_path = f"assets/drivers/{value}.png"
    return image_path, style

@app.callback(
    Output('plot_id', 'style'),
    Output('driver_plot', 'srcDoc'),
    Input('driver_selection', 'value')
)
def plot_select(value):
    if value is None:
        style = {'display': 'none'}
    else:
        style = {'display': 'block'}
    return style, plot_driver(value)




if __name__ == '__main__':
    app.run_server(debug=True)
# from dash import dash, html, dcc


# app = dash.Dash(__name__)

# app.layout = html.Div([
#     'This is my slider',
#     dcc.Slider(min=0, max=5, value=2, marks={0: '0', 5: '5'})])

# if __name__ == '__main__':
#     app.run_server(debug=True)