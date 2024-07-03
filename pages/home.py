import dash
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH, ctx
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from furl import furl
from utils.components import HomePage, tabel, Page, PageGroup
from app import db
import pandas as pd
from pages.subpage import employees, inventory, purchase_orders, hoc, vendors, clients, ncnp

home_page = HomePage()

home_page.add(
    Page(
        'Home',
        'home',
        'tabler:home-filled',
        'Home'
    )
)

# home_page.add(
#     Page(
#         'Jobs',
#         'jobs',
#         'material-symbols:work',
#         jobs.layout
#     )
# )

home_page.add(
    Page(
        'NCNP',
        'ncnp',
        'bx:data',
        ncnp.layout
    )
)

home_page.add(
    Page(
        'Inventory',
        'inventory',
        'ic:baseline-inventory',
        inventory.layout
    )
)

home_page.add(
    Page(
        'Hazard Observation Card',
        'hoc',
        'clarity:form-line',
        hoc.layout
    )
)

home_page.add(
    PageGroup(
        'Marketing',
        'icon-park-solid:sales-report',
        [
            Page(
                'Clients',
                'clients',
                'material-symbols:person',
                clients.layout
            ),
            Page(
                'Vendors',
                'vendors',
                'mdi:company',
                vendors.layout
            ),
            Page(
                'Purchase Orders',
                'purchaseorders',
                'vaadin:money-exchange',
                purchase_orders.layout
            ),
        ]
    )
)

home_page.add(
    Page(
        'Employees',
        'employees',
        'clarity:employee-group-solid',
        employees.layout,
        admin=True
    )
)

home_page.initiate_callbacks()

layout = home_page.render




