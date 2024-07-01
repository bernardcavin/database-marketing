import dash
from dash import html, dcc, callback, Input, Output, State, ctx, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from utils.components import tabel, notif_fail,notif_success, data_tabel
from utils.models import Item, File
import pandas as pd
import dash_ag_grid as dag
import base64
from utils import apis
import flask
import uuid

def layout():

    df = apis.get_inventory_table()

    table_columns = [
        {
            "field": 'Photo',
            'cellRenderer':'Image',
            'width':100
        }
    ] + [
        {
            "headerName": col,
            "field": col,
            'filter': True 
        } for col in df.drop('id',axis=1).columns.to_list()[1:]
    ]

    table = dmc.Stack(
        [
            dcc.Store('refresh-inventory',data=0),
            dmc.Group(
                [
                    dmc.TextInput(
                        id='search-box',
                        leftSection=DashIconify(icon='quill:search',width=20),
                        placeholder='Search...'
                    ),

                    dmc.Button(
                        'Add Item',
                        leftSection=DashIconify(icon='mdi:add-bold',width=20),
                        id='add-item',
                        n_clicks=0,
                        color='green',
                        justify='flex-end'
                    )
                ],
                justify='space-between'
            ),
            tabel(
                'inventory',
                df,['view','edit','delete'],table_columns,rowHeight=100,height=500
            )
        ]
    )

    layout = dmc.Stack(
        [
            table
        ]
    )

    return layout

