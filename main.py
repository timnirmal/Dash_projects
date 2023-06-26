import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from plotly import graph_objects as go

# Creating the sample DataFrame
data = [
    ["This is the first sample text.", 3.2, 4.5, 6.7, 1],
    ["Here's another sample text.", 7.1, 2.3, 8.9, 2],
    ["A third sample text.", 9.4, 1.8, 5.2, 3],
    ["One more sample text.", 6.6, 3.9, 2.1, 1],
    ["Last sample text.", 4.8, 7.2, 9.5, 2]
]

df = pd.DataFrame(data, columns=['text', '0', '1', '2', 'page'])

# Update the DataFrame to include the "text_id" column
df['text_id'] = df['page'].astype(str) + '_' + (df.index + 1).astype(str)

# Creating the Dash application
app = dash.Dash(__name__)


# Defining the layout
app.layout = html.Div([
    html.Div([
        # Left Sidebar
        html.Div([
            html.H2('Left Sidebar'),
            # Add your input components for the left sidebar here
            # For example, dropdowns, sliders, etc.
        ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),

        # Plot Area
        html.Div([
            dcc.Graph(
                id='scatter-plot',
                style={'width': '100%', 'height': '600px'}  # Set the width and height of the graph
            )
        ], style={'width': '40%', 'display': 'inline-block', 'vertical-align': 'top', 'text-align': 'center'}),

        # Right Sidebar
        html.Div([
            html.H2('Right Sidebar'),
            html.Div(id='sidebar-output')
            # Add your output components for the right sidebar here
            # For example, text elements, charts, etc.
        ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
    ])
])

# Callback function to update the scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('scatter-plot', 'hoverData')]
)
def update_scatter_plot(hover_data):
    # Extracting the hovered point's coordinates and text value
    if hover_data is not None:
        point_data = hover_data['points'][0]
        x, y, z, text_value = point_data['x'], point_data['y'], point_data['z'], point_data['customdata']
    else:
        x, y, z, text_value = None, None, None, None

    # Creating the scatter plot
    trace = go.Scatter3d(
        x=df['0'],
        y=df['1'],
        z=df['2'],
        mode='markers',
        marker=dict(
            size=6,
            color=df['page'],
            colorscale='Viridis',
            opacity=0.8
        ),
        text=df['text'],
        hovertemplate='Text: %{text}<br>X: %{x}<br>Y: %{y}<br>Z: %{z}<extra></extra>',
        customdata=df['text']
    )

    annotations = []
    if x is not None and y is not None and z is not None and text_value is not None:
        annotations.append(dict(
            x=x,
            y=y,
            text=f"Text: {text_value}<br>X: {x}<br>Y: {y}<br>Z: {z}",
            showarrow=False,
            font=dict(size=12)
        ))

    layout = go.Layout(scene=dict(aspectmode='cube'), annotations=annotations)

    fig = go.Figure(data=[trace], layout=layout)

    return fig


@app.callback(
    Output('sidebar-output', 'children'),
    [Input('scatter-plot', 'hoverData')]
)
def update_sidebar_output(hover_data):
    if hover_data is not None:
        point_data = hover_data['points'][0]
        x, y, z, text_value, page = point_data['x'], point_data['y'], point_data['z'], point_data['customdata'], point_data['pointNumber']
        page_number = df.loc[page, 'page']
        return html.Div([
            html.H3('Hovered Point'),
            html.P(f"Text: {text_value}"),
            html.P(f"X: {x}"),
            html.P(f"Y: {y}"),
            html.P(f"Z: {z}"),
            html.P(f"Page: {page_number}")
        ])
    else:
        return ""


# Running the Dash application
if __name__ == '__main__':
    print("Running...")
    app.run_server(debug=True)
