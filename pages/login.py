from dash import html, callback, Output, Input, State, dcc, no_update, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from flask_login import login_user
from werkzeug.security import check_password_hash
from utils.models import Employee
from dash_extensions import EventListener

layout = dmc.Center(
    dmc.Stack(
        [
            dmc.Image(
                src='assets/Logo APS 2.png',h=10
            ),
            dmc.Paper(
                dmc.Box(
                    children=[
                        dmc.Stack(
                            pos="relative",
                            p=5,
                            w=300,
                            children=[
                                EventListener(
                                    dmc.Stack(
                                        [
                                            dcc.Store(id='login'),
                                            dmc.LoadingOverlay(
                                                visible=False,
                                                id="loading-overlay",
                                                zIndex=1000,
                                                overlayProps={"radius": "sm", "blur": 2},
                                            ),
                                            dmc.LoadingOverlay(
                                                visible=False,
                                                id="loading-overlay",
                                                zIndex=1000,
                                                overlayProps={"radius": "sm", "blur": 2},
                                            ),
                                            dmc.TextInput(
                                                label="Username",
                                                placeholder="Your username",
                                                leftSection=DashIconify(icon="radix-icons:person"),
                                                id="uname-box",
                                            ),
                                            dmc.PasswordInput(
                                                label="Password",
                                                placeholder="Your password",
                                                leftSection=DashIconify(icon="radix-icons:lock-closed"),
                                                id='pwd-box'
                                            ),
                                            dmc.Checkbox(
                                                label="Remember me",
                                                checked=True,
                                            ),
                                            dmc.Button(
                                                "Login", id="login-button", fullWidth=True
                                            ),
                                        ]
                                    ),
                                    events=[{"event": "keydown", "props": ["key"]}],
                                    id='event_listener'
                                ),
                                html.Div(children="", id="output-state"),
                            ],
                        ),
                    ]
                ),
                withBorder=True,
                p='lg',
                radius=20,
                shadow='lg'
            ),
        ]
    ),
    h='100vh',
    bg='white'
)

@callback(
    Output("output-state", "children"),
    Output('login','data'),
    Output("loading-overlay", "visible"),
    Input("login-button", "n_clicks"),
    State("uname-box", "value"),
    State("pwd-box", "value"),
    prevent_initial_call=True,
)
def login_button_click(n, username, password):

    user = Employee.query.filter_by(username=username).first()

    if user:
        if check_password_hash(user.password, password):
            
            login_user(user)

            return dmc.Alert(
                'Login successful! You will be redirected',
                title="Success!",
                color='green'
            ), 1, False
        
        else:
            return dmc.Alert(
                'Incorrect Password.',
                title="Error!",
                color='red'
            ), no_update, False
            
    else:
        return dmc.Alert(
            "Username not found.",
            title="Error!",
            color='red'
        ), no_update, False
    
clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        return true
    }
    """,
    Output("loading-overlay", "visible", allow_duplicate=True),
    Input("login-button", "n_clicks"),
    prevent_initial_call=True,
)

clientside_callback(
    """
    function(n) {
        if (n == 1) {
            setTimeout(function() {
                window.location.href = "/?p=home";
            }, 2000);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('url', 'pathname'),
    Input('login', 'data')
)

clientside_callback(
    """
    function handleKeyDown(event) {
        if (event !== undefined) {
            if (event.key === 'Enter') {
                document.getElementById('login-button').click();
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('login-button', 'n_clicks'),
    [Input('event_listener', 'event')]
)