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
            # If user is not logged in, redirect to login page
            return login_layout
        elif time.time() > token_expiration:
            # If the token has expired, redirect to login page
            return login_layout
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
def getToken(username, password):
    return "token", time.time() + 20


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
    # Call the getToken function with username and password
    token, expiration = getToken(username, password)

    if token is None or expiration is None:
        return "Invalid credentials. Please try again."

    # Store the token and expiration in session or cookies for later use
    # For now, we'll use global variables as an example
    global logged_in
    global token_expiration
    logged_in = True
    token_expiration = expiration

    return "Login successful! Redirecting to the dashboard..."


# Callback to redirect to the login page after token expiration
@app.callback(
    Output('url', 'pathname'),
    [Input('login-message', 'children')],
    [State('url', 'pathname')]
)
def redirect_to_login(message, current_pathname):
    global logged_in

    if message == "Login successful! Redirecting to the dashboard...":
        time.sleep(2)  # Delay for demonstration purposes
        return '/dashboard'
    elif current_pathname == '/dashboard' and logged_in and token_expiration is not None and time.time() > token_expiration:
        logged_in = False
        print("Token expired. Redirecting to login page.")
        return '/'
    else:
        if logged_in and token_expiration is not None:
            time_remaining = int(token_expiration - time.time())
            if time_remaining <= 0:
                logged_in = False
                print("Token expired. Redirecting to login page.")
                return '/'
        raise PreventUpdate


# # Callback to redirect to the dashboard after successful login
# @app.callback(
#     Output('url', 'pathname'),
#     [Input('login-message', 'children')]
# )
# def redirect_to_dashboard(message):
#     if message == "Login successful! Redirecting to the dashboard...":
#         time.sleep(2)  # Delay for demonstration purposes
#         return '/dashboard'
#     else:
#         raise PreventUpdate


if __name__ == '__main__':
    logged_in = False
    token_expiration = None
    print("Starting server...")
    app.run_server(debug=True)
