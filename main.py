import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from plotly import graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Creating the sample DataFrame
data = [
    ["This is the first sample text.", 3.2, 4.5, 6.7, 1],
    ["Here's another sample text.", 7.1, 2.3, 8.9, 2],
    ["A third sample text.", 9.4, 1.8, 5.2, 3],
    ["One more sample text.", 6.6, 3.9, 2.1, 1],
    ["Last sample text.", 4.8, 7.2, 9.5, 2]
]

df = pd.DataFrame(data, columns=['text', '0', '1', '2', 'page'])

# Update the DataFrame to include the "text_id" column page + incrementing index for each page
df['text_id'] = df['page'].astype(str) + '_' + df.groupby('page').cumcount().add(1).astype(str)

# Compute cosine similarity matrix
similarity_matrix = cosine_similarity(df[['0', '1', '2']])


# Creating the Dash application
app = dash.Dash(__name__)

# Defining the layout
app.layout = html.Div([
    html.Div([
        html.Div(
            id='left-sidebar',
            className='sidebar',
            children=[
                html.H2("Left Sidebar"),
                html.H4("Tooltip Options"),
                dcc.Checklist(
                    id='tooltip-toggle',
                    options=[
                        {'label': 'Show Text', 'value': 'show-text'}
                    ],
                    value=[],
                    labelStyle={'display': 'block'}
                ),
                html.Br(),
                html.H4("Page Number"),
                dcc.Input(
                    id='page-input',
                    type='number',
                    placeholder='Enter page number',
                    min=1,
                    max=df['page'].max(),
                    step=1
                ),
            ],
            style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}
        ),

        html.Div([
            dcc.Graph(
                id='scatter-plot',
                style={'width': '100%', 'height': '600px'}
            )
        ], style={'width': '40%', 'display': 'inline-block', 'vertical-align': 'top', 'text-align': 'center'}),

        html.Div([
            html.H2('Right Sidebar'),
            html.Div([
                html.H3('Hovered Point'),
                html.Div(id='hovered-point-output')
            ]),
        ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),

        html.Button('Toggle Selection', id='clear-selection-button')
    ])
])


