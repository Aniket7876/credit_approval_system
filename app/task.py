from celery import shared_task
import pandas as pd
from .models import Customer, Loan

@shared_task
def ingest_customer_data():
    customer_df = pd.read_excel('customer_data.xlsx')
    for _, row in customer_df.iterrows():
        Customer.objects.create(
            customer_id=row['customer_id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            phone_number=row['phone_number'],
            monthly_salary=row['monthly_salary'],
            approved_limit=row['approved_limit'],
            current_debt=row['current_debt'],
        )

@shared_task
def ingest_loan_data():
    loan_df = pd.read_excel('loan_data.xlsx')
    for _, row in loan_df.iterrows():
        customer = Customer.objects.get(customer_id=row['customer_id'])
        Loan.objects.create(
            customer=customer,
            loan_amount=row['loan_amount'],
            tenure=row['tenure'],
            interest_rate=row['interest_rate'],
            monthly_repayment=row['monthly_repayment'],
            emis_paid_on_time=row['emis_paid_on_time'],
            start_date=row['start_date'],
            end_date=row['end_date'],
        )
