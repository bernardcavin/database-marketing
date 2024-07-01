    
import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from utils.components import tabel, notif_fail,notif_success, data_tabel
from utils.models import Vendor
import dash_ag_grid as dag
from utils import apis
import flask
import uuid

def layout():

    df = apis.get_vendors_table()

    table_columns = [
        {
            "headerName": col,
            "field": col,
            'filter': True 
        } for col in df.columns.to_list()[1:]
    ]

    table = dmc.Stack(
        [
            dcc.Store('refresh-vendors',data=0),
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
                        id='add-vendor',
                        n_clicks=0,
                        color='green',
                        justify='flex-end'
                    )
                ],
                justify='space-between'
            ),
            tabel(
                'vendors',
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

modal_add_vendor = dmc.Modal(
    opened=True,
    id='modal-add-vendor',
    padding='lg',
    title=dmc.Group(
        [
            DashIconify(icon='mdi:add-bold',width=30),
            dmc.Title('Add Vendor',order=3)
        ],
        gap='sm'
    ),
    size='75%',
    children=dmc.Stack(
        [
            dmc.TextInput(
                label='Vendor Name',
                id='vendor_name',
                required=True
            ),
            dmc.Textarea(
                label='Vendor Address',
                id='vendor_address',
            ),
            dmc.Select(
                label='Vendor Type',
                id='vendor_type',
                data=['Manufacturer', 'Wholesaler', 'Retailers', 'Service','Maintenance Providers'],
                required=True
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
                                        id='add-contact',
                                        n_clicks=0,
                                        color='green',
                                        bottom=0,
                                    ),
                                    justify='flex-end'
                                ),
                                dag.AgGrid(
                                    id='contacts',
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
            dmc.Stack(
                [
                    dmc.Text('Products',fw=500,size="sm"),
                    dmc.Paper(
                        dmc.Stack(
                            [
                                dmc.TextInput(
                                    id='product_name',
                                    label='Product Name',
                                    required=True
                                ),
                                dmc.NumberInput(
                                    id='unit_price',
                                    label='Unit Price',
                                ),
                                dmc.Select(
                                    id='currency',
                                    label='Currency',
                                    data=['USD','IDR'],
                                    value='USD'
                                ),
                                dmc.Textarea(
                                    id='description',
                                    label='Description',
                                ),
                                dmc.Group(
                                    dmc.Button(
                                        'Add',
                                        leftSection=DashIconify(icon='mdi:add-bold',width=20),
                                        id='add-product',
                                        n_clicks=0,
                                        color='green',
                                        bottom=0,
                                    ),
                                    justify='flex-end'
                                ),
                                dag.AgGrid(
                                    id='products',
                                    columnDefs=[
                                        {'field':header} for header in ['Product Name', 'Unit Price', 'Currency', 'Description']
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
                id='form-add-vendor',
                n_clicks=0,
                color='green',
            ),
        ]
    ),
)

def modal_delete_vendor(vendor_id):

    vendor_obj = Vendor.query.filter(Vendor.vendor_id == vendor_id).first()

    flask.session['session_id'] = vendor_obj.vendor_id

    modal_delete_vendor = dmc.Modal(
        title=dmc.Group(
            [
                DashIconify(icon="material-symbols:delete",width=30),
                dmc.Title(f'Delete Vendor',order=3)
            ],
            gap='sm'
        ),
        centered=True,
        zIndex=10000,
        children=dmc.Stack([
            dmc.Text(f'Are you sure you want to delete {vendor_obj.vendor_name}?'),
            dmc.Group([
                dmc.Button(
                    'Yes, delete',
                    color="red",
                    id="delete_vendor",
                    n_clicks=0
                ),
            ], justify='flex-end')
        ], gap='xl', style={'padding-top':20}),
        size='40%',
        style={'padding':20},
        opened=True)
    
    return modal_delete_vendor

def modal_edit_vendor(vendor_id):

    flask.session['session_id'] = str(uuid.uuid4())

    vendor_obj = Vendor.query.filter(Vendor.vendor_id == vendor_id).first()

    contacts = []

    products = []

    for contact in vendor_obj.contacts:

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
        

    for product in vendor_obj.products:

        _product = {
            'id':product.product_id,
            'Product Name':product.product_name,
            'Unit Price':product.unit_price,
            'Currency':product.currency,
            'Description':product.description,
            'Action':['delete']
        }

        products.append(_product)

    modal_edit_vendor = dmc.Modal(
        opened=True,
        id='modal-edit-vendor',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon="tabler:edit",width=30),
                dmc.Title(f'Edit Vendor',order=3)
            ],
            gap='sm'
        ),
        size='75%',
        children=dmc.Stack(
            [
                dmc.TextInput(
                    label='Vendor Id',
                    id='vendor_id',
                    value=vendor_obj.vendor_id,
                    disabled=True
                ),
                dmc.TextInput(
                    label='Vendor Name',
                    id='vendor_name',
                    value=vendor_obj.vendor_name,
                    required=True
                ),
                dmc.Textarea(
                    label='Vendor Address',
                    id='vendor_address',
                    value=vendor_obj.vendor_address,
                ),
                dmc.Select(
                    label='Vendor Type',
                    id='vendor_type',
                    data=['Manufacturer', 'Wholesaler', 'Retailers', 'Service','Maintenance Providers'],
                    value=vendor_obj.vendor_type,
                    required=True
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
                                            id='add-contact',
                                            n_clicks=0,
                                            color='green',
                                            bottom=0,
                                        ),
                                        justify='flex-end'
                                    ),
                                    dag.AgGrid(
                                        id='contacts',
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
                dmc.Stack(
                    [
                        dmc.Text('Products',fw=500,size="sm"),
                        dmc.Paper(
                            dmc.Stack(
                                [
                                    dmc.TextInput(
                                        id='product_name',
                                        label='Product Name',
                                        required=True
                                    ),
                                    dmc.NumberInput(
                                        id='unit_price',
                                        label='Unit Price',
                                    ),
                                    dmc.Select(
                                        id='currency',
                                        label='Currency',
                                        data=['USD','IDR'],
                                        value='USD'
                                    ),
                                    dmc.Textarea(
                                        id='description',
                                        label='Description',
                                    ),
                                    dmc.Group(
                                        dmc.Button(
                                            'Add',
                                            leftSection=DashIconify(icon='mdi:add-bold',width=20),
                                            id='add-product',
                                            n_clicks=0,
                                            color='green',
                                            bottom=0,
                                        ),
                                        justify='flex-end'
                                    ),
                                    dag.AgGrid(
                                        id='products',
                                        columnDefs=[
                                            {'field':header} for header in ['Product Name', 'Unit Price', 'Currency', 'Description']
                                        ] + [{'field':'Action','cellRenderer':'ActionButton','width':90,'minWidth':90,'pinned':'right'}],
                                        columnSize='sizeToFit',
                                        rowData=products,
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
                    value=vendor_obj.additional_info
                ),
                dmc.Button(
                    'Save Changes',
                    leftSection=DashIconify(icon='material-symbols:save',width=20),
                    id='form-edit-vendor',
                    n_clicks=0,
                    color='green',
                ),
            ]
        )
    )

    return modal_edit_vendor

def modal_view_vendor(vendor_id):

    flask.session['session_id'] = str(uuid.uuid4())

    vendor_obj = Vendor.query.filter(Vendor.vendor_id == vendor_id).first()

    modal_view_vendor = dmc.Modal(
        opened=True,
        id='modal-view-vendor',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon="carbon:view-filled",width=30),
                dmc.Title(f'{vendor_obj.vendor_name}',order=3)
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
                                    dmc.TableTd('Vendor Id'),
                                    dmc.TableTd(str(vendor_obj.vendor_id))
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Vendor Name'),
                                    dmc.TableTd(vendor_obj.vendor_name)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Vendor Address'),
                                    dmc.TableTd(vendor_obj.vendor_address)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Vendor Type'),
                                    dmc.TableTd(vendor_obj.vendor_type)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Additional Info'),
                                    dmc.TableTd(vendor_obj.additional_info)
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
                                        ) for contact in vendor_obj.contacts
                                    ]
                                )
                            ]
                        ),
                    ],
                    gap=2
                ) if vendor_obj.contacts != [] else None,
                dmc.Stack(
                    [
                        dmc.Text('Products',fw=500,size="sm"),
                        dmc.Table(
                            [
                                dmc.TableThead(
                                    dmc.TableTr(
                                        [
                                            dmc.TableTh("Product Name"),
                                            dmc.TableTh("Unit Price"),
                                            dmc.TableTh("Description"),
                                        ]
                                    )
                                ),
                                dmc.TableTbody(
                                    [
                                        dmc.TableTr(
                                            [
                                                dmc.TableTd(str(product.product_name)),
                                                dmc.TableTd(f"{product.currency} {product.unit_price}"),
                                                dmc.TableTd(str(product.description)),
                                            ] 
                                        ) for product in vendor_obj.products
                                    ]
                                )
                            ]
                        ),
                    ],
                    gap=2
                ) if vendor_obj.products != [] else None,
            ]

        ),
    )


    return modal_view_vendor

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('add-vendor','n_clicks'),
    prevent_initial_call=True
)
def open_modal_add_vendor(n):
    if n>0:
        flask.session['session_id'] = str(uuid.uuid4())
        return modal_add_vendor

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('vendors','cellRendererData'),
    prevent_initial_call=True
)
def open_modals(data):
    if data is not None:
        if data['value']=='edit':

            vendor_id = data['rowId']

            return modal_edit_vendor(vendor_id)
        
        if data['value']=='delete':

            vendor_id = data['rowId']

            return modal_delete_vendor(vendor_id)
        
        if data['value']=='view':

            vendor_id = data['rowId']

            return modal_view_vendor(vendor_id)

