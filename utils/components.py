
from dash import Input, Output, State, callback, ALL, clientside_callback, dcc, html
import dash_mantine_components as dmc
from furl import furl
from dash_iconify import DashIconify
import dash_ag_grid as dag
from flask_login import logout_user

PAGE_PATH = "/home"
HEADER_HEIGHT = 70
PADDING = 25
NAVBAR_WIDTH = 250
NAV_HEIGHT = 50
NAVBAR_COLOR = '#31393c'
GROUP_COLOR = '#3a4447'

class Page:
    __type__ = 'page'

    def __init__(self, name, path, icon, children, admin = False):
        
        self.name = name
        self.path = path
        self.icon = icon
        self.children = children
        self.admin = admin

class PageGroup:
    __type__ = 'pagegroup'

    def __init__(self, name, icon, pages, admin = False):
        
        self.name = name
        self.icon = icon
        self.pages = pages
        self.admin = admin

class HomePage:

    def __init__(self):

        self.navs = []
        self.pages = []
        self.locked = dmc.Center(
            dmc.Paper(
                dmc.Box(
                    dmc.Stack(
                        [
                            DashIconify(icon='mdi:eye-lock-outline',width=50),
                            dmc.Text('Sorry, this section is for admins only.')
                        ],
                        align='center'
                    )
                ),
                withBorder=True,
                radius='lg',
                p='lg'
            )
        )
        self.not_found = dmc.Center(
            dmc.Paper(
                dmc.Box(
                    dmc.Stack(
                        [
                            DashIconify(icon='tabler:error-404-off',width=50),
                            dmc.Text('This page does not exist.')
                        ],
                        align='center'
                    ),
                ),
                withBorder=True,
                radius='lg',
                p='lg'
            ),
        )

    def render_profile(self):

        from flask_login import current_user

        profile = dmc.HoverCard(
            shadow="md",
            position='top-end',
            withArrow=True,
            children=dmc.Group(
                [
                    dmc.ActionIcon(
                        DashIconify(icon='el:off'),
                        color='red',
                        id='logout',
                        n_clicks=0
                    )
                ]
            )
        )

        return profile

    def error_page(self, err):
        return dmc.Center(
            dmc.Paper(
                dmc.Box(
                    dmc.Stack(
                        [
                            DashIconify(icon='tabler:error-404-off',width=50),
                            dmc.Text('An error occured.'),
                            dmc.Code(str(err))
                        ],
                        align='center'
                    ),
                ),
                withBorder=True,
                radius='lg',
                p='lg' 
            ),
            h='100%'
        )

    def add(self, page):
        self.navs.append(
            page
        )
    
    def render_page(self, nav):

        layout = dmc.Stack(
            [
                dmc.Group(
                    [
                        DashIconify(icon = nav.icon, width=50),
                        dmc.Text(nav.name, fz=50,fw=100),
                    ],
                ),
                nav.children if not callable(nav.children) else nav.children()
            ]
        ) if isinstance(nav,Page) else nav

        return layout

    def initiate_callbacks(self):

        group_dict = {}
        navs = []
        groups = []

        for nav in self.navs:
        
            if nav.__type__ == 'page':

                self.pages.append(nav)
                navs.append(nav.path)

            elif nav.__type__ == 'pagegroup':

                for page in nav.pages:

                    group_dict[page.path]=nav.name

                    self.pages.append(page)
                    navs.append(page.path)
                
                groups.append(nav.name)

        page_dict = {
            item.path:item for item in self.pages
        }

        clientside_callback(
            """
            function updateLoadingState(href) {
                return null
            }
            """,
            Output("loading-overlay-dashboard", "className", allow_duplicate=True),
            Input('dashboard-url','href'),
            prevent_initial_call=True,
        )

        @callback(
            Output('subpage-container','children'),
            Output("loading-overlay-dashboard", "className"),
            Input('dashboard-url','href'),
        )
        def navigation(href):

            try:
                f = furl(href)
                nav_page_path = f.args['p']
            except:
                nav_page_path = 'home'

            from flask_login import current_user

            try:
                
                page_to_render = page_dict[nav_page_path]

                if isinstance(page_to_render,Page):

                    if page_to_render.admin:

                        if current_user.admin:

                            page_output = page_to_render
                        
                        else:

                            page_output = self.locked
                    
                    else:

                        page_output = page_to_render

            except Exception as err:

                page_output = self.error_page(err)
            
            page_output = self.render_page(page_output)         

            return page_output, 'fade-out'

        @callback(
            [Output(f'nav-phone-{nav}','active') for nav in navs]+[Output(f'nav-desktop-{nav}','active') for nav in navs]+[Output(f'group-phone-{group}','active') for group in groups]+[Output(f'group-desktop-{group}','value') for group in groups],
            [Input('dashboard-url','href'),tuple([State(f'nav-desktop-{nav}','id') for nav in navs]),tuple([State(f'group-desktop-{group}','id') for group in groups])],
        )
        def activate_nav(href, nav_ids, group_ids):

            try:
                f = furl(href)
                nav_page_path = f.args['p']
            except:
                nav_page_path = 'home'

            nav_output = [False for n in range(len(nav_ids))]
            group_output = [None for n in range(len(groups))]

            try:
                nav_output[[id.split('nav-desktop-')[1] for id in nav_ids].index(nav_page_path)] = True
                group_output[[group_id.split('group-desktop-')[1] for group_id in group_ids].index(group_dict[nav_page_path])] = group_dict[nav_page_path]

            except:
                pass

            return nav_output+nav_output+group_output+group_output

        clientside_callback(
            """
            function(n) {
                if (n>0){
                    if (window.innerWidth > 750) {
                        document.querySelector('.navbar').classList.toggle('closed');
                        document.querySelector('.container').classList.toggle('closed');
                        return window.dash_clientside.no_update;
                    } else {
                        document.getElementById("navbar").classList.remove("closed");
                        document.getElementById("container").classList.remove("closed");
                        document.getElementById("navbar").className +=" closed ";
                        document.getElementById("container").className +=" closed ";
                        return true
                    }
                }
                return window.dash_clientside.no_update;
                
            }
            """,
            Output("drawer-nav", 'opened'),
            Input('burger', 'n_clicks')
        )

    def render(self):

        def render_navigation(type):

            navigation = []

            for nav in self.navs:
            
                if nav.__type__ == 'page':

                    self.pages.append(nav)

                    from flask_login import current_user
                    
                    if  nav.admin:
                        
                        if current_user.admin:

                            navigation.append(
                                dmc.NavLink(
                                    label=nav.name,
                                    leftSection=DashIconify(icon=nav.icon, height=16),
                                    px=PADDING,
                                    variant='filled',
                                    id=f'nav-{type}-{nav.path}',
                                    href=f'?p={nav.path}',
                                    c='white',
                                    color='black',
                                    className='link',
                                    h=NAV_HEIGHT,
                                )
                            )

                    else:

                        navigation.append(
                            dmc.NavLink(
                                label=nav.name,
                                leftSection=DashIconify(icon=nav.icon, height=16),
                                px=PADDING,
                                variant='filled',
                                id=f'nav-{type}-{nav.path}',
                                href=f'?p={nav.path}',
                                c='white',
                                color='black',
                                className='link',
                                h=NAV_HEIGHT
                            )
                        )

                elif nav.__type__ == 'pagegroup':

                    group_pages = []

                    for page in nav.pages:

                        self.pages.append(page)

                        from flask_login import current_user

                        if  nav.admin:
                            
                            if current_user.admin:

                                group_pages.append(
                                    dmc.NavLink(
                                        label=page.name,
                                        leftSection=DashIconify(icon=page.icon, height=16),
                                        variant='filled',
                                        id=f'nav-{type}-{page.path}',
                                        href=f'?p={page.path}',
                                        c='white',
                                        color='black',
                                        className='link',
                                        h=NAV_HEIGHT,
                                        px=PADDING+10
                                    )
                                )

                        else:

                            group_pages.append(
                                dmc.NavLink(
                                    label=page.name,
                                    leftSection=DashIconify(icon=page.icon, height=16),
                                    variant='filled',
                                    id=f'nav-{type}-{page.path}',
                                    href=f'?p={page.path}',
                                    c='white',
                                    color='black',
                                    className='link',
                                    h=NAV_HEIGHT,
                                    px=PADDING+10
                                )
                            )

                    navigation.append(
                        dmc.Accordion(
                            chevronPosition="right",
                            variant="filled",
                            chevron=DashIconify(icon="bxs:chevron-up",color='white'),
                            p=0,
                            m=0,
                            children=dmc.AccordionItem(                  
                                [
                                    dmc.AccordionControl(
                                        dmc.NavLink(
                                            label=nav.name,
                                            leftSection=DashIconify(icon=nav.icon, height=16),
                                            px=PADDING,
                                            variant='filled',
                                            c='white',
                                            color='black',
                                            className='link',
                                        ),
                                        p=0,
                                        m=0,
                                        pr=10,
                                        className='link',
                                        h=NAV_HEIGHT,
                                    ),
                                    dmc.AccordionPanel(
                                        group_pages,
                                        p=0,
                                        m=0,
                                        bg=GROUP_COLOR,
                                    ),
                                ],
                                value=nav.name,
                                bg=NAVBAR_COLOR,
                                p=0,
                                m=0,
                            ),
                            id=f'group-{type}-{nav.name}'
                        )
                    )       

            return navigation

        layout = dmc.AppShell(
            [
                dcc.Location(id='dashboard-url', refresh=False),
                dmc.AppShellHeader(
                    dmc.Center(
                        dmc.Group(
                            [
                                dmc.Group(
                                    [
                                        dmc.ActionIcon(DashIconify(icon='iconamoon:menu-burger-horizontal-fill',width=30),id="burger",n_clicks=0,variant='transparent',color='black'),
                                        dmc.Image(
                                            src='assets/Logo APS 2.png',h=40
                                        ),
                                        dmc.Drawer(
                                            id="drawer-nav", p=0,m=0, size="70%", zIndex=10000, opened=False, children=render_navigation('phone'),styles={'content':{'background-color':NAVBAR_COLOR},'body':{'padding':0,'margin':0},'header':{'height':HEADER_HEIGHT}}
                                        ),
                                    ]
                                ),
                                self.render_profile()
                            ],
                            justify='space-between',
                            style={'width':'100%'}
                        ),
                        style={'width':'100%','height':HEADER_HEIGHT}
                    ), 
                    px=PADDING,
                ),
                dmc.AppShellNavbar(render_navigation('desktop'),bg=NAVBAR_COLOR,className='navbar closed', id='navbar'),
                dmc.AppShellMain(children=[
                    dmc.Container(
                        html.Div(
                            [
                                dmc.LoadingOverlay(visible=True,overlayProps={'bg':'white'},loaderProps={'type':'bars',"size": "xl",'color':NAVBAR_COLOR},id="loading-overlay-dashboard"),
                                html.Div(self.render_page(self.navs[0]),id='subpage-container')
                            ],
                        ),
                        p=0,
                        m=0,
                        fluid=True,
                        pos="relative",
                    )
                ],className='container closed', id='container',pos="relative"),
            ],
            header={"height": HEADER_HEIGHT},
            padding="xl",
            navbar={
                "width": NAVBAR_WIDTH,
            },
        )

        return layout
    
