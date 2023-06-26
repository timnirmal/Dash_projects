import dash
import numpy as np
import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from plotly import graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity

# parameters
default_similarity_threshold = 20
point_size = 3

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

# dataframe max rows / 2
n = int(df.shape[0] / 2)

# if n > 20 then n = 20
if n > default_similarity_threshold:
    n = default_similarity_threshold


# Creating the Dash application
app = dash.Dash(__name__)

# Defining the layout
app.layout = html.Div([
    html.Div([
        html.Div(
            id='left-sidebar',
            className='sidebar',
            children=[
                # html.H2("Left Sidebar"),
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
                html.Br(),
                html.H4("Similarity Threshold"),
                dcc.Input(
                    id='similarity-threshold',
                    type='number',
                    placeholder='Enter similarity threshold',
                    min=1,
                    step=1,
                    value=n
                ),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Button('Toggle Selection', id='clear-selection-button')
            ],
            style={'width': '13%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '15px'}
        ),

        html.Div([
            dcc.Graph(
                id='scatter-plot',
                style={'width': '100%', 'height': '100vh'}
            )
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top', 'text-align': 'center'}),

        html.Div([
            # html.H2('Right Sidebar'),
            html.H4('Hover Data'),
            html.Div(id='hovered-point-output'),
            html.Br(),
            html.Div(id='clicked-point-output')
        ], style={'width': '34%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '15px'}),


    ])
])


@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('tooltip-toggle', 'value'),
     Input('page-input', 'value'),
     Input('scatter-plot', 'clickData'),
     Input('clear-selection-button', 'n_clicks'),
     Input('similarity-threshold', 'value')]
)
def update_scatter_plot(show_text, page_number, click_data, clear_selection_clicks, similarity_threshold):
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
            size=point_size,
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

        # keep only the top n
        most_similars = most_similar_index[1:similarity_threshold + 1]

        # add most similar points to the plot
        if similarity_threshold > 0:
            for i in most_similars:
                fig.add_trace(
                    go.Scatter3d(
                        x=[filtered_df.iloc[clicked_index]['0'], filtered_df.iloc[i]['0']],
                        y=[filtered_df.iloc[clicked_index]['1'], filtered_df.iloc[i]['1']],
                        z=[filtered_df.iloc[clicked_index]['2'], filtered_df.iloc[i]['2']],
                        mode='markers',
                        marker=dict(
                            size=point_size,
                            color='red',
                            opacity=0.8
                        ),
                        name=filtered_df.iloc[i]['text_id'] + ' - ' + str(round(similarities[i], 2)),
                    )
                )
                similar_texts = filtered_df.iloc[most_similars]['text']
                similarity_scores = similarities[most_similars]
                print(similar_texts)
                print(similarity_scores)


    if clear_selection_clicks is not None:
        if clear_selection_clicks % 2 == 1:
            fig.data = [fig.data[0]]

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
            text_value, text_id, page = None, None, None
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


# Callback function to update the right sidebar output
@app.callback(
    Output('clicked-point-output', 'children'),
    [Input('scatter-plot', 'clickData'),
     Input('similarity-threshold', 'value')]
)
# In this function we need to get n number all of most similar texts from and update the clicked point output
# text_id - text - similarity score
def update_clicked_point_output(click_data, similarity_threshold):
    if click_data is not None:
        clicked_index = click_data['points'][0]['pointNumber']
        print(df)
        print(df.iloc[clicked_index])
        print(df.iloc[clicked_index][['0', '1', '2']])

        # Compute cosine similarity with clicked point
        similarities = cosine_similarity([df.iloc[clicked_index][['0', '1', '2']]], df[['0', '1', '2']])
        similarities = similarities.flatten()

        # sort similarities by descending order
        most_similar_index = np.argsort(similarities)[::-1]

        # keep only the top n
        most_similars = most_similar_index[1:similarity_threshold + 1]

        # prepare most similar texts and similarity scores
        similar_texts = df.iloc[most_similars]['text']
        similarity_scores = similarities[most_similars]
        print("Similar texts and similarity scores")
        print(similar_texts)
        print("Similar texts and similarity scores")
        print(similarity_scores)

        # prepare output
        output = []
        # add title
        output.append(html.H4("Most similar texts:"))
        # clicked text
        output.append(html.P(f"Clicked text: {df.iloc[clicked_index]['text']}"))
        # show small title for most similar texts
        output.append(html.P("Most similar texts:"))
        # add most similar texts and similarity scores
        for i in range(len(similar_texts)):
            print(similar_texts.iloc[i])
            print(similarity_scores[i])
            output.append(html.P(f"{similar_texts.iloc[i]} - {similarity_scores[i]}"))

        return output

    else:
        return html.P("Click on a point to see its most similar texts.")





# Running the Dash application
if __name__ == '__main__':
    print("Running...")
    app.run_server(debug=True)