@callback(
    Output('contacts', 'rowTransaction', allow_duplicate=True),
    Output('name','value'),
    Output('title','value'),
    Output('email','value'),
    Output('phone','value'),
    Output('contact_additional_info','value'),
    Input('add-contact', 'n_clicks'),
    State('name','value'),
    State('title','value'),
    State('email','value'),
    State('phone','value'),
    State('contact_additional_info','value'),
    prevent_initial_call=True
)
def add_contact(n,name,title,email,phone, additonal_info):

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
    Output('contacts', 'rowTransaction'),
    Input('contacts', 'cellRendererData'),
    prevent_initial_call=True
)
def delete_contact(data):
    
    if data['value']=='delete':

        file_id = data['rowId']
    
    output = {'remove':[{'id':file_id}]}

    return output


@callback(
    Output('products', 'rowTransaction', allow_duplicate=True),
    Output('product_name','value'),
    Output('unit_price','value'),
    Output('currency','value'),
    Output('description','value'),
    Input('add-product', 'n_clicks'),
    State('product_name','value'),
    State('unit_price','value'),
    State('currency','value'),
    State('description','value'),
    prevent_initial_call=True
)
def add_product(n,product_name,unit_price,currency,description):

    if n >= 0 and all(arg not in [None,''] for arg in [product_name,unit_price,currency]):

        contact = {
            'id':str(uuid.uuid4()),
            'Product Name':product_name,
            'Unit Price':unit_price,
            'Currency':currency,
            'Description':description,
            'Action':['delete']
        }

        return {'add':[contact]}, '', '', '', ''
    
    else:
        
        raise dash.exceptions.PreventUpdate()
     
