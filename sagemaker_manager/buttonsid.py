import dash
from dash import Input, Output, State, ALL, callback, ctx
from dash import html,dcc
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#List to stock when a button has been clicked we put the id of the button there
List_Interaction = []

#Simple div for output callback
Screen = html.Div(id='dd-output-container',children=[])

# A button to create new buttons
Button_create = html.Button(
    'Create Button',id='create', n_clicks=0,
    style={'backgroundColor':'white'}
)

# A div to hold created buttons
Button_container = html.Div(id='button-container',children=[])

#simple container to stock the Button
Container_div = html.Div(
    [
        Button_create,
        Button_container,
        Screen
    ],
    style={
        'position': 'absolute',
        'left': '0px',
        'top': '0px',
        'margin-left': '0%',
        'outline': '0',
        'height': '100%',
        'width': '100%',
    },
    id = 'container-div'
)

# Callback to create new buttons
@callback(
    Output('button-container','children'),
    Input('create','n_clicks'),
    State('button-container','children'),
    prevent_initial_call=True
)
def create_new_button(n_clicks, current_buttons) :

    if n_clicks == 0 :
        raise dash.exceptions.PreventUpdate

    new_button = html.Button(
        f'Button {n_clicks}',
        id={'type':'btn_created', 'index':n_clicks},
        style={'backgroundColor':'white'},
        n_clicks=0
    )

    return current_buttons + [new_button]

# Callback to update list with last clicked button
@callback(
    Output('dd-output-container','children'),
    Input({'type':'btn_created','index':ALL}, 'n_clicks'),
    State('dd-output-container','children'),
    prevent_initial_call=True
)
def update_list(current_clicks, previous_clicks) :

    trigger = ctx.triggered_id['index']

    # numbre of clicks of last trigger
    trigger_clicks = ctx.triggered[-1]['value']

    #  we include this to prevent the list from updating when we create a new button (when its number of clicks is 0)
    if trigger_clicks == 0 :
        raise dash.exceptions.PreventUpdate

    last_click  = f'Button {trigger}'

    return previous_clicks + [last_click] + [html.Br()]

app.layout = html.Div([
    Container_div
])

if __name__=='__main__':
    app.run_server(host="localhost", port=5005,debug=False,dev_tools_ui=False)
    #app.run_server(debug=True)