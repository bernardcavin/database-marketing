    
import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from utils.components import tabel, notif_fail,notif_success, data_tabel
from utils.models import Job
import dash_ag_grid as dag
from utils import apis
import flask
import uuid
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user

def layout():

    df = apis.get_jobs_table()

    table_columns = [
        {
            "headerName": col,
            "field": col,
            'filter': True 
        } for col in df.columns.to_list()[1:]
    ]

    table = dmc.Stack(
        [
            dcc.Store('refresh-jobs',data=0),
            dmc.Group(
                [
                    dmc.TextInput(
                        id='search-box',
                        leftSection=DashIconify(icon='quill:search',width=20),
                        placeholder='Search...'
                    ),

                    dmc.Button(
                        'Add Job',
                        leftSection=DashIconify(icon='mdi:add-bold',width=20),
                        id='add-job',
                        n_clicks=0,
                        color='green',
                        justify='flex-end'
                    )
                ],
                justify='space-between'
            ),
            tabel(
                'jobs',
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

modal_add_job = dmc.Modal(
    opened=True,
    id='modal-add-job',
    padding='lg',
    title=dmc.Group(
        [
            DashIconify(icon='mdi:add-bold',width=30),
            dmc.Title('Add Job',order=3)
        ],
        gap='sm'
    ),
    size='75%',
    children=dmc.Stack(
        [
            dmc.TextInput(
                label='Employe Name',
                id='name',
                required=True
            ),
            dmc.NumberInput(
                label='NIK',
                id='nik',
                required=True
            ),
            dmc.TextInput(
                label='Position',
                id='position',
                required=True
            ),
            dmc.TextInput(
                label='Email',
                id='email',
                required=True
            ),
            dmc.TextInput(
                label='Username',
                id='username',
                required=True
            ),
            dmc.PasswordInput(
                label='Password',
                id='password',
                required=True
            ),
            dmc.Select(
                label='Job Privilege',
                id='admin',
                data=['Admin','Not Admin'],
                value='Not Admin',
                required=True
            ),
            dmc.Button(
                'Add Job',
                leftSection=DashIconify(icon='mdi:add-bold',width=20),
                id='form-add-job',
                n_clicks=0,
                color='green',
            ),
        ]
    ),
)

def modal_delete_job(job_id):

    job_obj = Job.query.filter(Job.id == job_id).first()

    flask.session['session_id'] = job_obj.id

    modal_delete_job = dmc.Modal(
        title=dmc.Group(
            [
                DashIconify(icon="material-symbols:delete",width=30),
                dmc.Title(f'Delete Job',order=3)
            ],
            gap='sm'
        ),
        centered=True,
        zIndex=10000,
        children=dmc.Stack([
            dmc.Text(f'Are you sure you want to delete {job_obj.username}?'),
            dmc.Group([
                dmc.Button(
                    'Yes, delete',
                    color="red",
                    id="delete_job",
                    n_clicks=0
                ),
            ], justify='flex-end')
        ], gap='xl', style={'padding-top':20}),
        size='40%',
        style={'padding':20},
        opened=True)
    
    return modal_delete_job

def modal_edit_job(job_id):

    flask.session['session_id'] = str(uuid.uuid4())

    job_obj = Job.query.filter(Job.id == job_id).first()

    modal_edit_job = dmc.Modal(
        opened=True,
        id='modal-edit-job',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon="tabler:edit",width=30),
                dmc.Title(f'Edit Job',order=3)
            ],
            gap='sm'
        ),
        size='75%',
        children=dmc.Stack(
            [
                dmc.TextInput(
                    label='Job Id',
                    id='job_id',
                    disabled=True,
                    value=job_obj.id
                ),
                dmc.TextInput(
                    label='Employe Name',
                    id='name',
                    required=True,
                    value=job_obj.name
                ),
                dmc.NumberInput(
                    label='NIK',
                    id='nik',
                    required=True,
                    value=job_obj.nik
                ),
                dmc.TextInput(
                    label='Position',
                    id='position',
                    required=True,
                    value=job_obj.position
                ),
                dmc.TextInput(
                    label='Email',
                    id='email',
                    required=True,
                    value=job_obj.email
                ),
                dmc.TextInput(
                    label='Username',
                    id='username',
                    required=True,
                    value=job_obj.username
                ),
                dmc.PasswordInput(
                    label='Password',
                    id='password',
                    required=True
                ),
                dmc.Select(
                    label='Job Privilege',
                    id='admin',
                    data=['Admin','Not Admin'],
                    value='Admin' if job_obj.admin else 'Not Admin',
                    required=True
                ),
                dmc.Button(
                    'Save Changes',
                    leftSection=DashIconify(icon='material-symbols:save',width=20),
                    id='form-edit-job',
                    n_clicks=0,
                    color='green',
                ),
            ]
        )
    )

    return modal_edit_job

