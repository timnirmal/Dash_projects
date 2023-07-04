import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ClientsideFunction

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        dcc.Location(id="url", refresh=False),
        html.H1("Login Page"),
        dcc.Input(id="username-input", type="text", placeholder="Username"),
        dcc.Input(id="password-input", type="password", placeholder="Password"),
        html.Button("Login", id="login-button"),
        html.Div(id="login-status")
    ]
)

@app.callback(
    Output("url", "pathname"),
    Output("login-status", "children"),
    [Input("login-button", "n_clicks")],
    [State("username-input", "value"), State("password-input", "value")]
)
def authenticate(n_clicks, username, password):
    if n_clicks and username == "admin" and password == "password":
        # Authentication successful, redirect to authorized page
        return "/dashboard", "Login successful!"
    elif n_clicks:
        # Authentication failed, display error message
        return dash.no_update, "Invalid username or password"
    return dash.no_update, ""

# Define the authorized page
dashboard_page = html.Div(
    children=[
        html.H1("Dashboard"),
        html.P("Welcome to the dashboard!")
    ]
)

# Define a clientside callback to redirect to the dashboard page
app.clientside_callback(
    ClientsideFunction(
        namespace="clientside",
        function_name="redirect"
    ),
    Output("url", "pathname"),
    [Input("url", "pathname")]
)

# Inject JavaScript code for redirecting
app.clientside_callback(
    """
    function redirect(pathname) {
        if (pathname !== "/dashboard") {
            window.location.href = "/dashboard";
        }
    }
    """,
    Output("url", "pathname"),
    [Input("url", "pathname")]
)

if __name__ == "__main__":
    app.run_server(debug=True)