@callback(
    Output('products', 'rowTransaction'),
    Input('products', 'cellRendererData'),
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
    Output('refresh-vendors','data',allow_duplicate=True),
    Input('form-add-vendor','n_clicks'),
    State('vendor_name','value'),
    State('vendor_address','value'),
    State('vendor_type','value'),
    State('contacts','rowData'),
    State('products','rowData'),
    State('additional_info','value'),
    prevent_initial_call = True
)
def upload_data(n,vendor_name, vendor_address, vendor_type, contacts, products, additional_info):
    
    if n>0:

        try:

            apis.add_Vendor(
                vendor_name,
                vendor_address,
                vendor_type,
                contacts,
                products,
                additional_info
            )

            del flask.session['session_id']

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','Vendor successfully added.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-vendors','data',allow_duplicate=True),
    Input('form-edit-vendor','n_clicks'),
    State('vendor_id','value'),
    State('vendor_name','value'),
    State('vendor_address','value'),
    State('vendor_type','value'),
    State('contacts','rowData'),
    State('products','rowData'),
    State('additional_info','vallue'),
    prevent_initial_call = True
)
def edit_vendor(n,vendor_id, vendor_name, vendor_address, vendor_type, contacts, products,additional_info):
    if n>0:

        try:

            apis.edit_Vendor(
                vendor_id,
                vendor_name,
                vendor_address,
                vendor_type,
                contacts,
                products,
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
            model = { 'Vendor Name': { filterType: 'text', type: 'contains', filter: value } };
        } else {
            model['Vendor Name'] = { filterType: 'text', type: 'contains', filter: value };
        }
        return model;
    }

    """,
    Output('vendors', "filterModel"),
    Input("search-box", "value"),
    State('vendors', "filterModel"),
)

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-vendors','data',allow_duplicate=True),
    Input('delete_vendor','n_clicks'),
    prevent_initial_call=True
)
def delete_vendor(n):
    if n>0:
        try:

            apis.delete_Vendor(flask.session['session_id'])

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','Vendor deleted successfully.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()
    
@callback(
    Output('refresh-vendors','data',allow_duplicate=True),
    Output('vendors','rowData'),
    Input('refresh-vendors','data'),
    prevent_initial_call=True
)
def refresh(n):
    if n == 1:
        df = apis.get_vendors_table()
        return 0, data_tabel(df,['view','edit','delete']).to_dict('records')
    elif n== 0:
        raise dash.exceptions.PreventUpdate()