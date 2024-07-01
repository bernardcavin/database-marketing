    
import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from utils.components import tabel, notif_fail,notif_success, data_tabel
from utils.models import CompanyClient, Contact
import dash_ag_grid as dag
from utils import apis
import flask
import uuid

def layout():

    df = apis.get_clients_table()

    table_columns = [
        {
            "headerName": col,
            "field": col,
            'filter': True 
        } for col in df.columns.to_list()[1:]
    ]

    table = dmc.Stack(
        [
            dcc.Store('refresh-clients',data=0),
            dmc.Group(
                [
                    dmc.TextInput(
                        id='search-box',
                        leftSection=DashIconify(icon='quill:search',width=20),
                        placeholder='Search...'
                    ),

                    dmc.Button(
                        'Add',
                        leftSection=DashIconify(icon='mdi:add-bold',width=20),
                        id='add-client',
                        n_clicks=0,
                        color='green',
                        justify='flex-end'
                    )
                ],
                justify='space-between'
            ),
            tabel(
                'clients',
                df,['view','edit','delete'],table_columns,rowHeight=50,height=500
            )
        ]
    )

    layout = dmc.Stack(
        [
            table
        ]
    )

    return layout

form_add_company_client = dmc.Stack(
    [
        dmc.TextInput(
            label='Company Name',
            id='company_name',
            required=True
        ),
        dmc.Textarea(
            label='Company Address',
            id='company_address',
        ),
        dmc.Stack(
            [
                dmc.Text('Contact Person',fw=500,size="sm"),
                dmc.Paper(
                    dmc.Stack(
                        [
                            dmc.TextInput(
                                id='name',
                                label='Name',
                                required=True
                            ),
                            dmc.TextInput(
                                id='title',
                                label='Title',
                                required=True
                            ),
                            dmc.TextInput(
                                id='email',
                                label='Email',
                                required=True
                            ),
                            dmc.TextInput(
                                id='phone',
                                label='Phone Number',
                                required=True
                            ),
                            dmc.Textarea(
                                id='contact_additional_info',
                                label='Additional Info',
                            ),
                            dmc.Group(
                                dmc.Button(
                                    'Add',
                                    leftSection=DashIconify(icon='mdi:add-bold',width=20),
                                    id='add-client-contact',
                                    n_clicks=0,
                                    color='green',
                                    bottom=0,
                                ),
                                justify='flex-end'
                            ),
                            dag.AgGrid(
                                id='client-contacts',
                                columnDefs=[
                                    {'field':header, 'headerName':header.title()} for header in ['name', 'title', 'email', 'phone','additional_info']
                                ] + [{'field':'Action','cellRenderer':'ActionButton','width':90,'minWidth':90,'pinned':'right'}],
                                columnSize='sizeToFit',
                                rowData=[],
                                getRowId="params.data.id",
                                dashGridOptions={
                                    'suppressCellFocus': True,
                                    "noRowsOverlayComponent": "CustomNoRowsOverlay",
                                    "noRowsOverlayComponentParams": {
                                        "message": "No Contacts",
                                        "fontSize": 12,
                                    },
                                    "loadingOverlayComponent": "CustomNoRowsOverlay",
                                    "loadingOverlayComponentParams": {
                                        "message": "No Contacts",
                                        "fontSize": 12,
                                    },
                                },
                            )
                        ],
                    ),
                    withBorder=True,
                    radius="sm",
                    p="sm"
                ),
            ],
            gap=2
        ),
        dmc.Textarea(
            label='Additional Info',
            id='additional_info',
        ),
        dmc.Button(
            'Add',
            leftSection=DashIconify(icon='mdi:add-bold',width=20),
            id='form-add-company-client',
            n_clicks=0,
            color='green',
        ),
    ]
)

form_add_individual_client = dmc.Stack(
    [
        dmc.TextInput(
            label='Client Name',
            id='client_name',
            required=True
        ),
        dmc.Textarea(
            label='Client Title',
            id='client_title',
        ),
        dmc.Textarea(
            label='Client Email',
            id='client_email',
        ),
        dmc.Textarea(
            label='Client Title',
            id='client_phone',
        ),
        dmc.Textarea(
            label='Additional Info',
            id='additional_info',
        ),
        dmc.Button(
            'Add',
            leftSection=DashIconify(icon='mdi:add-bold',width=20),
            id='form-add-individual-client',
            n_clicks=0,
            color='green',
        ),
    ]
)

