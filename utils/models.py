from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from flask import session
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Enum, Date, Text, Boolean, Table, JSON
import datetime
from enum import Enum as PyEnum
from flask_login import UserMixin

db = SQLAlchemy()

# job_employee_association = Table('job_employee', db.metadata,
#     Column('job_id', String(36), ForeignKey('jobs.job_id')),
#     Column('employee_id', String(36), ForeignKey('employees.id'))
# )

class Employee(UserMixin,db.Model):
    
    __tablename__ = 'employees'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(15), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    admin = Column(Boolean)
    name = Column(String(256))
    nik = Column(String(16))
    position = Column(String(50))
    email = Column(String(120))
    logs = relationship('Log', back_populates='employee', cascade="all, delete-orphan")
    #jobs = relationship("Job", secondary=job_employee_association, back_populates="employees")
    hocs = relationship("HazardObservationCard", back_populates="employee")

    def __init__(self, username, password, admin, name, nik, position, email):
        self.username = username
        self.password = password
        self.admin = admin
        self.name = name
        self.nik = nik
        self.position = position
        self.email = email

class Item(db.Model):

    __tablename__ = 'inventory'

    item_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    quantity_available = Column(Integer, nullable=False)
    unit_price = Column(Float(precision=2), nullable=False)
    total_value = Column(Float(precision=2), nullable=False)
    supplier_name = Column(String(100), nullable=False)
    supplier_contact = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    date_of_acquisition = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=True)
    condition = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    files = relationship('File', back_populates='item', cascade="all, delete-orphan")

    def __init__(self, item_name, category, quantity_available, unit_price, total_value,
                 supplier_name, supplier_contact=None, location=None, date_of_acquisition=None,
                 expiration_date=None, condition='New', notes=None):
        self.item_name = item_name
        self.category = category
        self.quantity_available = quantity_available
        self.unit_price = unit_price
        self.total_value = total_value
        self.supplier_name = supplier_name
        self.supplier_contact = supplier_contact
        self.location = location
        self.date_of_acquisition = date_of_acquisition
        self.expiration_date = expiration_date
        self.condition = condition
        self.notes = notes

class File(db.Model):

    __tablename__ = 'inventory_files'

    file_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String(36), ForeignKey('inventory.item_id'))
    file_type = Column(String(20))
    file_name = Column(String(100))
    content = Column(MEDIUMBLOB)
    item = relationship('Item', back_populates='files')

    def __init__(self, item_id, file_type, file_name, content):
        self.item_id = item_id
        self.file_type = file_type
        self.file_name = file_name
        self.content = content

class TempFile(db.Model):

    __tablename__ = 'temp_files'

    file_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_session = Column(String(36))
    file_type = Column(String(20))
    file_name = Column(String(100))
    content = Column(MEDIUMBLOB)

    def __init__(self, file_id, file_type, file_name, content):
        self.file_id = file_id
        self.user_session = session['session_id']
        self.file_type = file_type
        self.file_name = file_name
        self.content = content

class LogType(PyEnum):
    ERROR = "ERROR"
    ACTIVITY = "ACTIVITY"

class CompanyClient(db.Model):
    __tablename__ = 'company_clients'

    client_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String(255), nullable=False)
    company_address = Column(String(255), nullable=False)
    additional_info = Column(String(255))

    contacts = relationship("Contact", back_populates="client_company", cascade="all, delete-orphan")

    def __init__(self, company_name, company_address, additional_info):
        self.company_name = company_name
        self.company_address = company_address
        self.additional_info = additional_info

class Log(db.Model):

    __tablename__ = 'logs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(36), ForeignKey('employees.id'))
    employee = relationship("Employee", back_populates="logs")
    type = Column(Enum(LogType), nullable=False)
    description = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    
    def __init__(self, type, log):

        from flask_login import current_user

        self.employee_id = current_user.id
        self.type = type
        self.description = log

    def __str__(self):
        return f'<{self.type} {self.user.username} - {self.log} at {self.timestamp}>'

class OrderStatus(PyEnum):
    ISSUED = "ISSUED"
    APPROVED = "APPROVED"
    CANCELED = "CANCELED"

class Vendor(db.Model):

    __tablename__ = 'vendors'

    vendor_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_name = Column(String(255), nullable=False)
    vendor_address = Column(String(255), nullable=False)
    vendor_type = Column(String(50), nullable=False)
    additional_info = Column(String(255), nullable=False)

    contacts = relationship("Contact", back_populates="vendor_company", cascade="all, delete-orphan")
    outgoing_purchase_orders = relationship("OutgoingPurchaseOrder", back_populates="vendor", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="vendor", cascade="all, delete-orphan")

    def __init__(self, vendor_name, vendor_address, vendor_type, additonal_info):
        self.vendor_name = vendor_name
        self.vendor_address = vendor_address
        self.vendor_type = vendor_type
        self.additional_info = additonal_info

