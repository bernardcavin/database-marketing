    
import dash
from dash import dcc, callback, Input, Output, State, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from utils.components import tabel, notif_fail,notif_success, data_tabel
from utils.models import NCNP
from utils import apis
import flask
import uuid
import numpy as np

def layout():

    df = apis.get_ncnps_table()

    table_columns = [
        {
            "headerName": col,
            "field": col,
            'filter': True 
        } for col in df.columns.to_list()[1:]
    ]

    table = dmc.Stack(
        [
            dcc.Store('refresh-ncnp',data=0),
            dmc.Group(
                [
                    dmc.TextInput(
                        id='search-box',
                        leftSection=DashIconify(icon='quill:search',width=20),
                        placeholder='Search...'
                    ),
                    dmc.Group(
                        [
                            dmc.Button(
                                'Tambah',
                                leftSection=DashIconify(icon='mdi:add-bold',width=20),
                                id='add-ncnp',
                                n_clicks=0,
                                color='green',
                                justify='flex-end'
                            ),
                            dcc.Upload(
                                dmc.Button(
                                    'Upload Excel',
                                    leftSection=DashIconify(icon='ic:round-upload-file',width=20),
                                    n_clicks=0,
                                    color='blue',
                                    justify='flex-end'
                                ),
                                id='upload-ncnp'
                            )
                        ]
                    )
                ],
                justify='space-between'
            ),
            tabel(
                'ncnp',
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


def modal_add_ncnp():

    ncnps = NCNP.query.all()

    modal_add_ncnp = dmc.Modal(
        opened=True,
        id='modal-add-ncnp',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon='mdi:add-bold',width=30),
                dmc.Title('Tambah NCNP',order=3)
            ],
            gap='sm'
        ),
        size='75%',
        children=dmc.Stack(
            [
                dmc.Group(
                    [
                        dmc.Select(
                            label='Regional',
                            id='regional-options',
                            required=True,
                            data=list(np.unique([ncnp.regional for ncnp in ncnps]))+['Lainnya'],
                            style={'flex': 1,'box-sizing': 'border-box'},
                        ),
                        dmc.TextInput(
                            id='regional',
                            label='Lainnya',
                            style={'box-sizing': 'border-box'},
                            w=200,
                            withAsterisk=True,
                            display='none'
                        )
                    ],
                ),
                dmc.Group(
                    [
                        dmc.Select(
                            label='Zona',
                            id='zona-options',
                            required=True,
                            data=list(np.unique([ncnp.regional for ncnp in ncnps]))+['Lainnya'],
                            style={'flex': 1,'box-sizing': 'border-box'},
                        ),
                        dmc.TextInput(
                            id='zona',
                            label='Lainnya',
                            style={'box-sizing': 'border-box'},
                            w=200,
                            withAsterisk=True,
                            display='none'
                        )
                        
                    ],
                ),
                dmc.Group(
                    [
                        dmc.Select(
                            label='Challenge Type',
                            id='challenge-options',
                            required=True,
                            data=list(np.unique([ncnp.zona for ncnp in ncnps]))+['Lainnya'],
                            style={'flex': 1,'box-sizing': 'border-box'},
                        ),
                        dmc.TextInput(
                            id='challenge_type',
                            label='Lainnya',
                            style={'box-sizing': 'border-box'},
                            w=200,
                            withAsterisk=True,
                            display='none'
                        )
                    ],
                ),
                dmc.Textarea(
                    label='Description',
                    id='description',
                ),
                dmc.TextInput(
                    label='PIC',
                    id='pic',
                    required=True
                ),
                dmc.Group(
                    [
                        dmc.Select(
                            label='Technology',
                            id='technology-options',
                            required=True,
                            data=list(np.unique([ncnp.zona for ncnp in ncnps]))+['Lainnya'],
                            style={'flex': 1,'box-sizing': 'border-box'},
                        ),
                        dmc.TextInput(
                            id='technology',
                            label='Lainnya',
                            style={'box-sizing': 'border-box'},
                            w=200,
                            withAsterisk=True,
                            display='none'
                        )
                    ],
                ),
                dmc.TextInput(
                    label='Provider',
                    id='provider',
                    required=True
                ),
                dmc.Button(
                    'Tambah',
                    leftSection=DashIconify(icon='mdi:add-bold',width=20),
                    id='form-add-ncnp',
                    n_clicks=0,
                    color='green',
                ),
            ]
        ),
    )

    return modal_add_ncnp

def modal_delete_ncnp(ncnp_id):

    ncnp_obj = NCNP.query.filter(NCNP.ncnp_id == ncnp_id).first()

    flask.session['session_id'] = ncnp_obj.ncnp_id

    modal_delete_ncnp = dmc.Modal(
        title=dmc.Group(
            [
                DashIconify(icon="material-symbols:delete",width=30),
                dmc.Title(f'Delete NCNP',order=3)
            ],
            gap='sm'
        ),
        centered=True,
        zIndex=10000,
        children=dmc.Stack([
            dmc.Text(f'Are you sure you want to delete this NCNP?'),
            dmc.Group([
                dmc.Button(
                    'Yes, delete',
                    color="red",
                    id="delete_ncnp",
                    n_clicks=0
                ),
            ], justify='flex-end')
        ], gap='xl', style={'padding-top':20}),
        size='40%',
        style={'padding':20},
        opened=True)
    
    return modal_delete_ncnp