modal_add_client = dmc.Modal(
    opened=True,
    id='modal-add-client',
    padding='lg',
    title=dmc.Group(
        [
            DashIconify(icon='mdi:add-bold',width=30),
            dmc.Title('Add Client',order=3)
        ],
        gap='sm'
    ),
    size='75%',
    children=dmc.Stack(
        [
            dmc.Select(
                label='Client Type',
                id='client_type',
                data=['Individual','Company'],
                value='Individual'
            ),
            html.Div(
                id='client-container',
                children=form_add_individual_client
            )
        ]
    ),
)


def modal_delete_client(type,client_id):

    if type=='company':

        client_obj = CompanyClient.query.filter(CompanyClient.client_id == client_id).first()

        flask.session['session_id'] = f"company;{client_obj.client_id}"

        modal_delete_client = dmc.Modal(
            title=dmc.Group(
                [
                    DashIconify(icon="material-symbols:delete",width=30),
                    dmc.Title(f'Delete Client',order=3)
                ],
                gap='sm'
            ),
            centered=True,
            zIndex=10000,
            children=dmc.Stack([
                dmc.Text(f'Are you sure you want to delete {client_obj.company_name}?'),
                dmc.Group([
                    dmc.Button(
                        'Yes, delete',
                        color="red",
                        id="delete_client",
                        n_clicks=0
                    ),
                ], justify='flex-end')
            ], gap='xl', style={'padding-top':20}),
            size='40%',
            style={'padding':20},
            opened=True)
        
        return modal_delete_client
    
    elif type == 'individual':

        client_obj = Contact.query.filter(Contact.contact_id == client_id).first()

        flask.session['session_id'] = f"individual;{client_obj.contact_id}"

        modal_delete_client = dmc.Modal(
            title=dmc.Group(
                [
                    DashIconify(icon="material-symbols:delete",width=30),
                    dmc.Title(f'Delete Client',order=3)
                ],
                gap='sm'
            ),
            centered=True,
            zIndex=10000,
            children=dmc.Stack([
                dmc.Text(f'Are you sure you want to delete {client_obj.name}?'),
                dmc.Group([
                    dmc.Button(
                        'Yes, delete',
                        color="red",
                        id="delete_client",
                        n_clicks=0
                    ),
                ], justify='flex-end')
            ], gap='xl', style={'padding-top':20}),
            size='40%',
            style={'padding':20},
            opened=True)
        
        return modal_delete_client

