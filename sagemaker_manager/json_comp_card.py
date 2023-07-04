import dash
from dash import html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# Define the template component
def render_template_component(json_data):
    components = []

    # Iterate over each item in the JSON data
    for item in json_data['item']:
        # Create the card component for each item
        card = dbc.Card(
            dbc.CardBody(
                [
                    html.P(f"{item['item_id']}"),
                    html.P(f"{item['item_status']}"),
                    dbc.ButtonGroup(
                        [
                            dbc.Button(
                                button['button_name'],
                                color=button['button_color'],
                                id={'type': 'button', 'index': button_index},
                                className='mr-1',
                                n_clicks=0
                            )
                            for button_index, button in enumerate(item['action_button'])
                        ]
                    )
                ],
                className='d-flex justify-content-between align-items-center'
            ),
            className='w-auto mb-3',
        )

        components.append(card)

    return components


# JSON data (replace with your actual data source)
json_data = {
    "component_name": "Component Name",
    "item": [
        {
            "item_id": "1",
            "item_name": "Item 1",
            "item_status": "Active",
            "action_button": [
                {
                    "button_name": "🗑️",
                    "button_color": "primary",
                    "button_action": "function1",
                },
                {
                    "button_name": "✅",
                    "button_color": "secondary",
                    "button_action": "function2",
                }
            ],
            "other_data": {}
        },
        {
            "item_id": "2",
            "item_name": "Item 2",
            "item_status": "Inactive",
            "action_button": [
                {
                    "button_name": "Button 3",
                    "button_color": "success",
                    "button_action": "function3",
                },
                {
                    "button_name": "Button 4",
                    "button_color": "danger",
                    "button_action": "function4",
                }
            ],
            "other_data": {}
        }
    ]
}

# Call the template component function to render the cards
template_component = render_template_component(json_data)

# Define the layout
app.layout = html.Div(
    children=[
        html.H1('Template Component'),
        dbc.Card(
            [
                dbc.CardHeader(json_data['component_name']),
                dbc.CardBody(
                    template_component
                )
            ],
            className='mb-3',
            style={'width': '30vw'}
        )
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
