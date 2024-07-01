    
import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from utils.components import tabel, notif_fail,notif_success, data_tabel
from utils.models import OutgoingPurchaseOrder, Vendor, Product, OrderStatus
import dash_ag_grid as dag
from utils import apis
import flask
import uuid
import dash_quill

def layout():

    df = apis.get_outgoing_purchase_orders_table()

    table_columns = [
        {
            "headerName": col,
            "field": col,
            'filter': True 
        } for col in df.columns.to_list()[1:]
    ]

    table = dmc.Stack(
        [
            dcc.Store('refresh-outgoing-purchase-orders',data=0),
            dmc.Group(
                [
                    dmc.TextInput(
                        id='search-box',
                        leftSection=DashIconify(icon='quill:search',width=20),
                        placeholder='Search...'
                    ),

                    dmc.Button(
                        'Create Purchase Order',
                        leftSection=DashIconify(icon='mdi:add-bold',width=20),
                        id='create-outgoing_purchase_order',
                        n_clicks=0,
                        color='green',
                        justify='flex-end'
                    )
                ],
                justify='space-between'
            ),
            tabel(
                'outgoing-purchase-orders',
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

def modal_create_outgoing_purchase_order():
    return dmc.Modal(
        opened=True,
        id='modal-create-outgoing_purchase_order',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon='mdi:add-bold',width=30),
                dmc.Title('Create Purchase Order',order=3)
            ],
            gap='sm'
        ),
        size='75%',
        children=dmc.Stack(
            [
                dmc.TextInput(
                    label='PO Number',
                    id='po_no',
                    required=True,
                ),
                dmc.Select(
                    label='Vendor',
                    id='vendor_id',
                    data=[{'label':vendor.vendor_name,'value':vendor.vendor_id} for vendor in Vendor.query.all() ],
                    required=True
                ),
                dmc.Select(
                    label='Contact',
                    id='contact_id',
                    required=True,
                    placeholder='Contact Person or Attention'
                ),
                dmc.Stack(
                    [
                        dmc.Text('Items',fw=500,size="sm"),
                        dmc.Paper(
                            dmc.Stack(
                                [
                                    dmc.Select(
                                        id='product_id',
                                        label='Product',
                                        required=True
                                    ),
                                    dmc.TextInput(
                                        id='quantity',
                                        label='Quantity',
                                        required=True
                                    ),
                                    dmc.NumberInput(
                                        id='total_price',
                                        label='Total Price',
                                        required=True
                                    ),
                                    dmc.Select(
                                        id='po_currency',
                                        label='Currency',
                                        required=True,
                                        data=['USD','IDR'],
                                        value='USD'
                                    ),
                                    dmc.Group(
                                        dmc.Button(
                                            'Add',
                                            leftSection=DashIconify(icon='mdi:add-bold',width=20),
                                            id='add-po-item',
                                            n_clicks=0,
                                            color='green',
                                            bottom=0,
                                        ),
                                        justify='flex-end'
                                    ),
                                    dag.AgGrid(
                                        id='po-items',
                                        columnDefs=[
                                            {'field':header} for header in ['Product Name', 'Quantity', 'Unit Price', 'Total Price', 'Currency']
                                        ] + [{'field':'Action','cellRenderer':'ActionButton','width':90,'minWidth':90,'pinned':'right'}],
                                        columnSize='sizeToFit',
                                        rowData=[],
                                        getRowId="params.data.id",
                                        dashGridOptions={
                                            'suppressCellFocus': True,
                                            "noRowsOverlayComponent": "CustomNoRowsOverlay",
                                            "noRowsOverlayComponentParams": {
                                                "message": "No Items",
                                                "fontSize": 12,
                                            },
                                            "loadingOverlayComponent": "CustomNoRowsOverlay",
                                            "loadingOverlayComponentParams": {
                                                "message": "No Items",
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
                        dmc.Text('Notes',fw=500,size="sm"),
                        dash_quill.Quill(
                            id='notes',
                        ),
                    ],
                    gap=2
                ),
                dmc.Button(
                    'Create Purchase Order',
                    leftSection=DashIconify(icon='mdi:add-bold',width=20),
                    id='form-create-outgoing_purchase_order',
                    n_clicks=0,
                    color='green',
                ),
            ]
        ),
    )

def modal_delete_outgoing_purchase_order(po_id):

    po_obj = OutgoingPurchaseOrder.query.filter(OutgoingPurchaseOrder.po_id == po_id).first()

    flask.session['session_id'] = po_obj.po_id

    modal_delete_outgoing_purchase_order = dmc.Modal(
        title=dmc.Group(
            [
                DashIconify(icon="material-symbols:delete",width=30),
                dmc.Title(f'Delete PO',order=3)
            ],
            gap='sm'
        ),
        centered=True,
        zIndex=10000,
        children=dmc.Stack([
            dmc.Text(f'Are you sure you want to delete {po_obj.po_no}?'),
            dmc.Group([
                dmc.Button(
                    'Yes, delete',
                    color="red",
                    id="delete_outgoing_purchase_order",
                    n_clicks=0
                ),
            ], justify='flex-end')
        ], gap='xl', style={'padding-top':20}),
        size='50%',
        style={'padding':20},
        opened=True)
    
    return modal_delete_outgoing_purchase_order

def modal_edit_outgoing_purchase_order(po_id):

    flask.session['session_id'] = str(uuid.uuid4())

    po_obj = OutgoingPurchaseOrder.query.filter(OutgoingPurchaseOrder.po_id == po_id).first()

    items = []

    for item in po_obj.items:

        item = {
            'id':str(uuid.uuid4()),
            'product_id':item.product_id,
            'Product Name':item.product.product_name,
            'Quantity':item.quantity,
            'Unit Price':item.product.unit_price,
            'Total Price':item.total_price,
            'Currency':item.currency,
            'Action':['delete']
        }

        items.append(item)

    modal_edit_outgoing_purchase_order = dmc.Modal(
        opened=True,
        id='modal-edit-outgoing_purchase_order',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon="tabler:edit",width=30),
                dmc.Title(f'Edit Purchase Order',order=3)
            ],
            gap='sm'
        ),
        size='75%',
        children=dmc.Stack(
            [
                dmc.TextInput(
                    label='PO Id',
                    id='po_id',
                    required=True,
                    value=po_obj.po_id,
                    disabled=True
                ),
                dmc.TextInput(
                    label='PO Number',
                    id='po_no',
                    required=True,
                    value=po_obj.po_no
                ),
                dmc.Select(
                    label='Vendor',
                    id='vendor_id',
                    data=[{'label':vendor.vendor_name,'value':vendor.vendor_id} for vendor in Vendor.query.all()],
                    required=True,
                    value=po_obj.vendor_id
                ),
                dmc.Select(
                    label='Contact',
                    id='contact_id',
                    required=True,
                    placeholder='Contact Person or Attention',
                    value=po_obj.contact_id
                ),
                dmc.Stack(
                    [
                        dmc.Text('Items',fw=500,size="sm"),
                        dmc.Paper(
                            dmc.Stack(
                                [
                                    dmc.Select(
                                        id='product_id',
                                        label='Product',
                                        required=True
                                    ),
                                    dmc.TextInput(
                                        id='quantity',
                                        label='Quantity',
                                        required=True
                                    ),
                                    dmc.NumberInput(
                                        id='total_price',
                                        label='Total Price',
                                        required=True
                                    ),
                                    dmc.Select(
                                        id='po_currency',
                                        label='Currency',
                                        required=True,
                                        data=['USD','IDR'],
                                        value='USD'
                                    ),
                                    dmc.Group(
                                        dmc.Button(
                                            'Add',
                                            leftSection=DashIconify(icon='mdi:add-bold',width=20),
                                            id='add-po-item',
                                            n_clicks=0,
                                            color='green',
                                            bottom=0,
                                        ),
                                        justify='flex-end'
                                    ),
                                    dag.AgGrid(
                                        id='po-items',
                                        columnDefs=[
                                            {'field':header} for header in ['Product Name', 'Quantity', 'Unit Price', 'Total Price', 'Currency']
                                        ] + [{'field':'Action','cellRenderer':'ActionButton','width':90,'minWidth':90,'pinned':'right'}],
                                        columnSize='sizeToFit',
                                        rowData=items,
                                        getRowId="params.data.id",
                                        dashGridOptions={
                                            'suppressCellFocus': True,
                                            "noRowsOverlayComponent": "CustomNoRowsOverlay",
                                            "noRowsOverlayComponentParams": {
                                                "message": "No Items",
                                                "fontSize": 12,
                                            },
                                            "loadingOverlayComponent": "CustomNoRowsOverlay",
                                            "loadingOverlayComponentParams": {
                                                "message": "No Items",
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
                        dmc.Text('Notes',fw=500,size="sm"),
                        dash_quill.Quill(
                            id='notes',
                            value=po_obj.notes
                        ),
                    ],
                    gap=2
                ),
                dmc.Button(
                    'Save Changes',
                    leftSection=DashIconify(icon='material-symbols:save',width=20),
                    id='form-edit-outgoing-purchase-order',
                    n_clicks=0,
                    color='green',
                ),
            ]
        ),
    )

    return modal_edit_outgoing_purchase_order

def modal_view_outgoing_purchase_order(po_id):

    flask.session['session_id'] = str(po_id)

    po_obj = OutgoingPurchaseOrder.query.filter(OutgoingPurchaseOrder.po_id == po_id).first()

    display_po = apis.generate_po_pdf(po_obj)

    modal_view_outgoing_purchase_order = dmc.Modal(
        opened=True,
        id='modal-view-outgoing_purchase_order',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon="carbon:view-filled",width=30),
                html.Div(dmc.Title(f'{po_obj.po_no}',order=3,id='po_no'),id='po_print')
            ],
            gap='sm',
        ),
        size='full',
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
                                    dmc.TableTd('PO Id'),
                                    dmc.TableTd(str(po_obj.po_id),id='po_id')
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('PO Status'),
                                    dmc.TableTd(
                                        dmc.Group(
                                            [
                                                str(po_obj.status.value),
                                                dmc.Button(
                                                    'Approve',
                                                    id='approve',
                                                    leftSection=DashIconify(icon='material-symbols:order-approve',width=20),
                                                    color='blue',
                                                    n_clicks=0
                                                ) if str(po_obj.status.value) == 'ISSUED' else None,
                                            ],
                                        ),
                                        id='po_approval_status'
                                    )
                                ]),
                                
                            ]
                        )
                    ]
                ),
                dmc.Group(
                    [
                        dmc.Button(
                            'Download',
                            id='download',
                            leftSection=DashIconify(icon='ic:baseline-download',width=20),
                            color='green',
                            n_clicks=0
                        )
                    ],
                    justify='flex-end'
                ),
                dmc.Paper(
                    [
                        display_po
                    ],
                    withBorder=True,
                    p='sm',
                    radius=0,
                    id='print'
                ),
            ]

        ),
    )

    return modal_view_outgoing_purchase_order

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('create-outgoing_purchase_order','n_clicks'),
    prevent_initial_call=True
)
def open_modal_create_outgoing_purchase_order(n):
    if n>0:
        flask.session['session_id'] = str(uuid.uuid4())
        return modal_create_outgoing_purchase_order()

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('outgoing-purchase-orders','cellRendererData'),
    prevent_initial_call=True
)
def open_modals(data):
    if data is not None:

        po_id = data['rowId']

        if data['value']=='edit':

            return modal_edit_outgoing_purchase_order(po_id)
        
        if data['value']=='delete':

            return modal_delete_outgoing_purchase_order(po_id)
        
        if data['value']=='view':

            return modal_view_outgoing_purchase_order(po_id)