class Contact(db.Model):
    __tablename__ = 'contacts'

    contact_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_id = Column(String(36), ForeignKey('vendors.vendor_id'))
    company_client_id = Column(String(36), ForeignKey('company_clients.client_id'))
    name = Column(String(100), nullable=False)
    title = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    additional_info = Column(String(255))
    contact_type = Column(String(20), nullable=False)

    vendor_company = relationship("Vendor", back_populates="contacts")
    client_company = relationship("CompanyClient", back_populates="contacts")
    outgoing_purchase_orders = relationship("OutgoingPurchaseOrder", back_populates="contact")
    
    def __init__(self, id, name, title, email, phone, additional_info, type='vendor'):

        if type=='vendor':
            self.vendor_id = id
        elif type=='client':
            self.company_client_id = id
        else:
            raise ValueError('Must either vendor or client')
            
        self.name = name
        self.title = title
        self.email = email
        self.phone = phone
        self.additional_info = additional_info
        self.contact_type = type

class Product(db.Model):
    __tablename__ = 'products'

    product_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_id = Column(String(36), ForeignKey('vendors.vendor_id'))
    product_name = Column(String(100), nullable=False)
    description = Column(String(255))
    unit_price = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)

    vendor = relationship("Vendor", back_populates="products")
    order_items = relationship("OutgoingPurchaseOrderItem", back_populates="product")

    def __init__(self, vendor_id, product_name, unit_price, currency, description=None):
        self.vendor_id = vendor_id
        self.product_name = product_name
        self.unit_price = unit_price
        self.currency = currency
        self.description = description

class OutgoingPurchaseOrder(db.Model):
    __tablename__ = 'outgoing_purchase_orders'

    po_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    po_no = Column(String(50), nullable=False, unique=True)
    vendor_id = Column(String(36), ForeignKey('vendors.vendor_id'))
    contact_id = Column(String(36), ForeignKey('contacts.contact_id'))
    order_date = Column(DateTime, default=datetime.datetime.now)
    total_amount = Column(Float, nullable=False)
    notes = Column(Text)

    status = Column(Enum(OrderStatus), default=OrderStatus.ISSUED)
    issued_by = Column(String(36), ForeignKey('employees.id'), nullable=True)
    issued_date = Column(DateTime, default=datetime.datetime.now)
    last_edited_by = Column(String(36), ForeignKey('employees.id'), nullable=True)
    last_edited_date = Column(DateTime, onupdate=datetime.datetime.now)
    approved_by = Column(String(36), ForeignKey('employees.id'), nullable=True)
    approved_date = Column(DateTime, nullable=True)

    vendor = relationship("Vendor", back_populates="outgoing_purchase_orders")
    contact = relationship("Contact", back_populates="outgoing_purchase_orders")
    items = relationship("OutgoingPurchaseOrderItem", back_populates="outgoing_purchase_order",cascade="all, delete-orphan")
    issuer = relationship("Employee", foreign_keys=[issued_by])
    editor = relationship("Employee", foreign_keys=[last_edited_by])
    approver = relationship("Employee", foreign_keys=[approved_by])

    def __init__(self, po_no, vendor_id, total_amount, contact_id=None, notes=None, status=OrderStatus.ISSUED, issued_by=None, issued_date=None, last_edited_by=None, last_edited_date=None, approved_by=None, approved_date=None):
        self.po_no = po_no
        self.vendor_id = vendor_id
        self.total_amount = total_amount
        self.contact_id = contact_id
        self.notes = notes
        self.status = status
        self.issued_by = issued_by
        self.issued_date = issued_date or datetime.datetime.now()
        self.last_edited_by = last_edited_by
        self.last_edited_date = last_edited_date
        self.approved_by = approved_by
        self.approved_date = approved_date

