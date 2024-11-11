from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
import json
import math

# Assuming the models are named Customer and Loan
from .models import Customer, Loan
from .utils import calculate_credit_score, calculate_monthly_installment
from django.views.decorators.csrf import csrf_exempt    

# /register

@csrf_exempt
@require_POST
def register(request):
    data = json.loads(request.body)
    
    try:
        # Calculate approved limit
        monthly_income = data['monthly_income']
        approved_limit = round(36 * monthly_income, -5)  # rounded to nearest lakh (100,000)
        
        # Create new customer
        customer = Customer.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            monthly_income=monthly_income,
            phone_number=data['phone_number'],
            approved_limit=approved_limit
        )
        
        response_data = {
            "id": customer.id,
            "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age,
            "monthly_income": customer.monthly_income,
            "approved_limit": customer.approved_limit,
            "phone_number": customer.phone_number
        }
        return JsonResponse(response_data, status=201)
    
    except KeyError as e:
        return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)

# /check-eligibility
@csrf_exempt
@require_POST
def check_eligibility(request):
    data = json.loads(request.body)
    
    try:
        customer = get_object_or_404(Customer, pk=data['id'])
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']

        # Calculate credit score
        credit_score = calculate_credit_score(customer)
        
        # Determine approval and interest rate based on credit score
        approved = False
        corrected_interest_rate = interest_rate
        if credit_score > 50:
            approved = True
        elif 50 > credit_score > 30:
            approved = True
            corrected_interest_rate = max(interest_rate, 12)
        elif 30 > credit_score > 10:
            approved = True
            corrected_interest_rate = max(interest_rate, 16)
        else:
            approved = False

        # Additional check for EMI threshold
        if approved:
            monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
            if monthly_installment > 0.5 * customer.monthly_income:
                approved = False
                monthly_installment = None

        response_data = {
            "id": customer.id,
            "approval": approved,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": monthly_installment
        }
        return JsonResponse(response_data, status=200)
    
    except KeyError as e:
        return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)


# /create-loan
@csrf_exempt
@require_POST
def create_loan(request):
    data = json.loads(request.body)
    
    try:
        customer = get_object_or_404(Customer, pk=data['id'])
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']

        # Check eligibility
        eligibility_response = check_eligibility(request)
        if not eligibility_response['approval']:
            return JsonResponse({
                "loan_id": None,
                "id": customer.id,
                "loan_approved": False,
                "message": "Loan not approved due to eligibility criteria.",
                "monthly_installment": None
            }, status=400)

        # Create Loan
        monthly_installment = eligibility_response['monthly_installment']
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure,
            monthly_installment=monthly_installment,
            loan_approved=True
        )

        response_data = {
            "loan_id": loan.id,
            "id": customer.id,
            "loan_approved": True,
            "message": "Loan approved successfully.",
            "monthly_installment": monthly_installment
        }
        return JsonResponse(response_data, status=201)
    
    except KeyError as e:
        return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)

# /view-loan/<int:loan_id>
@csrf_exempt
@require_GET
def view_loan(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    
    response_data = {
        "loan_id": loan.id,
        "customer": {
            "id": loan.customer.id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "phone_number": loan.customer.phone_number,
            "age": loan.customer.age
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_installment,
        "tenure": loan.tenure
    }
    return JsonResponse(response_data, status=200)

# /view-loans/<int:id>
@csrf_exempt
@require_GET
def view_loans(request, id):
    customer = get_object_or_404(Customer, pk=id)
    loans = Loan.objects.filter(customer=customer)
    
    response_data = []
    for loan in loans:
        loan_data = {
            "loan_id": loan.id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "repayments_left": loan.calculate_remaining_emis()
        }
        response_data.append(loan_data)
    
    return JsonResponse(response_data, safe=False, status=200)
