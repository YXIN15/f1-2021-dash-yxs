from dash import dash_table as dt
from dash import dash, html, Dash, Output, Input, dcc
import dash_bootstrap_components as dbc
import pandas as pd

teams_df = pd.read_csv("data/formula1_2021season_teams.csv")
teams = teams_df.Team.unique().tolist()

drivers_df = pd.read_csv("data/formula1_2021season_drivers.csv")



app = dash.Dash(__name__,
                external_stylesheets = [dbc.themes.LUX])

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
                            'Choose a team:',
                            dcc.Dropdown(
                                id="team_selection",
                                options = [{"label": t, "value": t} for t in teams],
                                value =  teams_df.Team.values,
                                placeholder = 'Select a team'),
                            dt.DataTable(
                                id='teams_table',
                                columns=[{"name": i, "id": i} for i in teams_df.columns],
                                data=teams_df.to_dict("records"),
                                fixed_columns={'headers': True, 'data': 1},
                                style_table={'minWidth': '100%'},
                                style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'}
                                ),
                            ])]),
                    dbc.Col([
                        html.Br(),
                        html.Br(),
                        dt.DataTable(
                            id='teams_table2',
                            columns=[{"name": i, "id": i} for i in teams_df.columns],
                            data=teams_df.to_dict("records"),
                            fixed_columns={'headers': True, 'data': 1},
                            style_table={'minWidth': '100%'},
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'}),
                        ])
                    ])
            ], label='Tab1'),
            dbc.Tab('some', label='Tab2')
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
    Output("teams_table", "data"),
    Input("team_selection", "value")
)
def teams_display(team):
    df = teams_df.query("Team == @team")
    return df.to_dict("records")

if __name__ == '__main__':
    app.run_server(debug=True)

# from dash import dash, html, dcc


# app = dash.Dash(__name__)

# app.layout = html.Div([
#     'This is my slider',
#     dcc.Slider(min=0, max=5, value=2, marks={0: '0', 5: '5'})])

# if __name__ == '__main__':
#     app.run_server(debug=True)