class OutgoingPurchaseOrderItem(db.Model):
    
    __tablename__ = 'outgoing_purchase_orders_items'

    item_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    po_id = Column(String(36), ForeignKey('outgoing_purchase_orders.po_id'))
    product_id = Column(String(36), ForeignKey('products.product_id'))
    quantity = Column(String(50), nullable=False)
    total_price = Column(Float, nullable=False)
    currency = Column(String(3))

    outgoing_purchase_order = relationship("OutgoingPurchaseOrder", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __init__(self, po_id, product_id, quantity, total_price, currency):
        self.po_id = po_id
        self.product_id = product_id
        self.quantity = quantity
        self.total_price = total_price
        self.currency = currency

class HazardObservationCard(db.Model):

    __tablename__ = 'hocs'

    hoc_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(36), ForeignKey('employees.id'))
    employee = relationship("Employee", back_populates="hocs")
    area = Column(String(30))
    hazard_tanggal_waktu = Column(DateTime)
    temuan = Column(String(255))
    bahaya_fisik = Column(String(255))
    bahaya_kimia = Column(String(255))
    bahaya_biologi = Column(String(255))
    bahaya_ergonomi = Column(String(255))
    bahaya_psikososial = Column(String(255))
    bahaya_psikososial = Column(String(255))
    resiko_potensial = Column(String(255))
    penyebab = Column(String(255))
    pengendalian = Column(JSON)
    tindakan_perbaikan = Column(String(255))
    
    def __init__(self, area, hazard_tanggal, hazard_waktu_jam, hazard_waktu_menit, temuan, bahaya_fisik=None, bahaya_kimia=None, 
                 bahaya_biologi=None, bahaya_ergonomi=None, bahaya_psikososial=None, resiko_potensial=None, 
                 penyebab=None, pengendalian=None, tindakan_perbaikan=None):
        
        from flask_login import current_user

        self.employee_id = current_user.id
        self.area = area
        self.hazard_tanggal_waktu = datetime.datetime.combine(datetime.datetime.strptime(hazard_tanggal, "%Y-%m-%d"), datetime.datetime.min.time()).replace(hour=int(hazard_waktu_jam), minute=int(hazard_waktu_menit))
        self.temuan = temuan
        self.bahaya_fisik = bahaya_fisik
        self.bahaya_kimia = bahaya_kimia
        self.bahaya_biologi = bahaya_biologi
        self.bahaya_ergonomi = bahaya_ergonomi
        self.bahaya_psikososial = bahaya_psikososial
        self.resiko_potensial = resiko_potensial
        self.penyebab = penyebab
        self.pengendalian = pengendalian
        self.tindakan_perbaikan = tindakan_perbaikan

# class Job(db.Model):
#     __tablename__ = 'jobs'

#     job_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     job_title = Column(String(50), nullable=False)
#     plan_start_date = Column(Date, nullable=False)
#     plan_end_date = Column(Date, nullable=False)
#     actual_start_date = Column(Date, nullable=False)
#     actual_end_date = Column(Date, nullable=False)
#     job_desc = Column(Float, nullable=False)
#     job_service_type = Column(String(50), nullable=False)
#     shipments = relationship("Shipment", back_populates="job")
#     daily_reports = relationship("DailyReport", back_populates="job")
#     basts = relationship("BAST", back_populates="job")
#     hsse_reports = relationship("HSSE", back_populates="job")
#     employees = relationship("Employee", secondary=job_employee_association, back_populates="jobs")

#     def __init__(self, job_title, plan_start_date, plan_end_date, actual_start_date, actual_end_date, job_desc, job_service_type):
#         self.job_id = str(uuid.uuid4())
#         self.job_title = job_title
#         self.plan_start_date = plan_start_date
#         self.plan_end_date = plan_end_date
#         self.actual_start_date = actual_start_date
#         self.actual_end_date = actual_end_date
#         self.job_desc = job_desc
#         self.job_service_type = job_service_type


# class Shipment(db.Model):
#     __tablename__ = 'shipments'

#     shipment_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     job_id = Column(String(36), ForeignKey('jobs.job_id'), nullable=False)
#     tool_name = Column(String(50), nullable=False)
#     quantity = Column(Integer, nullable=False)
#     direction = Column(String(10), nullable=False)  # 'in' or 'out'
#     date = Column(Date, nullable=False)
#     job = relationship("Job", back_populates="shipments")

#     def __init__(self, job_id, tool_name, quantity, direction, date):
#         self.shipment_id = str(uuid.uuid4())
#         self.job_id = job_id
#         self.tool_name = tool_name
#         self.quantity = quantity
#         self.direction = direction
#         self.date = date

# class DailyReport(db.Model):
#     __tablename__ = 'daily_reports'

#     report_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     job_id = Column(String(36), ForeignKey('jobs.job_id'), nullable=False)
#     report_date = Column(Date, nullable=False)
#     report_content = Column(Text, nullable=False)
#     job = relationship("Job", back_populates="daily_reports")

#     def __init__(self, job_id, report_date, report_content):
#         self.report_id = str(uuid.uuid4())
#         self.job_id = job_id
#         self.report_date = report_date
#         self.report_content = report_content


# class BAST(db.Model):
#     __tablename__ = 'basts'

#     bast_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     job_id = Column(String(36), ForeignKey('jobs.job_id'), nullable=False)
#     bast_date = Column(Date, nullable=False)
#     bast_details = Column(Text, nullable=False)
#     job = relationship("Job", back_populates="basts")

#     def __init__(self, job_id, bast_date, bast_details):
#         self.bast_id = str(uuid.uuid4())
#         self.job_id = job_id
#         self.bast_date = bast_date
#         self.bast_details = bast_details


# class HSSE(db.Model):
    # __tablename__ = 'hsse_reports'

    # hsse_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # job_id = Column(String(36), ForeignKey('jobs.job_id'), nullable=False)
    # report_date = Column(Date, nullable=False)
    # report_content = Column(Text, nullable=False)
    # job = relationship("Job", back_populates="hsse_reports")

    # def __init__(self, job_id, report_date, report_content):
    #     self.hsse_id = str(uuid.uuid4())
    #     self.job_id = job_id
    #     self.report_date = report_date
    #     self.report_content = report_content