def modal_edit_client(type, client_id):

    if type == 'company':

        flask.session['session_id'] = str(uuid.uuid4())

        client_obj = CompanyClient.query.filter(CompanyClient.client_id == client_id).first()

        contacts = []

        for contact in client_obj.contacts:

            _contact = {
                'id':contact.contact_id,
                'name':contact.name,
                'title':contact.title,
                'email':contact.email,
                'phone':contact.phone,
                'additional_info':contact.additional_info,
                'Action':['delete']
            }

            contacts.append(_contact)

        modal_edit_client = dmc.Modal(
            opened=True,
            id='modal-edit-client',
            padding='lg',
            title=dmc.Group(
                [
                    DashIconify(icon="tabler:edit",width=30),
                    dmc.Title(f'Edit Client',order=3)
                ],
                gap='sm'
            ),
            size='75%',
            children=dmc.Stack(
                [
                    dmc.TextInput(
                        label='Client Id',
                        id='client_id',
                        value=client_obj.client_id,
                        disabled=True
                    ),
                    dmc.TextInput(
                        label='Company Name',
                        id='company_name',
                        value=client_obj.company_name,
                        required=True
                    ),
                    dmc.Textarea(
                        label='Client Address',
                        id='company_address',
                        value=client_obj.company_address,
                    ),
                    dmc.Stack(
                        [
                            dmc.Text('Contact Person',fw=500,size="sm"),
                            dmc.Paper(
                                dmc.Stack(
                                    [
                                        dmc.TextInput(
                                            id='name',
                                            label='Name',
                                            required=True
                                        ),
                                        dmc.TextInput(
                                            id='title',
                                            label='Title',
                                            required=True
                                        ),
                                        dmc.TextInput(
                                            id='email',
                                            label='Email',
                                            required=True
                                        ),
                                        dmc.TextInput(
                                            id='phone',
                                            label='Phone Number',
                                            required=True
                                        ),
                                        dmc.Textarea(
                                            id='contact_additional_info',
                                            label='Additional Info',
                                        ),
                                        dmc.Group(
                                            dmc.Button(
                                                'Add',
                                                leftSection=DashIconify(icon='mdi:add-bold',width=20),
                                                id='add-client-contact',
                                                n_clicks=0,
                                                color='green',
                                                bottom=0,
                                            ),
                                            justify='flex-end'
                                        ),
                                        dag.AgGrid(
                                            id='client-contacts',
                                            columnDefs=[
                                                {'field':header} for header in ['name', 'title', 'email', 'phone','additional_info']
                                            ] + [{'field':'Action','cellRenderer':'ActionButton','width':90,'minWidth':90,'pinned':'right'}],
                                            columnSize='sizeToFit',
                                            rowData=contacts,
                                            getRowId="params.data.id",
                                            dashGridOptions={
                                                'suppressCellFocus': True,
                                                "noRowsOverlayComponent": "CustomNoRowsOverlay",
                                                "noRowsOverlayComponentParams": {
                                                    "message": "No Contacts",
                                                    "fontSize": 12,
                                                },
                                                "loadingOverlayComponent": "CustomNoRowsOverlay",
                                                "loadingOverlayComponentParams": {
                                                    "message": "No Contacts",
                                                    "fontSize": 12,
                                                },
                                            },
                                        )
                                    ],
                                ),
                                withBorder=True,
                                radius="sm",
                                p="sm"
                            ),
                        ],
                        gap=2
                    ),
                    dmc.Textarea(
                        label='Additional Info',
                        id='additional_info',
                        value=client_obj.additional_info
                    ),
                    dmc.Button(
                        'Save Changes',
                        leftSection=DashIconify(icon='material-symbols:save',width=20),
                        id='form-edit-company-client',
                        n_clicks=0,
                        color='green',
                    ),
                ]
            )
        )

        return modal_edit_client
    
    elif type=='individual':

        flask.session['session_id'] = str(uuid.uuid4())

        client_obj = Contact.query.filter(Contact.contact_id == client_id).first()

        modal_edit_client = dmc.Modal(
            opened=True,
            id='modal-edit-client',
            padding='lg',
            title=dmc.Group(
                [
                    DashIconify(icon="tabler:edit",width=30),
                    dmc.Title(f'Edit Client',order=3)
                ],
                gap='sm'
            ),
            size='75%',
            children=dmc.Stack(
                [
                    dmc.TextInput(
                        label='Client_id',
                        id='client_id',
                        value=client_obj.contact_id,
                        disabled=True
                    ),
                    dmc.TextInput(
                        label='Client Name',
                        id='client_name',
                        value=client_obj.name,
                        required=True
                    ),
                    dmc.Textarea(
                        label='Client Title',
                        id='client_title',
                        value=client_obj.title,
                    ),
                    dmc.Textarea(
                        label='Client Email',
                        id='client_email',
                        value=client_obj.email,
                    ),
                    dmc.Textarea(
                        label='Client Phone',
                        id='client_phone',
                        value=client_obj.phone,
                    ),
                    dmc.Textarea(
                        label='Additional Info',
                        id='additional_info',
                        value=client_obj.additional_info
                    ),
                    dmc.Button(
                        'Save Changes',
                        leftSection=DashIconify(icon='material-symbols:save',width=20),
                        id='form-edit-individual-client',
                        n_clicks=0,
                        color='green',
                    ),
                ]
            )
        )

        return modal_edit_client