def modal_edit_ncnp(ncnp_id):

    flask.session['session_id'] = str(uuid.uuid4())

    ncnp_obj = NCNP.query.filter(NCNP.ncnp_id == ncnp_id).first()

    ncnps = NCNP.query.all()

    modal_edit_ncnp = dmc.Modal(
        opened=True,
        id='modal-edit-ncnp',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon='mdi:add-bold',width=30),
                dmc.Title('Edit NCNP',order=3)
            ],
            gap='sm'
        ),
        size='75%',
        children=dmc.Stack(
            [
                dmc.TextInput(
                    label='NCNP Id',
                    id='ncnp_id',
                    required=True,
                    value=ncnp_obj.ncnp_id,
                    disabled=True
                ),
                dmc.Group(
                    [
                        dmc.Select(
                            label='Regional',
                            id='regional-options',
                            required=True,
                            data=list(np.unique([ncnp.regional for ncnp in ncnps]))+['Lainnya'],
                            style={'flex': 1,'box-sizing': 'border-box'},
                            value=ncnp_obj.regional,
                        ),
                        dmc.TextInput(
                            id='regional',
                            label='Lainnya',
                            style={'box-sizing': 'border-box'},
                            w=200,
                            withAsterisk=True,
                            value=ncnp_obj.regional,
                            display='none'
                        )
                    ],
                ),
                dmc.Group(
                    [
                        dmc.Select(
                            label='Zona',
                            id='zona-options',
                            required=True,
                            data=list(np.unique([ncnp.zona for ncnp in ncnps]))+['Lainnya'],
                            style={'flex': 1,'box-sizing': 'border-box'},
                            value=ncnp_obj.zona,
                        ),
                        dmc.TextInput(
                            id='zona',
                            label='Lainnya',
                            style={'box-sizing': 'border-box'},
                            w=200,
                            withAsterisk=True,
                            value=ncnp_obj.zona,
                            display='none'
                        )
                        
                    ],
                ),
                dmc.Group(
                    [
                        dmc.Select(
                            label='Challenge Type',
                            id='challenge-options',
                            required=True,
                            data=list(np.unique([ncnp.challenge_type for ncnp in ncnps]))+['Lainnya'],
                            style={'flex': 1,'box-sizing': 'border-box'},
                            value=ncnp_obj.challenge_type,
                        ),
                        dmc.TextInput(
                            id='challenge_type',
                            label='Lainnya',
                            style={'box-sizing': 'border-box'},
                            w=200,
                            withAsterisk=True,
                            value=ncnp_obj.challenge_type,
                            display='none'
                        )
                    ],
                ),
                dmc.Textarea(
                    label='Description',
                    id='description',
                    value=ncnp_obj.description
                ),
                dmc.TextInput(
                    label='PIC',
                    id='pic',
                    required=True,
                    value=ncnp_obj.pic
                ),
                dmc.Group(
                    [
                        dmc.Select(
                            label='Technology',
                            id='technology-options',
                            required=True,
                            data=list(np.unique([ncnp.technology for ncnp in ncnps]))+['Lainnya'],
                            style={'flex': 1,'box-sizing': 'border-box'},
                            value=ncnp_obj.technology,
                        ),
                        dmc.TextInput(
                            id='technology',
                            label='Lainnya',
                            style={'box-sizing': 'border-box'},
                            w=200,
                            withAsterisk=True,
                            value=ncnp_obj.technology,
                            display='none'
                        )
                    ],
                ),
                dmc.TextInput(
                    label='Provider',
                    id='provider',
                    required=True,
                    value=ncnp_obj.provider
                ),
                dmc.Button(
                    'Simpan Perubahan',
                    leftSection=DashIconify(icon='material-symbols:save',width=20),
                    id='form-edit-ncnp',
                    n_clicks=0,
                    color='green',
                ),
            ]
        ),
    )
    
    return modal_edit_ncnp

def modal_view_ncnp(ncnp_id):

    flask.session['session_id'] = str(uuid.uuid4())

    ncnp_obj = NCNP.query.filter(NCNP.ncnp_id == ncnp_id).first()

    modal_view_ncnp = dmc.Modal(
        opened=True,
        id='modal-view-ncnp',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon="carbon:view-filled",width=30),
                dmc.Title(f'NCNP {ncnp_obj.ncnp_id}',order=3)
            ],
            gap='sm'
        ),
        size='75%',
        children=
        dmc.Stack(
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
                                    dmc.TableTd('Regional'),
                                    dmc.TableTd(str(ncnp_obj.regional))
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Zona'),
                                    dmc.TableTd(ncnp_obj.zona)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Challenge Type'),
                                    dmc.TableTd(ncnp_obj.challenge_type)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Description'),
                                    dmc.TableTd(ncnp_obj.description)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('PIC'),
                                    dmc.TableTd(ncnp_obj.pic)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Technology'),
                                    dmc.TableTd(ncnp_obj.technology)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Provider'),
                                    dmc.TableTd(ncnp_obj.provider)
                                ]),
                                
                            ]
                        )
                    ]
                ),
            ]
        ),
    )

    return modal_view_ncnp

