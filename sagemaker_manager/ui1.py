import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc
import time

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Secure Application'
app.config['suppress_callback_exceptions'] = True
# app.css.append_css({
#     'external_url': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'
# })

# Login layout
login_layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Login", className="text-center mb-4"),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                [
                    dbc.Input(
                        id="username-input",
                        type="text",
                        placeholder="Username",
                        className="mb-3",
                    ),
                    dbc.Input(
                        id="password-input",
                        type="password",
                        placeholder="Password",
                        className="mb-3",
                    ),
                    dbc.Button(
                        "Log in",
                        id="login-button",
                        color="primary",
                        n_clicks=0
                    ),
                    html.Div(id="login-message", className="mt-3"),
                ],
                width=4,
                className="mx-auto",
            )
        ),
    ],
    className="mt-5",
)

# Dashboard layout
dashboard_layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    html.H1("Dashboard", className="text-center mb-4"),
                    html.Div(id="dashboard-content"),
                ],
                width=12
            )
        ),
    ],
    className="mt-5",
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# Callback to handle login
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return login_layout
    elif pathname == '/dashboard':
        if not logged_in:
            return html.Div("You must log in first.")
        else:
            return dashboard_layout
    else:
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The requested URL {pathname} was not found on this server."),
            ]
        )


# Callback to authenticate the user
@app.callback(
    Output('login-message', 'children'),
    [Input('login-button', 'n_clicks')],
    [State('username-input', 'value'), State('password-input', 'value')]
)
def authenticate_user(n_clicks, username, password):
    if n_clicks is None:
        raise PreventUpdate

    # Here, you should validate the username and password against your user database.
    # For simplicity, we'll use a dummy validation.
    if username is None or password is None:
        return ""
    if username == 'admin' and password == 'password':
        global logged_in
        logged_in = True
        return "Login successful! Redirecting to the dashboard..."
    else:
        return "Invalid credentials. Please try again."


# Callback to redirect to the dashboard after successful login
@app.callback(
    Output('url', 'pathname'),
    [Input('login-message', 'children')]
)
def redirect_to_dashboard(message):
    if message == "Login successful! Redirecting to the dashboard...":
        time.sleep(2)  # Delay for demonstration purposes
        return '/dashboard'
    else:
        raise PreventUpdate


if __name__ == '__main__':
    logged_in = False
    app.run_server(debug=True)