def modal_view_client(type,client_id):

    if type == 'company':
    
        flask.session['session_id'] = str(uuid.uuid4())

        client_obj = CompanyClient.query.filter(CompanyClient.client_id == client_id).first()

        modal_view_client = dmc.Modal(
            opened=True,
            id='modal-view-client',
            padding='lg',
            title=dmc.Group(
                [
                    DashIconify(icon="carbon:view-filled",width=30),
                    dmc.Title(f'{client_obj.company_name}',order=3)
                ],
                gap='sm'
            ),
            size='75%',
            children=dmc.Stack(
                [
                    dmc.Table(
                        [
                            dmc.TableThead(
                                dmc.TableTr(
                                    [
                                        dmc.TableTh("Information"),
                                        dmc.TableTh("Description"),
                                    ]
                                )
                            ),
                            dmc.TableTbody(
                                [
                                    dmc.TableTr([
                                        dmc.TableTd('Client Id'),
                                        dmc.TableTd(str(client_obj.client_id))
                                    ]),
                                    dmc.TableTr([
                                        dmc.TableTd('Client Name'),
                                        dmc.TableTd(client_obj.company_name)
                                    ]),
                                    dmc.TableTr([
                                        dmc.TableTd('Client Address'),
                                        dmc.TableTd(client_obj.company_address)
                                    ]),
                                    dmc.TableTr([
                                        dmc.TableTd('Additional Info'),
                                        dmc.TableTd(client_obj.additional_info)
                                    ]),
                                ]
                            )
                        ]
                    ),
                    dmc.Stack(
                        [
                            dmc.Text('Contacts',fw=500,size="sm"),
                            dmc.Table(
                                [
                                    dmc.TableThead(
                                        dmc.TableTr(
                                            [
                                                dmc.TableTh("Name"),
                                                dmc.TableTh("Title"),
                                                dmc.TableTh("Email"),
                                                dmc.TableTh("Phone"),
                                            ]
                                        )
                                    ),
                                    dmc.TableTbody(
                                        [
                                            dmc.TableTr(
                                                [
                                                    dmc.TableTd(str(contact.name)),
                                                    dmc.TableTd(str(contact.title)),
                                                    dmc.TableTd(str(contact.email)),
                                                    dmc.TableTd(str(contact.phone)),
                                                ] 
                                            ) for contact in client_obj.contacts
                                        ]
                                    )
                                ]
                            ),
                        ],
                        gap=2
                    ) if client_obj.contacts != [] else None,
                ]

            ),
        )

    elif type == 'individual':
    
        flask.session['session_id'] = str(uuid.uuid4())

        client_obj = Contact.query.filter(Contact.contact_id == client_id).first()

        modal_view_client = dmc.Modal(
            opened=True,
            id='modal-view-client',
            padding='lg',
            title=dmc.Group(
                [
                    DashIconify(icon="carbon:view-filled",width=30),
                    dmc.Title(f'{client_obj.name}',order=3)
                ],
                gap='sm'
            ),
            size='75%',
            children=dmc.Stack(
                [
                    dmc.Table(
                        [
                            dmc.TableThead(
                                dmc.TableTr(
                                    [
                                        dmc.TableTh("Information"),
                                        dmc.TableTh("Description"),
                                    ]
                                )
                            ),
                            dmc.TableTbody(
                                [
                                    dmc.TableTr([
                                        dmc.TableTd('Client Id'),
                                        dmc.TableTd(str(client_obj.contact_id))
                                    ]),
                                    dmc.TableTr([
                                        dmc.TableTd('Client Name'),
                                        dmc.TableTd(client_obj.name)
                                    ]),
                                    dmc.TableTr([
                                        dmc.TableTd('Client Title'),
                                        dmc.TableTd(client_obj.title)
                                    ]),
                                    dmc.TableTr([
                                        dmc.TableTd('Client Email'),
                                        dmc.TableTd(client_obj.email)
                                    ]),
                                    dmc.TableTr([
                                        dmc.TableTd('Client Phone'),
                                        dmc.TableTd(client_obj.email)
                                    ]),
                                    dmc.TableTr([
                                        dmc.TableTd('Additional Information'),
                                        dmc.TableTd(client_obj.additional_info)
                                    ]),
                                ]
                            )
                        ]
                    ),
                ]

            ),
        )


    return modal_view_client

@callback(
    Output('client-container','children'),
    Input('client_type','value'),
    prevent_initial_call=True
)
def render_client_type(client_type):
    if client_type == 'Company':
        return form_add_company_client
    else:
        return form_add_individual_client

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('add-client','n_clicks'),
    prevent_initial_call=True
)
def open_modal_add_client(n):
    if n>0:
        flask.session['session_id'] = str(uuid.uuid4())
        return modal_add_client

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('clients','cellRendererData'),
    prevent_initial_call=True
)
def open_modals(data):
    if data is not None:
        if data['value']=='edit':

            type,client_id = data['rowId'].split(';')

            return modal_edit_client(type,client_id)
        
        if data['value']=='delete':

            type,client_id = data['rowId'].split(';')

            return modal_delete_client(type,client_id)
        
        if data['value']=='view':

            type,client_id = data['rowId'].split(';')

            return modal_view_client(type,client_id)