@callback(
    Output('contact_id','data'),
    Output('product_id','data'),
    Input('vendor_id','value'),
    prevent_initial_call = True
)
def put_data(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    contacts = [{'label':contact.name,'value':contact.contact_id} for contact in vendor.contacts]
    products = [{'label':f'{product.product_name} - {product.currency} {product.unit_price}','value':product.product_id} for product in vendor.products]
    return contacts,products

@callback(
    Output('po-items', 'rowTransaction', allow_duplicate=True),
    Output('product_id','value'),
    Output('quantity','value'),
    Output('total_price','value'),
    Output('po_currency','value'),
    Input('add-po-item', 'n_clicks'),
    State('product_id','value'),
    State('quantity','value'),
    State('total_price','value'),
    State('po_currency','value'),
    prevent_initial_call=True
)
def add_product(n,product_id,quantity, total_price, currency):

    if n >= 0 and all(arg not in [None,''] for arg in [product_id,quantity]):

        item = Product.query.get(product_id)

        contact = {
            'id':str(uuid.uuid4()),
            'product_id':item.product_id,
            'Product Name':item.product_name,
            'Quantity':quantity,
            'Unit Price':item.unit_price,
            'Total Price':total_price,
            'Currency':currency,
            'Action':['delete']
        }

        return {'add':[contact]}, '', '', '', ''
    
    else:
        
        raise dash.exceptions.PreventUpdate()

@callback(
    Output('po-items', 'rowTransaction'),
    Input('po-items', 'cellRendererData'),
    prevent_initial_call=True
)
def delete_product(data):
    
    if data['value']=='delete':

        file_id = data['rowId']
    
    output = {'remove':[{'id':file_id}]}

    return output

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-outgoing-purchase-orders','data',allow_duplicate=True),
    Input('form-create-outgoing_purchase_order','n_clicks'),
    State('vendor_id','value'),
    State('po_no','value'),
    State('contact_id','value'),
    State('po-items','rowData'),
    State('notes','value'),
    prevent_initial_call = True
)
def upload_data(n,vendor_id, po_no, contact_id, po_items, notes):
    if n>0:

        try:

            total_amount = sum(
                [
                    item['Total Price'] for item in po_items
                ]
            )

            if not all([item['Currency'] == po_items[0]['Currency'] for item in po_items]):
                raise Exception(
                    'Currencies must be the same.'
                )

            apis.add_OutgoingPurchaseOrder(
                vendor_id,
                po_no,
                total_amount,
                contact_id,
                po_items,
                notes
            )

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update
        
        finally:

            del flask.session['session_id']

        return notif_success('Success','Purchase order successfully created.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()


@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-outgoing-purchase-orders','data',allow_duplicate=True),
    Input('form-edit-outgoing-purchase-order','n_clicks'),
    State('po_id','value'),
    State('vendor_id','value'),
    State('po_no','value'),
    State('contact_id','value'),
    State('po-items','rowData'),
    State('notes','value'),
    prevent_initial_call = True
)
def edit_data(n,po_id,vendor_id, po_no, contact_id, po_items, notes):
    if n>0:

        try:

            total_amount = sum(
                [
                    item['Total Price'] for item in po_items
                ]
            )

            if not all([item['Currency'] == po_items[0]['Currency'] for item in po_items]):
                raise Exception(
                    'Currencies must be the same.'
                )

            apis.edit_OutgoingPurchaseOrder(
                po_id,
                vendor_id,
                po_no,
                total_amount,
                contact_id,
                po_items,
                notes
            )

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update
        
        finally:

            del flask.session['session_id']

        return notif_success('Success','Changes saved successfully.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('po_approval_status','children'),
    Output('refresh-outgoing-purchase-orders','data',allow_duplicate=True),
    Input('approve','n_clicks'),
    prevent_initial_call = True
)
def approve(n):
    if n>0:

        try:

            po_id = flask.session['session_id']

            apis.approve_OutgoingPurchaseOrder(
                po_id,
                OrderStatus.APPROVED
            )

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update
        
        finally:

            del flask.session['session_id']

        return notif_success('Success','Purchase Order approved.'), str(OrderStatus.APPROVED.value), 1

    else:

        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-outgoing-purchase-orders','data',allow_duplicate=True),
    Input('delete_outgoing_purchase_order','n_clicks'),
    prevent_initial_call=True
)
def delete_po(n):
    if n>0:
        try:

            apis.delete_OutgoingPurchaseOrder(flask.session['session_id'])

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','Purchase Order deleted successfully.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

clientside_callback(
    """
    function(n_clicks){
        if(n_clicks > 0){
            po_no = document.getElementById("po_print").value = document.getElementById("po_no").innerText;
            var opt = {
                margin: 1,
                filename: `${po_no}.pdf`,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 3},
                jsPDF: { unit: 'cm', format: 'a2', orientation: 'p' },
                pagebreak: { mode: ['avoid-all'] }
            };
            html2pdf().from(document.getElementById("print")).set(opt).save();
        }
    }
    """,
    Output('download','n_clicks'),
    Input('download','n_clicks'),
)
    
@callback(
    Output('refresh-outgoing-purchase-orders','data',allow_duplicate=True),
    Output('outgoing-purchase-orders','rowData'),
    Input('refresh-outgoing-purchase-orders','data'),
    prevent_initial_call=True
)
def refresh(n):
    if n == 1:
        df = apis.get_outgoing_purchase_orders_table()
        return 0, data_tabel(df,['view','edit','delete']).to_dict('records')
    elif n== 0:
        raise dash.exceptions.PreventUpdate()

