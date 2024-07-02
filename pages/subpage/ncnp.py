    
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

    df = apis.get_ncnp_table()

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
                    dmc.Button(
                        'Tambah',
                        leftSection=DashIconify(icon='mdi:add-bold',width=20),
                        id='add-ncnp',
                        n_clicks=0,
                        color='green',
                        justify='flex-end'
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


def modal_add_ncnp(ncnp_id):

    ncnps = NCNP.query.all()

    modal_add_ncnp = dmc.Modal(
    opened=True,
    id='modal-add-ncnp',
    padding='lg',
    title=dmc.Group(
        [
            DashIconify(icon='mdi:add-bold',width=30),
            dmc.Title('Tambah Hazard Observation Card',order=3)
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
                        data=np.unique([ncnp.regional for ncnp in ncnps])+['Lainnya'],
                        style={'flex': 1,'box-sizing': 'border-box'},
                    ),
                    dmc.TextInput(
                        id='regional',
                        label='Lainnya',
                        style={'box-sizing': 'border-box'},
                        w=200,
                        withAsterisk=True
                    )
                    
                ],
            ),
            
            
            dmc.Group(
                [
                    dmc.DatePicker(
                        label='Tanggal',
                        id='tanggal',
                        style={'flex': 1,'box-sizing': 'border-box'},
                        required=True
                    ),
                    dmc.TimeInput(
                        id='waktu',
                        label='Waktu',
                        style={'box-sizing': 'border-box'},
                        w=150,
                        withAsterisk=True
                    )
                    
                ],
            ),
            dmc.Textarea(
                label='Temuan',
                id='temuan',
                required=True
            ),
            dmc.CheckboxGroup(
                id="bahaya",
                label="Bahaya",
                withAsterisk=True,
                children=dmc.Stack(
                    [
                        dmc.Paper(
                            dmc.Stack(
                                [
                                    dmc.Group(
                                        [
                                            dmc.Checkbox(
                                                label='Bahaya Fisik',id='check_bahaya_fisik', value='bahaya_fisik'
                                            ),
                                            dmc.TextInput(
                                                id='bahaya_fisik',
                                                w='100%', display='none'
                                            ),
                                        ]
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Checkbox(
                                                label='Bahaya Kimia',id='check_bahaya_kimia', value='bahaya_kimia'
                                            ),
                                            dmc.TextInput(
                                                id='bahaya_kimia',
                                                w='100%', display='none'
                                            )
                                        ]
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Checkbox(
                                                label='Bahaya Biologi',id='check_bahaya_biologi', value='bahaya_biologi'
                                            ),
                                            dmc.TextInput(
                                                id='bahaya_biologi',
                                                w='100%', display='none'
                                            )
                                        ]
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Checkbox(
                                                label='Bahaya Ergonomi',id='check_bahaya_ergonomi', value='bahaya_ergonomi'
                                            ),
                                            dmc.TextInput(
                                                id='bahaya_ergonomi',
                                                w='100%', display='none'
                                            )
                                        ]
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Checkbox(
                                                label='Bahaya Psikososial',id='check_bahaya_psikososial', value='psikososial'
                                            ),
                                            dmc.TextInput(
                                                id='bahaya_psikososial',
                                                w='100%', display='none'
                                            )
                                        ]
                                    )
                                ]
                            ),
                            p='md',
                            withBorder=True,
                            radius='sm'
                        )
                    ],
                    gap=2
                ),
            ),
            dmc.Textarea(
                label='Resiko Potensial',
                id='resiko_potensial',
                required=True
            ),
            dmc.Textarea(
                label='Penyebab',
                id='penyebab',
                required=True
            ),
            dmc.CheckboxGroup(
                id="pengendalian",
                label="Pengendalian",
                withAsterisk=True,
                children=dmc.Stack(
                    [
                        dmc.Paper(
                            dmc.Stack(
                                [
                                    dmc.Checkbox(
                                        label='Eliminiasi', value='Eliminiasi'
                                    ),
                                    dmc.Checkbox(
                                        label='Substitusi', value='Substitusi'
                                    ),
                                    dmc.Checkbox(
                                        label='Minimalisasi', value='Minimalisasi'
                                    ),
                                    dmc.Checkbox(
                                        label='Pelatihan', value='Pelatihan'
                                    ),
                                    dmc.Checkbox(
                                        label='APD', value='APD'
                                    ),
                                ]
                            ),
                            p='md',
                            withBorder=True,
                            radius='sm'
                        )
                    ]
                )
            ),
            dmc.Textarea(
                label='Tindakan Perbaikan',
                id='tindakan_perbaikan',
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

    lbahaya = ['bahaya_fisik','bahaya_kimia', 'bahaya_biologi', 'bahaya_ergonomi', 'bahaya_psikososial']
    value_bahaya = []

    for bahaya in lbahaya:
        if getattr(ncnp_obj,bahaya) not in [None,'']:
            value_bahaya.append(bahaya)
    
    modal_edit_ncnp = dmc.Modal(
        opened=True,
        id='modal-edit-ncnp',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon="tabler:edit",width=30),
                dmc.Title(f'Edit Hazard Observation Card',order=3)
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
                dmc.TextInput(
                    label='Area',
                    id='area',
                    required=True,
                    value = ncnp_obj.area
                ),
                dmc.Group(
                    [
                        dmc.DatePicker(
                            label='Tanggal',
                            id='tanggal',
                            style={'flex': 1,'box-sizing': 'border-box'},
                            required=True,
                            value = ncnp_obj.hazard_tanggal_waktu.date()
                        ),
                        dmc.TimeInput(
                            id='waktu',
                            label='Waktu',
                            style={'box-sizing': 'border-box'},
                            w=150,
                            withAsterisk=True,
                            value=f'{ncnp_obj.hazard_tanggal_waktu.hour}:{ncnp_obj.hazard_tanggal_waktu.minute}'
                        )
                    ],
                ),
                dmc.Textarea(
                    label='Temuan',
                    id='temuan',
                    required=True,
                    value=ncnp_obj.temuan
                ),
                dmc.CheckboxGroup(
                    id="bahaya",
                    label="Bahaya",
                    withAsterisk=True,
                    value=value_bahaya,
                    children=dmc.Stack(
                        [
                            dmc.Paper(
                                dmc.Stack(
                                    [
                                        dmc.Group(
                                            [
                                                dmc.Checkbox(
                                                    label='Bahaya Fisik',id='check_bahaya_fisik', value='bahaya_fisik'
                                                ),
                                                dmc.TextInput(
                                                    id='bahaya_fisik',
                                                    w='100%', display='none' if 'bahaya_fisik' not in value_bahaya else 'inline',
                                                    value=ncnp_obj.bahaya_fisik,
                                                    
                                                ),
                                            ]
                                        ),
                                        dmc.Group(
                                            [
                                                dmc.Checkbox(
                                                    label='Bahaya Kimia',id='check_bahaya_kimia', value='bahaya_kimia'
                                                ),
                                                dmc.TextInput(
                                                    id='bahaya_kimia',
                                                    w='100%', display='none' if 'bahaya_kimia' not in value_bahaya else 'inline',
                                                    value=ncnp_obj.bahaya_kimia
                                                )
                                            ]
                                        ),
                                        dmc.Group(
                                            [
                                                dmc.Checkbox(
                                                    label='Bahaya Biologi',id='check_bahaya_biologi', value='bahaya_biologi'
                                                ),
                                                dmc.TextInput(
                                                    id='bahaya_biologi',
                                                    w='100%', display='none' if 'bahaya_biologi' not in value_bahaya else 'inline',
                                                    value=ncnp_obj.bahaya_biologi
                                                )
                                            ]
                                        ),
                                        dmc.Group(
                                            [
                                                dmc.Checkbox(
                                                    label='Bahaya Ergonomi',id='check_bahaya_ergonomi', value='bahaya_ergonomi'
                                                ),
                                                dmc.TextInput(
                                                    id='bahaya_ergonomi',
                                                    w='100%', display='none' if 'bahaya_ergonomi' not in value_bahaya else 'inline',
                                                    value=ncnp_obj.bahaya_ergonomi
                                                )
                                            ]
                                        ),
                                        dmc.Group(
                                            [
                                                dmc.Checkbox(
                                                    label='Bahaya Psikososial',id='check_bahaya_psikososial', value='bahaya_psikososial'
                                                ),
                                                dmc.TextInput(
                                                    id='bahaya_psikososial',
                                                    w='100%', display='none' if 'bahaya_psikososial' not in value_bahaya else 'inline',
                                                    value=ncnp_obj.bahaya_psikososial
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                p='md',
                                withBorder=True,
                                radius='sm'
                            )
                        ],
                        gap=2
                    ),
                ),
                dmc.Textarea(
                    label='Resiko Potensial',
                    id='resiko_potensial',
                    required=True,
                    value=ncnp_obj.resiko_potensial
                ),
                dmc.Textarea(
                    label='Penyebab',
                    id='penyebab',
                    required=True,
                    value=ncnp_obj.penyebab
                ),
                dmc.CheckboxGroup(
                    id="pengendalian",
                    label="Pengendalian",
                    withAsterisk=True,
                    value=ncnp_obj.pengendalian,
                    children=dmc.Stack(
                        [
                            dmc.Paper(
                                dmc.Stack(
                                    [
                                        dmc.Checkbox(
                                            label='Eliminiasi', value='Eliminiasi'
                                        ),
                                        dmc.Checkbox(
                                            label='Substitusi', value='Substitusi'
                                        ),
                                        dmc.Checkbox(
                                            label='Minimalisasi', value='Minimalisasi'
                                        ),
                                        dmc.Checkbox(
                                            label='Pelatihan', value='Pelatihan'
                                        ),
                                        dmc.Checkbox(
                                            label='APD', value='APD'
                                        ),
                                    ]
                                ),
                                p='md',
                                withBorder=True,
                                radius='sm'
                            )
                        ]
                    )
                ),
                dmc.Textarea(
                    label='Tindakan Perbaikan',
                    id='tindakan_perbaikan',
                    value=ncnp_obj.tindakan_perbaikan,
                    required=True
                ),

                dmc.Button(
                    'Simpan Perubahan',
                    leftSection=DashIconify(icon='material-symbols:save',width=20),
                    id='form-edit-ncnp',
                    n_clicks=0,
                    color='green',
                ),
            ]
        )
    )

    return modal_edit_ncnp

def modal_view_ncnp(ncnp_id):

    flask.session['session_id'] = str(uuid.uuid4())

    ncnp_obj = NCNP.query.filter(NCNP.ncnp_id == ncnp_id).first()

    lbahaya = ['bahaya_fisik','bahaya_kimia', 'bahaya_biologi', 'bahaya_ergonomi', 'bahaya_psikososial']
    value_bahaya = []

    for bahaya in lbahaya:
        if getattr(ncnp_obj,bahaya) not in [None,'']:
            value_bahaya.append(bahaya)

    bahaya_content = dmc.List(
        [
            dmc.ListItem(
                dmc.Stack(
                    [
                        dmc.Text(bahaya.replace("_", " ").title(), fw=500),
                        dmc.Text(
                            getattr(ncnp_obj, bahaya)
                        ),
                    ],
                    gap=0
                )
            ) for bahaya in value_bahaya
        ]
    )

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
                                    dmc.TableTd('NCNP Id'),
                                    dmc.TableTd(str(ncnp_obj.ncnp_id))
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Area'),
                                    dmc.TableTd(ncnp_obj.area)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Tanggal/Waktu'),
                                    dmc.TableTd(ncnp_obj.hazard_tanggal_waktu.strftime('%d %B %Y / %H:%M WIB'))
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Bahaya'),
                                    dmc.TableTd(bahaya_content)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Resiko Potensial'),
                                    dmc.TableTd(ncnp_obj.resiko_potensial)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Penyebab'),
                                    dmc.TableTd(ncnp_obj.penyebab)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Pengendalian'),
                                    dmc.TableTd(dmc.List([dmc.ListItem(pengendalian) for pengendalian in ncnp_obj.pengendalian]))
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Tindakan Perbaikan'),
                                    dmc.TableTd(ncnp_obj.tindakan_perbaikan)
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
    function updateFilterModel(a,b,c,d,e) {
        let outputs = [];
        let values = [a, b, c, d, e]; // Assuming a, b, c, d, e are defined
        values.forEach(x => {
            outputs.push(x ? 'inline' : 'none');
        });
        return outputs;
    }

    """,
    Output('bahaya_fisik', "display"),
    Output('bahaya_kimia', "display"),
    Output('bahaya_biologi', "display"),
    Output('bahaya_ergonomi', "display"),
    Output('bahaya_psikososial', "display"),
    Input('check_bahaya_fisik', "checked"),
    Input('check_bahaya_kimia', "checked"),
    Input('check_bahaya_biologi', "checked"),
    Input('check_bahaya_ergonomi', "checked"),
    Input('check_bahaya_psikososial', "checked"),
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
        return modal_add_ncnp

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
    State('area','value'),
    State('tanggal','value'),
    State('waktu','value'),
    State('temuan','value'),
    State('bahaya_fisik','value'),
    State('bahaya_kimia','value'),
    State('bahaya_biologi','value'),
    State('bahaya_ergonomi','value'),
    State('bahaya_psikososial','value'),
    State('resiko_potensial','value'),
    State('penyebab','value'),
    State('pengendalian','value'),
    State('tindakan_perbaikan','value'),

    prevent_initial_call = True
)
def upload_data(
    n,
    area,
    hazard_tanggal,
    hazard_waktu,
    temuan,
    bahaya_fisik,
    bahaya_kimia,
    bahaya_biologi,
    bahaya_ergonomi,
    bahaya_psikososial,
    resiko_potensial,
    penyebab,
    pengendalian,
    tindakan_perbaikan
):
    
    if n>0:

        try:

            hazard_waktu_jam, hazard_waktu_menit = hazard_waktu.split(':')

            apis.add_NCNP(
                area,
                hazard_tanggal,
                hazard_waktu_jam,
                hazard_waktu_menit,
                temuan,
                bahaya_fisik,
                bahaya_kimia,
                bahaya_biologi,
                bahaya_ergonomi,
                bahaya_psikososial,
                resiko_potensial,
                penyebab,
                pengendalian,
                tindakan_perbaikan
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
    State('area','value'),
    State('tanggal','value'),
    State('waktu','value'),
    State('temuan','value'),
    State('bahaya_fisik','value'),
    State('bahaya_kimia','value'),
    State('bahaya_biologi','value'),
    State('bahaya_ergonomi','value'),
    State('bahaya_psikososial','value'),
    State('resiko_potensial','value'),
    State('penyebab','value'),
    State('pengendalian','value'),
    State('tindakan_perbaikan','value'),
    prevent_initial_call = True
)
def edit_ncnp(
    n, 
    ncnp_id, area,
    hazard_tanggal,
    hazard_waktu,
    temuan,
    bahaya_fisik,
    bahaya_kimia,
    bahaya_biologi,
    bahaya_ergonomi,
    bahaya_psikososial,
    resiko_potensial,
    penyebab,
    pengendalian,
    tindakan_perbaikan
):
    if n>0:

        try:

            hazard_waktu_jam, hazard_waktu_menit = hazard_waktu.split(':')

            apis.edit_NCNP(
                ncnp_id,
                area,
                hazard_tanggal,
                hazard_waktu_jam,
                hazard_waktu_menit,
                temuan,
                bahaya_fisik,
                bahaya_kimia,
                bahaya_biologi,
                bahaya_ergonomi,
                bahaya_psikososial,
                resiko_potensial,
                penyebab,
                pengendalian,
                tindakan_perbaikan
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
        df = apis.get_ncnp_table()
        return 0, data_tabel(df,['view','edit','delete']).to_dict('records')
    elif n== 0:
        raise dash.exceptions.PreventUpdate()