def modal_view_job(job_id):

    flask.session['session_id'] = str(uuid.uuid4())

    job_obj = Job.query.filter(Job.id == job_id).first()

    modal_view_job = dmc.Modal(
        opened=True,
        id='modal-view-job',
        padding='lg',
        title=dmc.Group(
            [
                DashIconify(icon="carbon:view-filled",width=30),
                dmc.Title(f'{job_obj.username}',order=3)
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
                                    dmc.TableTd('Job Id'),
                                    dmc.TableTd(str(job_obj.id))
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Employe Name'),
                                    dmc.TableTd(job_obj.name)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('NIK'),
                                    dmc.TableTd(job_obj.nik)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Position'),
                                    dmc.TableTd(job_obj.position)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Email'),
                                    dmc.TableTd(job_obj.email)
                                ]),
                                dmc.TableTr([
                                    dmc.TableTd('Job Privilege'),
                                    dmc.TableTd('Admin' if job_obj.admin else 'Not Admin')
                                ]),
                            ]
                        )
                    ]
                ),
            ]

        ),
    )

    return modal_view_job

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('add-job','n_clicks'),
    prevent_initial_call=True
)
def open_modal_add_job(n):
    if n>0:
        flask.session['session_id'] = str(uuid.uuid4())
        return modal_add_job

@callback(
    Output('modal','children',allow_duplicate=True),
    Input('jobs','cellRendererData'),
    prevent_initial_call=True
)
def open_modals(data):
    if data is not None:
        if data['value']=='edit':

            job_id = data['rowId']

            return modal_edit_job(job_id)
        
        if data['value']=='delete':

            job_id = data['rowId']

            return modal_delete_job(job_id)
        
        if data['value']=='view':

            job_id = data['rowId']

            return modal_view_job(job_id)

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-jobs','data',allow_duplicate=True),
    Input('form-add-job','n_clicks'),
    State('username','value'),
    State('password','value'),
    State('admin','value'),
    State('name','value'),
    State('nik','value'),
    State('position','value'),
    State('email','value'),
    prevent_initial_call = True
)
def upload_data(n, username, password, admin, name, nik, position, email):
    
    if n>0:

        try:

            admin = True if admin == 'Admin' else False

            password = apis.apply_password_hash(password)

            apis.add_Job(
                username, 
                password, 
                admin, 
                name, 
                nik, 
                position, 
                email
            )

            del flask.session['session_id']

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','Job successfully added.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-jobs','data',allow_duplicate=True),
    Input('form-edit-job','n_clicks'),
    State('job_id','value'),
    State('username','value'),
    State('password','value'),
    State('admin','value'),
    State('name','value'),
    State('nik','value'),
    State('position','value'),
    State('email','value'),
    prevent_initial_call = True
)
def edit_job(n, job_id, username, password, admin, name, nik, position, email):
    if n>0:

        try:

            admin = True if admin == 'Admin' else False

            password = apis.apply_password_hash(password)

            apis.edit_Job(
                job_id,
                username, 
                password, 
                admin, 
                name, 
                nik, 
                position, 
                email
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
            model = { 'Job Name': { filterType: 'text', type: 'contains', filter: value } };
        } else {
            model['Job Name'] = { filterType: 'text', type: 'contains', filter: value };
        }
        return model;
    }

    """,
    Output('jobs', "filterModel"),
    Input("search-box", "value"),
    State('jobs', "filterModel"),
)

@callback(
    Output('notif','children',allow_duplicate=True),
    Output('modal','children',allow_duplicate=True),
    Output('refresh-jobs','data',allow_duplicate=True),
    Input('delete_job','n_clicks'),
    prevent_initial_call=True
)
def delete_job(n):
    if n>0:
        try:

            apis.delete_Job(flask.session['session_id'])

        except Exception as err:

            return notif_fail('Error',f'An error occured. {err}'), dash.no_update, dash.no_update

        return notif_success('Success','Item deleted successfully.'), None, 1

    else:

        raise dash.exceptions.PreventUpdate()
    
@callback(
    Output('refresh-jobs','data',allow_duplicate=True),
    Output('jobs','rowData'),
    Input('refresh-jobs','data'),
    prevent_initial_call=True
)
def refresh(n):
    if n == 1:
        df = apis.get_jobs_table()
        return 0, data_tabel(df,['view','edit','delete']).to_dict('records')
    elif n== 0:
        raise dash.exceptions.PreventUpdate()