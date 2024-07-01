from sqlalchemy import create_engine, text, and_, or_
from sqlalchemy.orm import sessionmaker
from app import db
from utils.models import Item, File
import base64
import pandas as pd
import uuid
from utils.models import Item, File, TempFile, Vendor, Contact, Employee, Product, OutgoingPurchaseOrder, OutgoingPurchaseOrderItem, OrderStatus, HazardObservationCard, CompanyClient
from werkzeug.security import check_password_hash, generate_password_hash
import dash_mantine_components as dmc
from dash import html, dcc
from datetime import datetime

def get_clients_table():

    company_clients = CompanyClient.query.all()
    contact_clients = Contact.query.filter(and_(Contact.contact_type=='client',Contact.company_client_id==None)).all()

    id = []
    client_type = []
    client_name = []

    for client in (company_clients+contact_clients):
        if isinstance(client, CompanyClient):
            id.append(f'company;{client.client_id}')
            client_type.append('Company')
            client_name.append(client.company_name)
        if isinstance(client, Contact):
            id.append(f'individual;{client.contact_id}')
            client_type.append('Individual')
            client_name.append(client.name)

    df = pd.DataFrame(
        {
            'id':id,
            'Client Type':client_type,
            'Client Name / Company Name':client_name
        }
    )

    return df


def get_jobs_table():

    df = pd.read_sql_table(
        'jobs',
        db.engine
    )

    df.columns = ['id'] + [ get_display_name(tag) for tag in df.columns[1:] ]

    return df

def get_hocs_table():

    query = text("SELECT * FROM hocs WHERE employee_id = :employee_id")

    from flask_login import current_user

    params = {'employee_id': current_user.id}

    df = pd.read_sql_query(query, db.engine, params=params)

    df['HOC ID'] = df['hoc_id']
    df = df[['hoc_id','HOC ID','area','hazard_tanggal_waktu']]

    if not df.empty:
        df['hazard_tanggal_waktu'] = df['hazard_tanggal_waktu'].dt.strftime('%d %B %Y / %H:%M WIB')

    df.columns = ['id'] + [ get_display_name(tag) for tag in df.columns[1:] ]

    return df

def get_inventory_table():

    Session = sessionmaker(bind=db.engine)
    session = Session()

    try:
        items = session.query(Item).all()
        data = []
        for item in items:
            photo_file = next((file for file in item.files if file.file_type == 'Photo'), None)
            if photo_file:
                base64_string = base64.b64encode(photo_file.content).decode('utf-8')
                image = 'data:image/png;base64,'+base64_string
            else:
                image = 'assets/no-image.png'

            item_data = [item.item_id] + [image] + [getattr(item, column.name) for column in Item.__table__.columns[1:]]
            data.append(item_data)

        columns = ['id'] + ['Photo'] + [get_display_name(column.name) for column in Item.__table__.columns[1:]]
        df = pd.DataFrame(data, columns=columns)

    except Exception as err:
        print(err)

    finally:
        # Close the session
        session.close()

        return df

def get_vendors_table():

    df = pd.read_sql_table(
        'vendors',
        db.engine
    )

    df.columns = ['id'] + [ get_display_name(tag) for tag in df.columns[1:] ]

    return df

def get_outgoing_purchase_orders_table():

    df = pd.read_sql_table(
        'outgoing_purchase_orders',
        db.engine
    )
    df.drop(columns=['vendor_id','contact_id','notes'],inplace=True)

    df = df[df.columns.to_list()[:6]]

    df['order_date'] = df['order_date'].dt.strftime('%d %B %Y')

    df['issued_by'] = [Employee.query.get(employee_id).name for employee_id in df['issued_by'].to_list()]

    df.columns = ['id'] + [ get_display_name(tag) for tag in df.columns[1:]]
    

    return df

def get_employees_table():

    df = pd.read_sql_table(
        'employees',
        db.engine
    )

    df = pd.DataFrame(
        {
            'id':df['id'],
            'Username':df['username'],
            'Privilege':['Admin' if admin==1 else 'Not Admin' for admin in df['admin'].to_list()]
        }
    )

    return df