@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('tooltip-toggle', 'value'),
     Input('page-input', 'value'),
     Input('scatter-plot', 'clickData'),
     Input('clear-selection-button', 'n_clicks')]
)
def update_scatter_plot(show_text, page_number, click_data, clear_selection_clicks):
    # Creating the hover template based on the checkbox value
    hover_template = 'X: %{x}<br>Y: %{y}<br>Z: %{z}<br>'

    # Filter the data based on the entered page number
    if page_number:
        filtered_df = df[df['page'] == page_number]
    else:
        filtered_df = df

    if 'show-text' in show_text:
        hover_template += 'Page: %{customdata}<br>Text: %{text}'
        customdata = filtered_df['page']
    else:
        hover_template += 'Text ID: %{customdata}'
        customdata = filtered_df['text_id']

    # Create the scatter plot
    trace = go.Scatter3d(
        x=filtered_df['0'],
        y=filtered_df['1'],
        z=filtered_df['2'],
        mode='markers',
        marker=dict(
            size=6,
            color=filtered_df['page'],
            colorscale='Viridis',
            opacity=0.8
        ),
        text=filtered_df['text'],
        hovertemplate=hover_template,
        customdata=customdata,
        name='',
    )

    layout = go.Layout(scene=dict(aspectmode='cube'))

    fig = go.Figure(data=[trace], layout=layout)

    # Update the layout to remove the axes ticks and gridlines
    fig.update_layout(scene=dict(xaxis=dict(showgrid=False, showticklabels=False),
                                 yaxis=dict(showgrid=False, showticklabels=False),
                                 zaxis=dict(showgrid=False, showticklabels=False)
                                 ))

    # no background color
    fig.update_layout(scene=dict(
        xaxis=dict(backgroundcolor="white"),
        yaxis=dict(backgroundcolor="white"),
        zaxis=dict(backgroundcolor="white"),
        bgcolor="white"
    ))

    # don't show axes labels
    fig.update_layout(scene=dict(
        xaxis_title='',
        yaxis_title='',
        zaxis_title=''
    ))

    # remove projection
    fig.update_layout(scene=dict(
        xaxis=dict(showspikes=False),
        yaxis=dict(showspikes=False),
        zaxis=dict(showspikes=False)
    ))

    show_traces = True
    # print("clear_selection_clicks", clear_selection_clicks)

    # disable n_clicks


    # if clear_selection_clicks is not None:
    #     print("Buutton clicked", show_traces)
    #     show_traces = False
    #     print("Buutton clicked", show_traces)
    #     clear_selection_clicks = None
    #     print("clear_selection_clicks 2",clear_selection_clicks)


    # Get clicked point index
    clicked_index = None
    if click_data is not None:
        print(click_data)
        clicked_index = click_data['points'][0]['pointNumber']

        # Compute cosine similarity with clicked point
        similarities = cosine_similarity([filtered_df.iloc[clicked_index][['0', '1', '2']]], filtered_df[['0', '1', '2']])
        similarities = similarities.flatten()

        # sort similarities by descending order
        most_similar_index = np.argsort(similarities)[::-1]

        n = 2
        # keep only the top n
        most_similars = most_similar_index[1:n + 1]

        # # Remove the similarity traces if no point is clicked
        # fig.data = [trace]

        # add most similar points to the plot
        if n > 0:
            for i in most_similars:
                # print(filtered_df.iloc[i]['text_id'])
                # # print similarity score
                # print(similarities[i])
                fig.add_trace(
                    go.Scatter3d(
                        x=[filtered_df.iloc[clicked_index]['0'], filtered_df.iloc[i]['0']],
                        y=[filtered_df.iloc[clicked_index]['1'], filtered_df.iloc[i]['1']],
                        z=[filtered_df.iloc[clicked_index]['2'], filtered_df.iloc[i]['2']],
                        mode='markers',
                        marker=dict(
                            size=6,
                            color='red',
                            opacity=0.8
                        ),
                        name=filtered_df.iloc[i]['text_id'] + ' - ' + str(round(similarities[i], 2)),
                    )
                )

    else:
        similarities = np.zeros(len(filtered_df))


    if clear_selection_clicks is not None:
        # print TraceInfo
        # if clear_selection_clicks is odd
        if clear_selection_clicks % 2 == 1:
            # show only the first fig.data
            # print(type(fig.data[1]))
            # print(type(fig.data[0]))
            fig.data = [fig.data[0]]
            # print(fig.data[0])

        # else:
        #     fig.data = fig.data
        #     print(fig.data)


    print(show_traces)


    # # Update the button state
    # clear_button_state = {'display': 'none'} if show_similarity else {'display': 'inline'}




    # return fig, clear_button_state
    return fig



# Callback function to update the right sidebar output
@app.callback(
    Output('hovered-point-output', 'children'),
    [Input('scatter-plot', 'hoverData')]
)
def update_hovered_point_output(hover_data):
    if hover_data is not None:
        point_data = hover_data['points'][0]
        x, y, z = point_data['x'], point_data['y'], point_data['z']
        # if point_data has text
        if 'text' in point_data:
            text_value = point_data['text']
            text_id = df.loc[df['text'] == text_value, 'text_id'].values[0]
            page = df.loc[df['text'] == text_value, 'page'].values[0]
    else:
        x, y, z, text_value, text_id, page = None, None, None, None, None, None

    if x is not None and y is not None and z is not None and text_value is not None:
        return html.Div([
            html.P(f"Text ID: {text_id}"),
            html.P(f"Coordinates: X: {x}, Y: {y}, Z: {z}"),
            html.P(f"Text: {text_value}"),
            html.P(f"Page: {page}"),
        ])
    elif x is not None and y is not None and z is not None:
        return html.Div([
            html.P(f"Coordinates: X: {x}, Y: {y}, Z: {z}"),
        ])
    else:
        return html.P("Hover over a point to see its details.")


# Running the Dash application
if __name__ == '__main__':
    print("Running...")
    app.run_server(debug=True)
