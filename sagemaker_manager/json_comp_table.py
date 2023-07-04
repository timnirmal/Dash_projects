import dash
from dash import html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# Define the template component
def render_template_component(json_data, show_header=False):
    rows = []

    # Iterate over each item in the JSON data
    for item in json_data['item']:
        # Create a row for each item
        row = html.Tr(
            [
                html.Td(item['item_id']),
                html.Td(item['item_name']),
                html.Td(item['item_status']),
                html.Td(
                    [
                        dbc.Button(
                            button['button_name'],
                            color=button['button_color'],
                            id={'type': 'button', 'index': button_index},
                            className='mr-1',
                            n_clicks=0
                        )
                        for button_index, button in enumerate(item['action_button'])
                    ],
                    className='d-flex justify-content-center'
                )
            ]
        )

        rows.append(row)

        # Create the table with the rows
        table = html.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th('Item ID'),
                            html.Th('Item Name'),
                            html.Th('Item Status'),
                            html.Th('Action')
                        ]
                    )
                )
                if show_header else None,
                html.Tbody(rows)
            ],
            className='table'
        )

    # Create the card component with the table inside
    card = dbc.Card(
        [
            dbc.CardHeader(json_data['component_name']),
            dbc.CardBody(table)
        ],
        className='mb-3',
        style={}
    )

    return card


# # Call the template component function to render the card
# template_component = render_template_component(json_data)
# template_component_2 = render_template_component(json_data)
#
# # Define the layout
# app.layout = html.Div(
#     children=[
#         html.H1('Template Component'),
#         html.Div(
#             children=[template_component, template_component_2],
#             style={'display': 'flex', 'flex-wrap': 'wrap'}
#         )
#     ]
# )

if __name__ == '__main__':
    app.run_server(debug=True)

#                                 id={'type': 'button', 'index': button_index, 'id': item['item_name'],
#                                     'name': button['button_name']},

# button_group = row.children[3].children
# for button in button_group:
#     print(button)
#     print()
