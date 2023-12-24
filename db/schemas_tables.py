# db/schemas_tables.py
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)

from db.base_class import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class PaymentMethod(Base):
    __tablename__ = "payments_methods"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class Month(Base):
    __tablename__ = "months"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class ExpenseCategory(Base):
    __tablename__ = "expenses_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class ExpenseSubcategory(Base):
    __tablename__ = "expenses_subcategories"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("expenses_categories.id"))
    name = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class ExpenseTransactionType(Base):
    __tablename__ = "expenses_transactions_types"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class ExpenseType(Base):
    __tablename__ = "expenses_types"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class ExpenseTransaction(Base):
    __tablename__ = "expenses_transactions"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("expenses_categories.id"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("expenses_subcategories.id"))
    type_id = Column(Integer, ForeignKey("expenses_transactions_types.id"), default=1)
    expense_type_id = Column(Integer, ForeignKey("expenses_types.id"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payments_methods.id"))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    amount = Column(Float, nullable=False)
    tax = Column(Float)
    invoice_flag = Column(Boolean, default=False)
    date = Column(DateTime)
    vendor = Column(String)
    location = Column(String)
    description = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    name = Column(String)
    location = Column(String)
    client = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class ProjectQuote(Base):
    __tablename__ = "projects_quotes"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    unit_price = Column(Float)
    quantity = Column(Float)
    subtotal = Column(Float)
    date = Column(DateTime)
    unit = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class IncomeType(Base):
    __tablename__ = "incomes_types"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class IncomePayroll(Base):
    __tablename__ = "incomes_payroll"
    id = Column(Integer, primary_key=True)
    income_type_id = Column(Integer, ForeignKey("incomes_types.id"), default=1)
    payment_destination_id = Column(
        Integer, ForeignKey("payments_methods.id"), default=3
    )
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    gross_income = Column(Float)
    imss = Column(Float)
    isr = Column(Float)
    total_deductions = Column(Float)
    net_income = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    fiscal_folio = Column(String, unique=True)
    client = Column(String)
    position = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class IncomeProject(Base):
    __tablename__ = "incomes_projects"
    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey("projects_quotes.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    income_type_id = Column(
        Integer, ForeignKey("incomes_types.id"), nullable=False, default=3
    )
    payment_destination_id = Column(
        Integer, ForeignKey("payments_methods.id"), default=3
    )
    invoice_flag = Column(Boolean, default=True)
    foreign_invoice = Column(Boolean)
    subtotal = Column(Float, nullable=False)
    iva = Column(Float)
    isr = Column(Float)
    discount = Column(Float, default=0)
    total = Column(Float)
    fiscal_folio = Column(String, unique=True)
    emission_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime)
    notes = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
