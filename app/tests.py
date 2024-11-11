from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .models import Customer, Loan
import json

class CreditApprovalSystemTests(TestCase):

    def setUp(self):
        # Setup a sample customer and loan data for testing
        self.customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "monthly_income": 50000,
            "phone_number": 1234567890,
        }
        self.loan_data = {
            "customer_id": 1,
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12,
        }
        # Create a customer instance for testing
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            monthly_income=50000,
            phone_number=1234567890,
            approved_limit=36 * 50000,  # approved_limit = 36 * monthly_salary
        )

    def test_register_customer(self):
        # Register a new customer
        url = reverse('register')  # Assuming 'register' is the name of your register endpoint
        response = self.client.post(url, self.customer_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('customer_id', response.data)
        self.assertEqual(response.data['first_name'], self.customer_data['first_name'])
        self.assertEqual(response.data['approved_limit'], 1800000)

    def test_check_eligibility(self):
        # Check loan eligibility for a customer
        url = reverse('check-eligibility')  # Assuming 'check-eligibility' is the name of your eligibility endpoint
        response = self.client.post(url, self.loan_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)
        self.assertIn('corrected_interest_rate', response.data)
        self.assertTrue(response.data['approval'])  # Assuming approval is True for this case

    def test_create_loan(self):
        # Create a loan for a customer
        url = reverse('create-loan')  # Assuming 'create-loan' is the name of your loan creation endpoint
        response = self.client.post(url, self.loan_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('loan_id', response.data)
        self.assertTrue(response.data['loan_approved'])
        self.assertIn('monthly_installment', response.data)

    def test_view_loan(self):
        # View loan details by loan_id
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            interest_rate=10,
            tenure=12,
            monthly_installment=10000,
            approved=True,
        )
        url = reverse('view-loan', kwargs={'loan_id': loan.id})  # Assuming 'view-loan' is the name of your loan detail endpoint
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_id'], loan.id)
        self.assertEqual(response.data['loan_amount'], loan.loan_amount)
        self.assertEqual(response.data['customer']['first_name'], self.customer.first_name)

    def test_view_loans_by_customer(self):
        # View all loans by customer_id
        loan1 = Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            interest_rate=10,
            tenure=12,
            monthly_installment=10000,
            approved=True,
        )
        loan2 = Loan.objects.create(
            customer=self.customer,
            loan_amount=200000,
            interest_rate=12,
            tenure=24,
            monthly_installment=15000,
            approved=True,
        )
        url = reverse('view-loans', kwargs={'customer_id': self.customer.id})  # Assuming 'view-loans' is the name of your loans by customer endpoint
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['loan_id'], loan1.id)
        self.assertEqual(response.data[1]['loan_id'], loan2.id)

    def test_register_customer_invalid_data(self):
        # Test invalid customer data (e.g., missing required fields)
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": "invalid",  # invalid age field
            "monthly_income": 50000,
            "phone_number": 1234567890,
        }
        url = reverse('register')
        response = self.client.post(url, invalid_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_eligibility_invalid_data(self):
        # Test invalid loan data for eligibility check
        invalid_data = {
            "customer_id": "invalid",  # invalid customer_id field
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12,
        }
        url = reverse('check-eligibility')
        response = self.client.post(url, invalid_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_loan_invalid_eligibility(self):
        # Create a loan with an ineligible customer
        ineligible_customer = Customer.objects.create(
            first_name="Jane",
            last_name="Doe",
            age=25,
            monthly_income=40000,
            phone_number=9876543210,
            approved_limit=36 * 40000,
        )
        url = reverse('create-loan')
        invalid_loan_data = {
            "customer_id": ineligible_customer.id,
            "loan_amount": 500000,
            "interest_rate": 10,
            "tenure": 12,
        }
        response = self.client.post(url, invalid_loan_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['loan_approved'])
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Loan not approved due to eligibility criteria")