def get_display_name(tag):


    tag_display_name_mapping = {

        #inventory
        'item_name': 'Item Name',
        'category': 'Category',
        'quantity_available': 'Quantity Available',
        'unit_price': 'Unit Price',
        'total_value': 'Total Value',
        'supplier_name': 'Supplier Name',
        'supplier_contact': 'Supplier Contact',
        'location': 'Location',
        'date_of_acquisition': 'Date Of Acquisition',
        'expiration_date': 'Expiration Date',
        'condition': 'Condition',
        'notes': 'Notes',

        #clients
        'vendor_name':'Vendor Name',
        'vendor_address':'Vendor Address',
        'vendor_type':'Vendor Type',

        #po
        'po_no':'PO No',
        'order_date':'Order Date',
        'total_amount':'Total Amount',
        'status':'Status',
        'issued_by':'Issued By',

        #jobs
        'job_title':'Job Title',
        'plan_start_date':'Start Date (Plan)',
        'plan_end_date':'End Date (Plan)',
        'actual_start_date':'Start Date (Actual)',
        'actual_end_date':'End Date (Actual)',
        'job_service_type':'Job Service Type',
        'job_desc':'Job Description',

        #hoc
        'area':'Area',
        'hazard_tanggal_waktu':'Tanggal/Waktu',
        'additional_info':'Additional Info'
    }
    return tag_display_name_mapping.get(tag,tag)

def generate_id(amount=None):
    if amount==None:
        return str(uuid.uuid4())
    else:
        return [str(uuid.uuid4()) for i in range(amount)]

