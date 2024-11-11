from django.http import JsonResponse
import pandas as pd

def calculate_credit_score(customer):
    # Load loan history from loan_data.xlsx
    try:
        loan_data = pd.read_excel('loan_data.xlsx')
    except FileNotFoundError:
        return JsonResponse({"error": "Loan data file not found"}, status=500)
    
    # Filter data for this customer
    customer_loans = loan_data[loan_data['customer_id'] == customer.id]
    
    # Initialize score
    credit_score = 100  # Starting with a full score to deduct from

    # Criteria i: Past loans paid on time
    on_time_loans = customer_loans[customer_loans['status'] == 'paid_on_time']
    credit_score -= (len(customer_loans) - len(on_time_loans)) * 10

    # Criteria ii: Number of loans taken in the past
    credit_score -= min(len(customer_loans) * 2, 20)

    # Criteria iii: Loan activity in the current year
    current_year_loans = customer_loans[customer_loans['year'] == pd.Timestamp.now().year]
    credit_score -= min(len(current_year_loans) * 5, 15)

    # Criteria iv: Loan approved volume
    total_loan_volume = customer_loans['loan_amount'].sum()
    if total_loan_volume > 500000:  # Example threshold for deduction
        credit_score -= 10

    # Criteria v: If sum of current loans > approved limit, set credit score to 0
    current_loan_sum = customer_loans[customer_loans['status'] == 'active']['loan_amount'].sum()
    if current_loan_sum > customer.approved_limit:
        return 0

    # Ensure score stays within 0 to 100
    credit_score = max(0, min(credit_score, 100))

    return credit_score


def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    # Calculate compound interest-based monthly installment
    monthly_interest_rate = interest_rate / (12 * 100)
    return loan_amount * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -tenure)