modal_add_item = dmc.Modal(
    opened=True,
    id='modal-add-item',
    padding='lg',
    title=dmc.Group(
        [
            DashIconify(icon='mdi:add-bold',width=30),
            dmc.Title('Add Item to Inventory',order=3)
        ],
        gap='sm'
    ),
    size='75%',
    children=dmc.Stack(
        [
            dmc.TextInput(
                label='Item Name',
                id='item_name',
                required=True
            ),
            dmc.Select(
                label='Category', 
                id='category',
                data=[
                    'Equipments',
                    'Electronics', 
                    'Office Supplies', 
                    'Raw Materials'
                ],
                required=True
            ),
            dmc.NumberInput(
                label='Quantity Available',
                decimalScale=0,
                min=0,
                id='quantity_available',
                required=True
            ),
            dmc.NumberInput(
                label='Unit Price',
                decimalScale=2,
                id='unit_price',
                required=True
            ),
            dmc.NumberInput(
                label='Total Value',
                decimalScale=2,
                id='total_value',
                required=True
            ),
            dmc.TextInput(
                label='Supplier Name',
                id='supplier_name',
                required=True
            ),
            dmc.TextInput(
                label='Supplier Contact',
                id='supplier_contact',
                required=True
            ),
            dmc.Select(
                label='Location',
                id='location',
                data=['Office','Outside Office'],
                required=True
            ),
            dmc.DatePicker(
                label='Date of Acquisition',
                id='date_of_acquisition'
            ),
            dmc.DatePicker(
                label='Expiration Date',
                id='expiration_date'
            ),
            dmc.Select(
                label='Condition',
                id='condition',
                data=['New','Used','Refurbished','Need Maintenance'],
                required=True
            ),
            dmc.Textarea(
                label='Notes',
                id='notes',
            ),
            dmc.Stack(
                [
                    dmc.Text('Item Photo',fw=500,size="sm"),
                    dmc.Paper(
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dcc.Upload(
                                            dmc.Button(
                                                'Upload Image',
                                                leftSection=DashIconify(icon='uil:image-upload',width=20)
                                            ),
                                            id='upload-item-photo',
                                            multiple=True
                                        ),
                                    ]
                                ),
                                dag.AgGrid(
                                    id='photos',
                                    columnDefs=[
                                        {'field':'File Encoding','headerName':'Image','cellRenderer':'Image','width':100},
                                        {'field':'File Name'},
                                        {'field':'Action','cellRenderer':'ActionButton','width':30,'minWidth':30,'pinned':'right'}
                                    ],
                                    style={'height':f"{101*2}px"},
                                    columnSize='sizeToFit',
                                    rowData=[],
                                    getRowId="params.data.id",
                                    dashGridOptions={
                                        'suppressCellFocus': True,
                                        'rowHeight':100,
                                        "noRowsOverlayComponent": "CustomNoRowsOverlay",
                                        "noRowsOverlayComponentParams": {
                                            "message": "No Uploaded Files",
                                            "fontSize": 12,
                                        },
                                        "loadingOverlayComponent": "CustomNoRowsOverlay",
                                        "loadingOverlayComponentParams": {
                                            "message": "No Uploaded Files",
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
                    dmc.Text('Item Documents',fw=500,size="sm"),
                    dmc.Paper(
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dcc.Upload(
                                            dmc.Button(
                                                'Upload Files',
                                                leftSection=DashIconify(icon='material-symbols:upload-file',width=20)
                                            ),
                                            id='upload-item-files',
                                            multiple=True
                                        ),
                                    ]
                                ),
                                dag.AgGrid(
                                    id='files',
                                    columnDefs=[
                                        {'field':'Icon','cellRenderer':'Icon','width':10},
                                        {'field':'File Name'},
                                        {'field':'Action','cellRenderer':'ActionButton','width':30,'minWidth':30,'pinned':'right'},
                                    ],
                                    style={'height':f"{41*5}px"},
                                    columnSize='sizeToFit',
                                    rowData=[],
                                    getRowId="params.data.id",
                                    dashGridOptions={
                                        'suppressCellFocus': True,
                                        'rowHeight':40,
                                        "noRowsOverlayComponent": "CustomNoRowsOverlay",
                                        "noRowsOverlayComponentParams": {
                                            "message": "No Uploaded Files",
                                            "fontSize": 12,
                                        },
                                        "loadingOverlayComponent": "CustomNoRowsOverlay",
                                        "loadingOverlayComponentParams": {
                                            "message": "No Uploaded Files",
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
            dmc.Button(
                'Add Item',
                leftSection=DashIconify(icon='mdi:add-bold',width=20),
                id='form-add-item',
                n_clicks=0,
                color='green',
            ),
        ]

    ),
)

def modal_delete_item(item_id):

    item_obj = Item.query.filter(Item.item_id == item_id).first()

    flask.session['session_id'] = item_obj.item_id

    modal_delete_item = dmc.Modal(
        title=dmc.Group(
            [
                DashIconify(icon="material-symbols:delete",width=30),
                dmc.Title(f'Delete Item',order=3)
            ],
            gap='sm'
        ),
        centered=True,
        zIndex=10000,
        children=dmc.Stack([
            dmc.Text(f'Are you sure you want to delete {item_obj.item_name}?'),
            dmc.Group([
                dmc.Button(
                    'Yes, delete',
                    color="red",
                    id="delete_item",
                    n_clicks=0
                ),
            ], justify='flex-end')
        ], gap='xl', style={'padding-top':20}),
        size='40%',
        style={'padding':20},
        opened=True)
    
    return modal_delete_item

def modal_edit_item(item_id):

    flask.session['session_id'] = str(uuid.uuid4())

    item_obj = Item.query.filter(Item.item_id == item_id).first()

    photos_records = []
    files_records = []

    for file in item_obj.files:

        if file.file_type == 'Photo':

            base64_string = base64.b64encode(file.content).decode('utf-8')
            image = 'data:image/png;base64,'+base64_string

            photos_records.append(
                {
                    'id':file.file_id,
                    'File Encoding':image,
                    'File Name': file.file_name,
                    'Action':['delete_existing']
                }
            )

        elif file.file_type == 'File':

            files_records.append(
                {
                    'id':file.file_id,
                    'Icon':'mdi:file',
                    'File Name': file.file_name,
                    'Action':['delete_existing']
                }
            )

        modal_edit_item = dmc.Modal(
            opened=True,
            id='modal-edit-item',
            padding='lg',
            title=dmc.Group(
                [
                    DashIconify(icon="tabler:edit",width=30),
                    dmc.Title(f'Edit {item_obj.item_name}',order=3)
                ],
                gap='sm'
            ),
            size='75%',
            children=dmc.Stack(
                [
                    dmc.TextInput(
                        label='Item Id',
                        id='item_id',
                        disabled=True,
                        value=item_obj.item_id
                    ),
                    dmc.TextInput(
                        label='Item Name',
                        id='item_name',
                        required=True,
                        value=item_obj.item_name
                    ),
                    dmc.Select(
                        label='Category', 
                        id='category',
                        data=[
                            'Equipments',
                            'Electronics', 
                            'Office Supplies', 
                            'Raw Materials'
                        ],
                        required=True,
                        value=item_obj.category
                    ),
                    dmc.NumberInput(
                        label='Quantity Available',
                        decimalScale=0,
                        min=0,
                        id='quantity_available',
                        required=True,
                        value=item_obj.quantity_available
                    ),
                    dmc.NumberInput(
                        label='Unit Price',
                        decimalScale=2,
                        id='unit_price',
                        required=True,
                        value=item_obj.unit_price
                    ),
                    dmc.NumberInput(
                        label='Total Value',
                        decimalScale=2,
                        id='total_value',
                        required=True,
                        value=item_obj.total_value
                    ),
                    dmc.TextInput(
                        label='Supplier Name',
                        id='supplier_name',
                        required=True,
                        value=item_obj.supplier_name
                    ),
                    dmc.TextInput(
                        label='Supplier Contact',
                        id='supplier_contact',
                        required=True,
                        value=item_obj.supplier_contact
                    ),
                    dmc.Select(
                        label='Location',
                        id='location',
                        data=['Office','Outside Office'],
                        required=True,
                        value=item_obj.location
                    ),
                    dmc.DatePicker(
                        label='Date of Acquisition',
                        id='date_of_acquisition',
                        value=item_obj.date_of_acquisition
                    ),
                    dmc.DatePicker(
                        label='Expiration Date',
                        id='expiration_date',
                        value=item_obj.expiration_date
                    ),
                    dmc.Select(
                        label='Condition',
                        id='condition',
                        data=['New','Used','Refurbished','Need Maintenance'],
                        required=True,
                        value=item_obj.condition
                    ),
                    dmc.Textarea(
                        label='Notes',
                        id='notes',
                        value=item_obj.notes
                    ),
                    dmc.Stack(
                        [
                            dmc.Text('Item Photo',fw=500,size="sm"),
                            dmc.Paper(
                                dmc.Stack(
                                    [
                                        dmc.Group(
                                            [
                                                dcc.Upload(
                                                    dmc.Button(
                                                        'Upload Image',
                                                        leftSection=DashIconify(icon='uil:image-upload',width=20)
                                                    ),
                                                    id='upload-item-photo',
                                                    multiple=True
                                                ),
                                            ]
                                        ),
                                        dag.AgGrid(
                                            id='photos',
                                            columnDefs=[
                                                {'field':'File Encoding','headerName':'Image','cellRenderer':'Image','width':100},
                                                {'field':'File Name'},
                                                {'field':'Action','cellRenderer':'ActionButton','width':30,'minWidth':30,'pinned':'right'}
                                            ],
                                            style={'height':f"{101*2}px"},
                                            columnSize='sizeToFit',
                                            rowData=photos_records,
                                            getRowId="params.data.id",
                                            dashGridOptions={
                                                'suppressCellFocus': True,
                                                'rowHeight':100,
                                                "noRowsOverlayComponent": "CustomNoRowsOverlay",
                                                "noRowsOverlayComponentParams": {
                                                    "message": "No Uploaded Files",
                                                    "fontSize": 12,
                                                },
                                                "loadingOverlayComponent": "CustomNoRowsOverlay",
                                                "loadingOverlayComponentParams": {
                                                    "message": "No Uploaded Files",
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
                            dmc.Text('Item Documents',fw=500,size="sm"),
                            dmc.Paper(
                                dmc.Stack(
                                    [
                                        dmc.Group(
                                            [
                                                dcc.Upload(
                                                    dmc.Button(
                                                        'Upload Files',
                                                        leftSection=DashIconify(icon='material-symbols:upload-file',width=20)
                                                    ),
                                                    id='upload-item-files',
                                                    multiple=True
                                                ),
                                            ]
                                        ),
                                        dag.AgGrid(
                                            id='files',
                                            columnDefs=[
                                                {'field':'Icon','cellRenderer':'Icon','width':10},
                                                {'field':'File Name'},
                                                {'field':'Action','cellRenderer':'ActionButton','width':30,'minWidth':30,'pinned':'right'},
                                            ],
                                            style={'height':f"{41*5}px"},
                                            columnSize='sizeToFit',
                                            rowData=files_records,
                                            getRowId="params.data.id",
                                            dashGridOptions={
                                                'suppressCellFocus': True,
                                                'rowHeight':40,
                                                "noRowsOverlayComponent": "CustomNoRowsOverlay",
                                                "noRowsOverlayComponentParams": {
                                                    "message": "No Uploaded Files",
                                                    "fontSize": 12,
                                                },
                                                "loadingOverlayComponent": "CustomNoRowsOverlay",
                                                "loadingOverlayComponentParams": {
                                                    "message": "No Uploaded Files",
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
                    dmc.Button(
                        'Save Changes',
                        leftSection=DashIconify(icon='material-symbols:save',width=20),
                        id='form-edit-item',
                        n_clicks=0,
                        color='green',
                    ),
                ]

            ),
        )


    return modal_edit_item

def modal_view_item(item_id):

    item_obj = Item.query.filter(Item.item_id == item_id).first()

    photos_records = []
    files_records = []

    for file in item_obj.files:

        if file.file_type == 'Photo':

            base64_string = base64.b64encode(file.content).decode('utf-8')
            image = 'data:image/png;base64,'+base64_string

            photos_records.append(
                {
                    'id':file.file_id,
                    'File Encoding':image,
                    'File Name': file.file_name,
                    'Action':['delete_existing']
                }
            )

        elif file.file_type == 'File':

            files_records.append(
                {
                    'id':file.file_id,
                    'Icon':'mdi:file',
                    'File Name': file.file_name,
                    'Action':['download']
                }
            )

    modal_view_item = dmc.Modal(
        opened=True,
        id='modal-view-item',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon="carbon:view-filled",width=30),
                dmc.Title(f'{item_obj.item_name}',order=3)
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
                                    dmc.TableTd('Item Id'),
                                    dmc.TableTd(str(item_obj.item_id))
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Item Name'),
                                    dmc.TableTd(item_obj.item_name)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Category'),
                                    dmc.TableTd(item_obj.category)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Quantity Available'),
                                    dmc.TableTd(str(item_obj.quantity_available))
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Unit Price'),
                                    dmc.TableTd(str(item_obj.unit_price))
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Total Value'),
                                    dmc.TableTd(str(item_obj.total_value))
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Supplier Name'),
                                    dmc.TableTd(item_obj.supplier_name)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Supplier Contact'),
                                    dmc.TableTd(item_obj.supplier_contact)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Location'),
                                    dmc.TableTd(item_obj.location)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Date of Acquisition'),
                                    dmc.TableTd(item_obj.date_of_acquisition)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Expiration Date'),
                                    dmc.TableTd(item_obj.expiration_date)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Condition'),
                                    dmc.TableTd(item_obj.condition)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Notes'),
                                    dmc.TableTd(item_obj.notes)
                                ])
                            ]
                        )
                    ]
                ),
                dmc.Stack(
                    [
                        dmc.Text('Item Photo',fw=500,size="sm"),
                        dmc.Paper(
                            dmc.Carousel(
                                [
                                    dmc.CarouselSlide(
                                        dmc.Center(
                                            html.Img(
                                                src=records['File Encoding'],
                                                className='carousel-image'
                                            ),
                                        )
                                    ) for records in photos_records
                                ],
                                withIndicators=True,
                                align='start',
                                loop=True,
                                controlSize=40
                            ),
                            withBorder=True,
                            radius="sm",
                            p="sm"
                        ),
                    ],
                    gap=2
                ) if photos_records != [] else None,
                dmc.Stack(
                    [
                        dmc.Text('Item Documents',fw=500,size="sm"),
                        dcc.Download(id='download-file'),
                        dmc.Paper(
                            dmc.Stack(
                                [
                                    dag.AgGrid(
                                        id='view-files',
                                        columnDefs=[
                                            {'field':'Icon','cellRenderer':'Icon','width':10},
                                            {'field':'File Name'},
                                            {'field':'Action','cellRenderer':'ActionButton','width':30,'minWidth':30,'pinned':'right'},
                                        ],
                                        style={'height':f"{41*5}px"},
                                        columnSize='sizeToFit',
                                        rowData=files_records,
                                        getRowId="params.data.id",
                                        dashGridOptions={
                                            'suppressCellFocus': True,
                                            'rowHeight':40,
                                            "noRowsOverlayComponent": "CustomNoRowsOverlay",
                                            "noRowsOverlayComponentParams": {
                                                "message": "No Uploaded Files",
                                                "fontSize": 12,
                                            },
                                            "loadingOverlayComponent": "CustomNoRowsOverlay",
                                            "loadingOverlayComponentParams": {
                                                "message": "No Uploaded Files",
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
                ) if files_records != [] else None,
            ]

        ),
    )

    return modal_view_item

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('add-item','n_clicks'),
    prevent_initial_call=True
)
def open_modal_add_item(n):
    if n>0:
        flask.session['session_id'] = str(uuid.uuid4())
        return modal_add_item

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('inventory','cellRendererData'),
    prevent_initial_call=True
)
def open_modal_edit_and_delete(data):
    if data is not None:
        if data['value']=='edit':

            item_id = data['rowId']

            return modal_edit_item(item_id)
        
        if data['value']=='delete':

            item_id = data['rowId']

            return modal_delete_item(item_id)
        
        if data['value']=='view':

            item_id = data['rowId']

            return modal_view_item(item_id)

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('photos', 'rowTransaction', allow_duplicate=True),
    Input('upload-item-photo', 'contents'),
    State('upload-item-photo', 'filename'),
    prevent_initial_call=True
)
def add_image(list_of_contents,list_of_filenames):

    if list_of_contents != None:


        list_of_ids = apis.generate_id(len(list_of_filenames))

        apis.upload_file(list_of_ids, list_of_filenames, list_of_contents, 'Photo')

        df = pd.DataFrame(
            {
                'id':list_of_ids,
                'File Encoding':list_of_contents,
                'File Name': list_of_filenames,
                'Action':[['delete'] for i in list_of_filenames],
            }
        )

        return notif_success('Success','File(s) successfully uploaded.'), {'add':df.to_dict('records')}
    
    else:
        
        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('files', 'rowTransaction', allow_duplicate=True),
    Input('upload-item-files', 'contents'),
    State('upload-item-files', 'filename'),
    prevent_initial_call=True
)
def add_files(list_of_contents,list_of_filenames):

    if list_of_contents != None:

        try:

            list_of_ids = apis.generate_id(len(list_of_filenames))

            apis.upload_file(list_of_ids, list_of_filenames, list_of_contents, 'File')

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update

        df = pd.DataFrame(
            {
                'id':list_of_ids,
                'Icon':['mdi:file' for i in range(len(list_of_filenames))],
                'File Name': list_of_filenames,
                'Action':[['delete'] for i in list_of_filenames],
            }
        )

        return notif_success('Success','File(s) successfully uploaded.'), {'add':df.to_dict('records')}
    
    else:
        
        raise dash.exceptions.PreventUpdate()
     
@callback(
    Output('photos', 'rowTransaction'),
    Output('files', 'rowTransaction'),
    Input('photos', 'cellRendererData'),
    Input('files', 'cellRendererData'),
    prevent_initial_call=True
)
def delete_data_photos(n1,n2):

    data = ctx.triggered[0]['value']

    if data['value']=='delete':

        file_id = data['rowId']

        try:

            apis.delete_file(file_id)

        except Exception as err:

            return dash.no_update
    
    if data['value']=='delete_existing':

        file_id = data['rowId']
    
    output = {'remove':[{'id':file_id}]}

    if ctx.triggered_id=='photos':
        return output, dash.no_update
    elif ctx.triggered_id=='files':
        return dash.no_update, output

@callback(
    Output('download-file','data'),
    Input('view-files',"cellRendererData")
)
def download(data):

    if data is not None:

        if data['value']=='download':

            file_id = data['rowId']

            file = File.query.filter(File.file_id == file_id).first()

            output = dict(base64=True, content=base64.b64encode(file.content).decode(), filename=file.file_name)

        return output
        
    else:

        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-inventory','data',allow_duplicate=True),
    Input('form-add-item','n_clicks'),
    State('item_name','value'),
    State('category','value'),
    State('quantity_available','value'),
    State('unit_price','value'),
    State('total_value','value'),
    State('supplier_name','value'),
    State('supplier_contact','value'),
    State('location','value'),
    State('date_of_acquisition','value'),
    State('expiration_date','value'),
    State('condition','value'),
    State('notes','value'),
    State('photos','rowData'),
    State('files','rowData'),
    prevent_initial_call = True
)
def upload_data(n,item_name,category,quantity_available,unit_price,total_value,supplier_name,supplier_contact,location,date_of_acquisition, expiration_date, condition, notes, photos, files):
    if n>0:

        try:

            apis.add_Item(
                item_name,
                category,
                quantity_available,
                unit_price,
                total_value,
                supplier_name,
                supplier_contact,
                location,
                date_of_acquisition,
                expiration_date,
                condition,
                notes,
                flask.session['session_id']
            )

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update
        
        finally:

            del flask.session['session_id']

        return notif_success('Success','Item successfully added.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children'),
    Output('modal','children'),
    Output('refresh-inventory','data',allow_duplicate=True),
    Input('form-edit-item','n_clicks'),
    State('item_id','value'),
    State('item_name','value'),
    State('category','value'),
    State('quantity_available','value'),
    State('unit_price','value'),
    State('total_value','value'),
    State('supplier_name','value'),
    State('supplier_contact','value'),
    State('location','value'),
    State('date_of_acquisition','value'),
    State('expiration_date','value'),
    State('condition','value'),
    State('notes','value'),
    State('photos','rowData'),
    State('files','rowData'),
    prevent_initial_call = True
)
def edit_data(n,item_id,item_name,category,quantity_available,unit_price,total_value,supplier_name,supplier_contact,location,date_of_acquisition, expiration_date, condition, notes, photos, files):
    if n>0:

        try:

            apis.edit_Item(
                item_id,
                item_name,
                category,
                quantity_available,
                unit_price,
                total_value,
                supplier_name,
                supplier_contact,
                location,
                date_of_acquisition,
                expiration_date,
                condition,
                notes,
                photos,
                files,
                flask.session['session_id']
            )

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update
        
        finally:

            del flask.session['session_id']

        return notif_success('Success','Changes saved successfully.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

clientside_callback(
    """
    function updateFilterModel(value, model) {
        if (model === null || model === undefined) {
            model = { 'Item Name': { filterType: 'text', type: 'contains', filter: value } };
        } else {
            model['Item Name'] = { filterType: 'text', type: 'contains', filter: value };
        }
        return model;
    }

    """,
    Output('inventory', "filterModel"),
    Input("search-box", "value"),
    State('inventory', "filterModel"),
)

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-inventory','data',allow_duplicate=True),
    Input('delete_item','n_clicks'),
    prevent_initial_call=True
)
def delete_item(n):
    if n>0:

        try:

            apis.delete_Item(
                flask.session['session_id']
            )

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update
        
        finally:

            del flask.session['session_id']

        return notif_success('Success','Item deleted successfully.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()
    
@callback(
    Output('refresh-inventory','data',allow_duplicate=True),
    Output('inventory','rowData'),
    Input('refresh-inventory','data'),
    prevent_initial_call=True
)
def refresh(n):
    if n == 1:
        df = apis.get_inventory_table()
        return 0, data_tabel(df,['view','edit','delete']).to_dict('records')
    elif n== 0:
        raise dash.exceptions.PreventUpdate()