clientside_callback(
    """
    function update_lainnya(value) {
        if (value == 'Lainnya') {
            return ['', 'inline'];
        } else {
            return [value, 'none'];
        }
    }
    """,
    Output('regional', "value"),
    Output('regional', "display"),
    Input('regional-options', "value"),
    prevent_initial_call=True
)

clientside_callback(
    """
    function update_lainnya(value) {
        if (value == 'Lainnya') {
            return ['', 'inline'];
        } else {
            return [value, 'none'];
        }
    }
    """,
    Output('zona', "value"),
    Output('zona', "display"),
    Input('zona-options', "value"),
    prevent_initial_call=True
)

clientside_callback(
    """
    function update_lainnya(value) {
        if (value == 'Lainnya') {
            return ['', 'inline'];
        } else {
            return [value, 'none'];
        }
    }
    """,
    Output('technology', "value"),
    Output('technology', "display"),
    Input('technology-options', "value"),
    prevent_initial_call=True
)

clientside_callback(
    """
    function update_lainnya(value) {
        if (value == 'Lainnya') {
            return ['', 'inline'];
        } else {
            return [value, 'none'];
        }
    }
    """,
    Output('challenge_type', "value"),
    Output('challenge_type', "display"),
    Input('challenge-options', "value"),
    prevent_initial_call=True
)

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('add-ncnp','n_clicks'),
    prevent_initial_call=True
)
def open_modal_add_ncnp(n):
    if n>0:
        flask.session['session_id'] = str(uuid.uuid4())
        return modal_add_ncnp()

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('ncnp','cellRendererData'),
    prevent_initial_call=True
)
def open_modals(data):
    if data is not None:
        if data['value']=='edit':

            ncnp_id = data['rowId']

            return modal_edit_ncnp(ncnp_id)
        
        if data['value']=='delete':

            ncnp_id = data['rowId']

            return modal_delete_ncnp(ncnp_id)
        
        if data['value']=='view':

            ncnp_id = data['rowId']

            return modal_view_ncnp(ncnp_id)

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-ncnp','data',allow_duplicate=True),
    Input('form-add-ncnp','n_clicks'),
    State('regional','value'),
    State('zona','value'),
    State('challenge_type','value'),
    State('description','value'),
    State('pic','value'),
    State('technology','value'),
    State('provider','value'),
    prevent_initial_call = True
)
def upload_data(
    n,
    regional, 
    zona, 
    challenge_type, 
    description, 
    pic, 
    technology, 
    provider
):
    
    if n>0:

        try:

            apis.add_NCNP(
                regional, 
                zona, 
                challenge_type, 
                description, 
                pic, 
                technology, 
                provider
            )

            del flask.session['session_id']

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','NCNP successfully added.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-ncnp','data',allow_duplicate=True),
    Input('form-edit-ncnp','n_clicks'),
    State('ncnp_id','value'),
    State('regional','value'),
    State('zona','value'),
    State('challenge_type','value'),
    State('description','value'),
    State('pic','value'),
    State('technology','value'),
    State('provider','value'),
    prevent_initial_call = True
)
def edit_ncnp(
    n, 
    ncncp_id,
    regional, 
    zona, 
    challenge_type, 
    description, 
    pic, 
    technology, 
    provider
):
    if n>0:

        try:

            apis.edit_NCNP(
                ncncp_id,
                regional, 
                zona, 
                challenge_type, 
                description, 
                pic, 
                technology, 
                provider
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
            model = { 'NCNP Name': { filterType: 'text', type: 'contains', filter: value } };
        } else {
            model['NCNP Name'] = { filterType: 'text', type: 'contains', filter: value };
        }
        return model;
    }

    """,
    Output('ncnp', "filterModel"),
    Input("search-box", "value"),
    State('ncnp', "filterModel"),
)

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-ncnp','data',allow_duplicate=True),
    Input('delete_ncnp','n_clicks'),
    prevent_initial_call=True
)
def delete_ncnp(n):
    if n>0:
        try:

            apis.delete_NCNP(flask.session['session_id'])

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','Item deleted successfully.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()
    
@callback(
    Output('refresh-ncnp','data',allow_duplicate=True),
    Output('ncnp','rowData'),
    Input('refresh-ncnp','data'),
    prevent_initial_call=True
)
def refresh(n):
    if n == 1:
        df = apis.get_ncnps_table()
        return 0, data_tabel(df,['view','edit','delete']).to_dict('records')
    elif n== 0:
        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-ncnp','data',allow_duplicate=True),
    Input('upload-ncnp', 'contents'),
    State('upload-ncnp', 'filename'),
    prevent_initial_call=True
)
def upload_ncnp(contents, filename):

    if contents is not None:

        try:

            apis.add_bulk_ncnp(
                contents, filename
            )

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','NCNPs successfully added.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()