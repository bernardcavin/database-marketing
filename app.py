import os
from flask import Flask
from flask_login import LoginManager, current_user, logout_user
from dotenv import load_dotenv
load_dotenv()

import dash
from dash import dcc, html, Input, Output, State
import dash_mantine_components as dmc
from utils.models import db, Employee

stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
]

external_scripts = ["https://unpkg.com/dash.nprogress@latest/dist/dash.nprogress.js"]

server = Flask(__name__)
app = dash.Dash(
    __name__, server=server, suppress_callback_exceptions=True, external_stylesheets=stylesheets, update_title=None, external_scripts=external_scripts
)

USERNAME = os.getenv("dbUSERNAME")
PASSWORD = os.getenv("dbPASSWORD")
HOST = os.getenv("dbHOST")
DATABASE = os.getenv("dbDATABASE")

app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}"
app.server.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))
app.server.app_context().push()
db.init_app(app.server)
db.create_all()

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"

@login_manager.user_loader
def load_user(user_id):
    return Employee.query.session.get(Employee, user_id)

app.title = 'Database APS'

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = dmc.MantineProvider(
    [
        dmc.NotificationProvider(),
        html.Div(id='modal'),
        html.Div(
            id='notif'
        ),
        dcc.Location(id='url', refresh=False),
        dcc.Location(id='redirect', refresh=True),
        html.Div(
            id='page-container',
        ),
    ],
)

from pages import home,login

@app.callback(Output('page-container', 'children'), 
              Output('redirect', 'pathname'),
              [Input('url', 'pathname'),
               State('url', 'href')],)
def display_page(pathname,href):
    view = None
    url = dash.no_update
    if pathname in ['/','/login']:
        if current_user.is_authenticated:
            view = home.layout()
            url = '/dashboard'
        else:
            view = login.layout
            url = '/login'
    elif pathname == '/dashboard':
        if current_user.is_authenticated:
            view = home.layout()
        else:
            view = login.layout
            url = '/login'
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            url = '/login'
        else:
            url = '/login'
    else:
        view = '404 Not Found'

    return view, url


if __name__ == "__main__":
    app.run(debug=True,host='localhost')#debug=True,