def upload_file(list_of_ids, list_of_filenames, list_of_contents, type):
        
    try:
    
        Session = sessionmaker(bind=db.engine)
        session = Session()

        file_objs = [
            TempFile(
                file_id,
                type,
                filename,
                base64.b64decode(contents.split(',')[1])
            ) for file_id, filename, contents in zip(list_of_ids,list_of_filenames,list_of_contents)
        ]

        session.add_all(
            file_objs
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err
    
    finally:
            
        session.close()

def delete_file(file_id):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        file = session.query(TempFile).filter(TempFile.file_id == file_id).first()

        session.delete(file)

        session.commit()

    except Exception as err:

        session.rollback()

        raise err
    
    finally:
        
        session.close()

def add_Item(
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
    session_id
):
    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        item = Item(
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
            notes
        )

        session.add(
            item
        )

        session.commit()

        temp_file_objs = session.query(TempFile).filter(TempFile.user_session == session_id).all()

        session.add_all(
            [File(item.item_id, file.file_type, file.file_name, file.content) for file in temp_file_objs]
        )

        for temp_file in temp_file_objs:
            session.delete(temp_file)

        session.commit()

    except Exception as err:

        session.rollback()

        raise err
    
    finally:

        session.close()

def edit_Item(
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
    session_id
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        item = session.query(Item).filter(Item.item_id == item_id).first()

        item.item_name = item_name
        item.category = category
        item.quantity_available = quantity_available
        item.unit_price = unit_price
        item.total_value = total_value
        item.supplier_name = supplier_name
        item.supplier_contact = supplier_contact
        item.location = location
        item.date_of_acquisition = date_of_acquisition
        item.expiration_date = expiration_date
        item.condition = condition
        item.notes = notes

        temp_file_objs = session.query(TempFile).filter(TempFile.employee_session == session_id).all()

        file_df = pd.DataFrame().from_records(photos+files)

        if not file_df.empty:

            for file_id in [f.file_id for f in item.files]:

                if not file_id in file_df['id'].to_list():

                    file_to_delete = session.query(File).filter(File.file_id == file_id).first()

                    session.delete(file_to_delete)

        else:

            for file_id in [f.file_id for f in item.files]:

                file_to_delete = session.query(File).filter(File.file_id == file_id).first()

                session.delete(file_to_delete)

        session.add_all(
            [File(item_id, file.file_type, file.file_name, file.content) for file in temp_file_objs]
        )

        for temp_file in temp_file_objs:
            session.delete(temp_file)

        session.commit()

    except Exception as err:

        session.rollback()

        raise err
    
    finally:

        session.close()

def delete_Item(
    item_id
):
    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        Item_to_delete = session.query(Item).filter(Item.item_id == item_id).first()

        session.delete(Item_to_delete)

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:
        
        session.close()

def add_OutgoingPurchaseOrder(
    vendor_id,
    po_no,
    total_amount,
    contact_id,
    po_items,
    notes
):
    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        from flask_login import current_user

        po = OutgoingPurchaseOrder(
            po_no,
            vendor_id,
            total_amount,
            contact_id,
            notes,
            issued_by=current_user.id,
        )

        session.add(
            po
        )

        session.commit()

        session.add_all(
            [
                OutgoingPurchaseOrderItem(
                    po.po_id,
                    item['product_id'],
                    item['Quantity'],
                    item['Total Price'],
                    item['Currency'],
                ) for item in po_items
            ]
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err
    
    finally:

        session.close()

def edit_OutgoingPurchaseOrder(
    po_id,
    vendor_id,
    po_no,
    total_amount,
    contact_id,
    po_items,
    notes
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        po = session.query(OutgoingPurchaseOrder).filter(OutgoingPurchaseOrder.po_id == po_id).first()
        
        po.vendor_id = vendor_id
        po.po_no = po_no
        po.total_amount = total_amount
        po.contact_id = contact_id
        po.notes = notes
        po.status = OrderStatus.ISSUED

        for item in po.items:
            session.delete(item)

        session.add_all(
            [
                OutgoingPurchaseOrderItem(
                    po.po_id,
                    item['product_id'],
                    item['Quantity'],
                    item['Total Price'],
                    item['Currency'],
                ) for item in po_items
            ]
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err
    
    finally:

        session.close()

def approve_OutgoingPurchaseOrder(
    po_id,
    approval
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        po = session.query(OutgoingPurchaseOrder).filter(OutgoingPurchaseOrder.po_id == po_id).first()
        
        from flask_login import current_user

        po.status = approval
        po.approved_by = current_user.id
        po.approved_date = datetime.now()

        session.add(
            po
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err
    
    finally:

        session.close()

def delete_OutgoingPurchaseOrder(
    po_id
):
    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        Po_to_delete = session.query(OutgoingPurchaseOrder).filter(OutgoingPurchaseOrder.po_id == po_id).first()
        
        session.delete(Po_to_delete)

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:
        
        session.close()

def add_Vendor(
    vendor_name,
    vendor_address,
    vendor_type,
    contacts,
    products,
    additonal_info
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        vendor = Vendor(
            vendor_name,
            vendor_address, 
            vendor_type,
            additonal_info
        )

        session.add(
            vendor
        )

        session.commit()

        session.add_all(
            [
                Contact(
                    vendor.vendor_id,
                    contact['name'],
                    contact['title'],
                    contact['email'],
                    contact['phone'],
                    contact['additional_info']
                ) for contact in contacts
            ] 
        )

        session.add_all(
            [
                Product(
                    vendor.vendor_id,
                    product['Product Name'],
                    product['Unit Price'],
                    product['Currency'],
                    product['Description']
                ) for product in products
            ] 
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:

        session.close()

def edit_Vendor(
    vendor_id,
    vendor_name,
    vendor_address,
    vendor_type,
    contacts,
    products,
    additional_info
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        vendor = session.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()

        vendor.vendor_name = vendor_name
        vendor.vendor_address = vendor_address
        vendor.vendor_type = vendor_type
        vendor.additional_info = additional_info

        for contact in vendor.contacts:
            session.delete(contact)
    
        session.add_all(
            [
                Contact(
                    vendor.vendor_id,
                    contact['name'],
                    contact['title'],
                    contact['email'],
                    contact['phone'],
                    contact['additional_info']
                ) for contact in contacts
            ] 
        )

        for product in vendor.products:
            session.delete(product)

        session.add_all(
            [
                Product(
                    vendor.vendor_id,
                    product['Product Name'],
                    product['Unit Price'],
                    product['Currency'],
                    product['Description']
                ) for product in products
            ] 
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:

        session.close()

def delete_Vendor(
    vendor_id
):
    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        Vendor_to_delete = session.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()

        session.delete(Vendor_to_delete)

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:
        session.close()

def add_Employee(
    username, 
    password, 
    admin, 
    name, 
    nik, 
    position, 
    email
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        employee = Employee(
            username, 
            password, 
            admin, 
            name, 
            nik, 
            position, 
            email
        )

        session.add(
            employee
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:

        session.close()

def edit_Employee(
    employee_id,
    username, 
    password, 
    admin, 
    name, 
    nik, 
    position, 
    email
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        employee = session.query(Employee).filter(Employee.id == employee_id).first()

        employee.username = username
        employee.password = password
        employee.admin = admin
        employee.name = name
        employee.nik = nik
        employee.position = position
        employee.email = email

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:

        session.close()

def delete_Employee(
    employee_id
):
    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        employee = session.query(Employee).filter(Employee.id == employee_id).first()

        session.delete(employee)

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:
        session.close()

def generate_po_pdf(po_obj):
        
    to_rows = [
        {'label':'To','value':'TRACERCO ASIA SDN. BHD.'},
        {'label':'Attn','value':'Amin Farhan bin Ismail'},
        {'label':'Address','value':'No. 27 Jalan PJU 3/47, Sunway Damansara 47810 Petaling Jaya, Selangor'},
        {'label':'Telp','value':'+6221-2302345'},
        {'label':'Email','value':'amin.farhanbinismail@tracerco.com'},
        {'label':'Ref Qout','value':'-'}
    ]

    to_table = dmc.Paper(
        dmc.Box(
            dmc.Table(
                dmc.TableTbody(
                    [  
                        dmc.TableTr(
                            [
                                dmc.TableTd(
                                    dmc.Text(
                                        row['label'],
                                        fw=500
                                    ),
                                    w=120,
                                    style={
                                        'vertical-align': 'top',
                                        'text-align': 'left',
                                    },
                                    py=0
                                ),
                                dmc.TableTd(
                                    dmc.Text(
                                        ':',
                                        fw=500,
                                    ),
                                    w=5,
                                    style={
                                        'vertical-align': 'top',
                                    },
                                    px=0,
                                    py=0
                                ),
                                dmc.TableTd(
                                    dmc.Text(
                                        row['value'],
                                    ),
                                    py=0,
                                    style={
                                        'vertical-align': 'top',
                                        'text-align': 'left',
                                    },
                                ),
                            ]
                        )
                        for row in to_rows
                    ]
                ),
                borderColor='white',
            ),
        ),
        w=500,
        withBorder=False
    )

    from_rows = [
        {'label':'PO No','value':'77988/HANDILTRACERCO/I'},
        {'label':'PO Date','value':'2 Mei 2024'},
        {'label':'From','value':'PT. Andalas Petroleum Services'},
        {'label':'Address','value':'Komp. Golden Plaza Blok H/2 No. 15, JI. RS Fatmawati, Jakarta Selatan - 12420'},
        {'label':'Phone/Fax','value':'021 2765 0756'},
        {'label':'Contact Person','value':'Eka Keneidy'},
        {'label':'Email','value':'eka@apetrol.com'}
    ]

    from_table = dmc.Paper(
        dmc.Box(
            dmc.Table(
                dmc.TableTbody(
                    [  
                        dmc.TableTr(
                            [
                                dmc.TableTd(
                                    dmc.Text(
                                        row['label'],
                                        fw=500
                                    ),
                                    w=120,
                                    style={
                                        'vertical-align': 'top',
                                        'text-align': 'left',
                                    },
                                    py=0
                                ),
                                dmc.TableTd(
                                    dmc.Text(
                                        ':',
                                        fw=500,
                                    ),
                                    w=5,
                                    style={
                                        'vertical-align': 'top',
                                    },
                                    px=0,
                                    py=0
                                ),
                                dmc.TableTd(
                                    dmc.Text(
                                        row['value'],
                                    ),
                                    py=0,
                                    style={
                                        'vertical-align': 'top',
                                        'text-align': 'left',
                                    },
                                ),
                            ]
                        )
                        for row in from_rows
                    ]
                ),
                borderColor='white',
            ),
        ),
        w=500,
        withBorder=False
    )

    item_rows = [
        {"No.": '1', "QTY": '105 Kg', "PRODUCT NAME": "Tracer Materials", "DESCRIPTION": "Three Unique Traces for 3 different layers", "PRICE": "400.00", "TOTAL PRICE": "42,000.00"},
    ]

    item_table = dmc.Table(
        [
            dmc.TableThead(
                dmc.TableTr(
                    [
                        dmc.TableTh(dmc.Text("NO.",fw=700,ta='center')),
                        dmc.TableTh(dmc.Text("QTY",fw=700,ta='center')),
                        dmc.TableTh(dmc.Text("PRODUCT NAME",fw=700,ta='center')),
                        dmc.TableTh(dmc.Text("DESCRIPTION",fw=700,ta='center')),
                        dmc.TableTh(dmc.Text("PRICE",fw=700,ta='center')),
                        dmc.TableTh(dmc.Text("TOTAL PRICE",fw=700,ta='center')),
                    ]
                ),
                h=50,
                bg=dmc.DEFAULT_THEME['colors']['blue'][3]
            ),
            dmc.TableTbody(
                [
                    dmc.TableTr(
                        [
                            dmc.TableTd(dmc.Text(item["No."])),
                            dmc.TableTd(dmc.Text(item["QTY"])),
                            dmc.TableTd(dmc.Text(item["PRODUCT NAME"])),
                            dmc.TableTd(dmc.Text(item["DESCRIPTION"])),
                            dmc.TableTd(dmc.Group([dmc.Text('$'),dmc.Text(item["PRICE"])],justify='space-between')),
                            dmc.TableTd(dmc.Group([dmc.Text('$'),dmc.Text(item["TOTAL PRICE"])],justify='space-between')),
                        ]
                    )
                    for item in item_rows
                ] + 
                [dmc.TableTr([
                    html.Td(),
                    html.Td(),
                    html.Td(),
                    html.Td(),
                    dmc.TableTd(dmc.Text('TOTAL PRICE',ta='right')),
                    dmc.TableTd(dmc.Group([dmc.Text('$'),dmc.Text('42,000.00')],justify='space-between')),
                ]),
                dmc.TableTr([
                    html.Td(),
                    html.Td(),
                    html.Td(),
                    html.Td(),
                    html.Td(),
                    dmc.TableTd(html.I(dmc.Text('(without shipping costs)',ta='right',fw=700))),
                ]),
                ]
            )
        ],
        striped=True,
        withTableBorder=True,
        withColumnBorders=True,
        borderColor='black'
    )

    layout = dmc.MantineProvider(
        dmc.Stack(
            [
                dmc.Group(
                    [
                        dmc.Image(
                            src='assets/Logo APS 2.png',
                            alt="Logo",
                            h=80
                        ),
                        dmc.Paper(
                            dmc.Text(
                                'Purchase Order',fw=700
                            ),
                            withBorder=True,
                            p='lg',
                            py='sm',
                            bg=dmc.DEFAULT_THEME['colors']['blue'][3],
                            radius=0,
                            top=0
                        )
                    ],
                    justify='space-between',
                    
                ),
                dmc.Group(
                    [
                        to_table,
                        from_table
                    ],
                    justify='space-between',
                    align='end',
                ),
                item_table,
                dmc.Stack(
                    [
                        dmc.Text(
                            'Notes', fw=700
                        ),
                        dcc.Markdown(
                            po_obj.notes,
                            dangerously_allow_html=True,
                            style={'margin':0},
                            className='no-padding'
                        )
                    ],
                    gap=0
                )
                
            ],
            p='lg'
        ),   
    )

    return layout

def apply_password_hash(password):
    return generate_password_hash(password, method='pbkdf2:sha256')

def add_HazardObservationCard(
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
):
    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        hoc = HazardObservationCard(
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

        session.add(
            hoc
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:

        session.close()

def edit_HazardObservationCard(
    hoc_id,
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
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        hoc = session.query(HazardObservationCard).filter(HazardObservationCard.hoc_id == hoc_id).first()

        hoc.area = area
        hoc.hazard_tanggal_waktu = datetime.combine(datetime.strptime(hazard_tanggal, "%Y-%m-%d"), datetime.min.time()).replace(hour=int(hazard_waktu_jam), minute=int(hazard_waktu_menit))
        hoc.temuan = temuan
        hoc.bahaya_fisik = bahaya_fisik
        hoc.bahaya_kimia = bahaya_kimia
        hoc.bahaya_biologi = bahaya_biologi
        hoc.bahaya_ergonomi = bahaya_ergonomi
        hoc.bahaya_psikososial = bahaya_psikososial
        hoc.resiko_potensial = resiko_potensial
        hoc.penyebab = penyebab
        hoc.pengendalian = pengendalian
        hoc.tindakan_perbaikan = tindakan_perbaikan

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:

        session.close()

def delete_HazardObservationCard(
    hoc_id
):
    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        hoc_to_delete = session.query(HazardObservationCard).filter(HazardObservationCard.hoc_id == hoc_id).first()

        session.delete(hoc_to_delete)

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:
        session.close()

def add_IndividualClient(
    name,
    title,
    email, 
    phone, 
    additional_info, 
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        client = Contact(
            None,
            name,
            title,
            email,
            phone,
            additional_info,
            type='client'
        )

        session.add(
            client
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:

        session.close()

def edit_IndividualClient(
    client_id,
    name,
    title,
    email, 
    phone, 
    additional_info, 
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        client = session.query(Contact).filter(Contact.contact_id == client_id).first()

        client.name = name
        client.title = title
        client.email = email
        client.phone = phone
        client.additional_info = additional_info

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:

        session.close()

def delete_IndividualClient(
    client_id
):
    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        client = session.query(Contact).filter(Contact.contact_id == client_id).first()

        session.delete(client)

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:
        session.close()

def add_CompanyClient(
    company_client_name,
    company_client_address,
    contacts,
    additional_info
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        company_client = CompanyClient(
            company_client_name,
            company_client_address, 
            additional_info,
        )

        session.add(
            company_client
        )

        session.commit()

        session.add_all(
            [
                Contact(
                    company_client.client_id,
                    contact['name'],
                    contact['title'],
                    contact['email'],
                    contact['phone'],
                    contact['additional_info'],
                    type='client'
                ) for contact in contacts
            ] 
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:

        session.close()

def edit_CompanyClient(
    client_id,
    company_name,
    company_address,
    contacts,
    additional_info
):

    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        company_client = session.query(CompanyClient).filter(CompanyClient.client_id == client_id).first()

        company_client.company_name = company_name
        company_client.company_address = company_address
        company_client.additional_info = additional_info

        for contact in company_client.contacts:
            session.delete(contact)
    
        session.add_all(
            [
                Contact(
                    company_client.client_id,
                    contact['name'],
                    contact['title'],
                    contact['email'],
                    contact['phone'],
                    contact['additional_info'],
                    type='client'
                ) for contact in contacts
            ] 
        )

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:

        session.close()

def delete_CompanyClient(
    client_id
):
    try:

        Session = sessionmaker(bind=db.engine)
        session = Session()

        CompanyClient_to_delete = session.query(CompanyClient).filter(CompanyClient.client_id == client_id).first()

        session.delete(CompanyClient_to_delete)

        session.commit()

    except Exception as err:

        session.rollback()

        raise err

    finally:
        session.close()