@callback(
    Output('client-contacts', 'rowTransaction', allow_duplicate=True),
    Output('name','value', allow_duplicate=True),
    Output('title','value', allow_duplicate=True),
    Output('email','value', allow_duplicate=True),
    Output('phone','value', allow_duplicate=True),
    Output('contact_additional_info','value', allow_duplicate=True),
    Input('add-client-contact', 'n_clicks'),
    State('name','value'),
    State('title','value'),
    State('email','value'),
    State('phone','value'),
    State('contact_additional_info','value'),
    prevent_initial_call=True
)
def add_client_contact(n,name,title,email,phone, additonal_info):

    if n >= 0 and all(arg not in [None,''] for arg in [name,title,email,phone]):

        contact = {
            'id':str(uuid.uuid4()),
            'name':name,
            'title':title,
            'email':email,
            'phone':phone,
            'additional_info':additonal_info,
            'Action':['delete']
        }

        return {'add':[contact]}, '', '', '', '', ''
    
    else:
        
        raise dash.exceptions.PreventUpdate()
     
@callback(
    Output('client-contacts', 'rowTransaction'),
    Input('client-contacts', 'cellRendererData'),
    prevent_initial_call=True
)
def delete_contact(data):
    
    if data['value']=='delete':

        file_id = data['rowId']
    
    output = {'remove':[{'id':file_id}]}

    return output

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-clients','data',allow_duplicate=True),
    Input('form-add-company-client','n_clicks'),
    State('company_name','value'),
    State('company_address','value'),
    State('client-contacts','rowData'),
    State('additional_info','value'),
    prevent_initial_call = True
)
def upload_data_company_client(n,company_name, company_address, contacts, additional_info):
    
    if n>0:

        try:

            apis.add_CompanyClient(
                company_name,
                company_address,
                contacts,
                additional_info,
            )

            del flask.session['session_id']

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','Client successfully added.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-clients','data',allow_duplicate=True),
    Input('form-add-individual-client','n_clicks'),
    State('client_name','value'),
    State('client_title','value'),
    State('client_email','value'),
    State('client_phone','value'),
    State('additional_info','value'),
    prevent_initial_call = True
)
def upload_data_individual_client(n,client_name, client_title, client_email, client_phone, additional_info):
    
    if n>0:

        try:

            apis.add_IndividualClient(
                client_name,
                client_title,
                client_email,
                client_phone,
                additional_info
            )

            del flask.session['session_id']

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','Client successfully added.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-clients','data',allow_duplicate=True),
    Input('form-edit-company-client','n_clicks'),
    State('client_id','value'),
    State('company_name','value'),
    State('company_address','value'),
    State('client-contacts','rowData'),
    State('additional_info','value'),
    prevent_initial_call = True
)
def edit_company(n,client_id, company_name, company_address, contacts, additional_info):
    if n>0:

        try:

            apis.edit_CompanyClient(
                client_id,
                company_name,
                company_address,
                contacts,
                additional_info
            )

            del flask.session['session_id']

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update
        
        return notif_success('Success','Changes saved successfully.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-clients','data',allow_duplicate=True),
    Input('form-edit-individual-client','n_clicks'),
    State('client_id','value'),
    State('client_name','value'),
    State('client_title','value'),
    State('client_email','value'),
    State('client_phone','value'),
    State('additional_info','value'),
    prevent_initial_call = True
)
def edit_client(n,client_id, client_name, client_title, client_email, client_phone, additional_info):
    if n>0:

        try:

            apis.edit_IndividualClient(
                client_id,
                client_name,
                client_title,
                client_email,
                client_phone,
                additional_info
            )

            del flask.session['session_id']

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update
        
        return notif_success('Success','Changes saved successfully.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

clientside_callback(
    """
    function updateFilterModel(value, model) {
        if (model === null || model === undefined) {
            model = { 'Client Name': { filterType: 'text', type: 'contains', filter: value } };
        } else {
            model['Client Name'] = { filterType: 'text', type: 'contains', filter: value };
        }
        return model;
    }

    """,
    Output('clients', "filterModel"),
    Input("search-box", "value"),
    State('clients', "filterModel"),
)

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-clients','data',allow_duplicate=True),
    Input('delete_client','n_clicks'),
    prevent_initial_call=True
)
def delete_client(n):
    if n>0:
        try:

            type, id = flask.session['session_id'].split(';')

            if type == 'company':

                apis.delete_CompanyClient(id)

            elif type == 'individual':

                apis.delete_IndividualClient(id)

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','Client deleted successfully.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()
    
@callback(
    Output('refresh-clients','data',allow_duplicate=True),
    Output('clients','rowData'),
    Input('refresh-clients','data'),
    prevent_initial_call=True
)
def refresh(n):
    if n == 1:
        df = apis.get_clients_table()
        return 0, data_tabel(df,['view','edit','delete']).to_dict('records')
    elif n== 0:
        raise dash.exceptions.PreventUpdate()