def data_tabel(
    df,
    action_buttons,
):
    if not df.empty:
        df['no'] =range(1,len(df)+1)
        df['Action'] = [action_buttons for i in range(1,len(df)+1)]

    return df

def tabel(
        id,
        df,
        action_buttons,
        columnDefs=None,
        height=600,
        rowHeight=40,
        columnSize='autoSize'
    ):

    index_column = {
        "headerName": "No.",
        "field": "no",
        "sortable": True,
        "pinned" : "left",
        "minWidth" : 70,
        "resizable": False,
    }

    action_column = {
        "headerName" : "Action",
        "field": "Action",
        "cellRenderer": "ActionButton",
        "pinned" : "right",
        'minWidth': len(action_buttons)*50,
        "resizable": False,
    }

    columnDefs = [
        {
            "headerName": col,
            "field": col,
            'filter': True 
        } for col in df.columns.to_list()
    ] if columnDefs is None else columnDefs

    df = data_tabel(df, action_buttons)

    grid = dag.AgGrid(
        id=id,
        columnDefs=[index_column]+columnDefs+[action_column],
        rowData=df.to_dict("records"),
        className='ag-theme-quartz',
        columnSize=columnSize,
        defaultColDef={
            "sortable": True,
            "editable": False,
            "resizable": True,
            "suppressMovable": True,
            "minWidth":0
        },
        dashGridOptions={
            'suppressCellFocus': True,
            "rowHeight": rowHeight,
            "pagination": True,
            "paginationPageSizeSelector": False,
            "domLayout": "autoHeight"
        },
        style={"height":None},
        getRowId='params.data.id'

    )
    return grid

def notif_success(title,msg):
    return dmc.Notification(
        id="succes-notif",
        title=title,
        message=msg,
        color="green",
        action="show",
        icon=DashIconify(icon="akar-icons:circle-check"),
    )

def notif_fail(title,msg):
    return dmc.Notification(
        id="fail-notif",
        title=title,
        message=msg,
        color="red",
        action="show",
        icon=DashIconify(icon="emojione-monotone:cross-mark"),
    )

@callback(
    Output('redirect','href'),
    Input('logout','n_clicks')
)
def logout(n):
    if n>0:
        logout_user()
        return '/login'