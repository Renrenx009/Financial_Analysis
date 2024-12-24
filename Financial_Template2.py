import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def get_cpf_allocation_rates(age):
    if age <= 35:
        return 0.6217, 0.1621, 0.2162
    elif age <= 45:
        return 0.5677, 0.1891, 0.2432
    elif age <= 50:
        return 0.5136, 0.2162, 0.2702
    elif age <= 55:
        return 0.4055, 0.3108, 0.2837
    elif age <= 60:
        return 0.3872, 0.2741, 0.3387
    elif age <= 65:
        return 0.1592, 0.3636, 0.4772
    elif age <= 70:
        return 0.0607, 0.303, 0.6363
    else:
        return 0.08, 0.08, 0.84


def get_cpf_rates(age):
    if age <= 55:
        return 0.17, 0.20, 0.37
    elif age <= 60:
        return 0.15, 0.16, 0.31
    elif age <= 65:
        return 0.115, 0.105, 0.22
    elif age <= 70:
        return 0.09, 0.075, 0.165
    else:
        return 0.075, 0.05, 0.125


def calculate_cpf_balance(salary, bonus, thirteenth_month, monthly_expenses, start_age, current_age,
                          annual_investment_premium, annual_interest_rate):
    cpf_balance = {'Year': [], 'Age': [], 'Cumulative Cash Savings': [], 'Cumulative OA': [], 'Cumulative SA': [],
                   'Cumulative MA': [],
                   'Cumulative Investment Premium': [], 'Investment Value': []}

    years_worked = current_age - start_age
    cumulative_cash_savings = cumulative_oa = cumulative_sa = cumulative_ma = cumulative_investment_premium = investment_value = 0

    for year in range(years_worked):
        age = start_age + year
        oa_rate, sa_rate, ma_rate = get_cpf_allocation_rates(age)
        employer_rate, employee_rate, total_rate = get_cpf_rates(age)

        annual_income = salary * 12 + bonus + thirteenth_month
        cpf_contribution = annual_income * total_rate

        net_monthly_salary = (salary * (1 - employee_rate)) - monthly_expenses
        net_annual_salary = (net_monthly_salary * 12) + (bonus * (1 - employee_rate)) + (
                    thirteenth_month * (1 - employee_rate))

        cumulative_cash_savings += net_annual_salary - annual_investment_premium
        cumulative_oa += cpf_contribution * oa_rate
        cumulative_sa += cpf_contribution * sa_rate
        cumulative_ma += cpf_contribution * ma_rate

        cumulative_investment_premium += annual_investment_premium
        investment_value = (investment_value + annual_investment_premium) * (1 + annual_interest_rate / 100)

        cpf_balance['Year'].append(year + 1)
        cpf_balance['Age'].append(age)
        cpf_balance['Cumulative Cash Savings'].append(round(cumulative_cash_savings, 2))
        cpf_balance['Cumulative OA'].append(round(cumulative_oa, 2))
        cpf_balance['Cumulative SA'].append(round(cumulative_sa, 2))
        cpf_balance['Cumulative MA'].append(round(cumulative_ma, 2))
        cpf_balance['Cumulative Investment Premium'].append(round(cumulative_investment_premium, 2))
        cpf_balance['Investment Value'].append(round(investment_value, 2))

    return cpf_balance


st.header("Financial Template")
st.subheader("Key in your information here")

salary = st.number_input("Enter your monthly gross income:", min_value=0.0, step=100.0)
bonus = st.number_input("Enter your annual bonus:", min_value=0.0, step=100.0)
thirteenth_month = st.number_input("Enter your 13th month salary:", min_value=0.0, step=100.0)
monthly_expenses = st.number_input("Enter your monthly expenses:", min_value=0.0, step=100.0)
start_age = st.number_input("Enter your starting age:", min_value=0, step=1)
current_age = st.number_input("Enter your current age:", min_value=0, step=1)
annual_investment_premium = st.number_input("Enter your annual investment premium:", min_value=0.0, step=100.0)
annual_interest_rate = st.number_input("Enter the annual interest rate (as a percentage):", min_value=0.0, step=0.1)

if st.button("Calculate"):
    cpf_balance = calculate_cpf_balance(salary, bonus, thirteenth_month, monthly_expenses,
                                        start_age, current_age,
                                        annual_investment_premium,
                                        annual_interest_rate)

    df = pd.DataFrame(cpf_balance)
    st.write(df)

    total_years_worked = current_age - start_age
    total_cpf_contribution = df['Cumulative OA'].iloc[-1] + df['Cumulative SA'].iloc[-1] + df['Cumulative MA'].iloc[-1]
    total_employee_contribution = total_cpf_contribution * (
                df['Age'].apply(get_cpf_rates).apply(lambda x: x[1]).mean() / df['Age'].apply(get_cpf_rates).apply(
            lambda x: x[2]).mean())
    total_oa = df['Cumulative OA'].iloc[-1]
    total_sa = df['Cumulative SA'].iloc[-1]
    total_ma = df['Cumulative MA'].iloc[-1]
    cumulative_cash_savings = df['Cumulative Cash Savings'].iloc[-1]
    net_monthly_salary = (salary * (1 - get_cpf_rates(current_age)[1])) - monthly_expenses
    net_annual_salary = net_monthly_salary * 12 + bonus + thirteenth_month

    total_investment_premium_paid = df['Cumulative Investment Premium'].iloc[-1]
    investment_value = df['Investment Value'].iloc[-1]

    st.write("\nIn-Depth Analysis:")
    st.write(f"Total years worked: {total_years_worked}")
    st.write(f"Total CPF contribution: ${total_cpf_contribution:.2f}")
    st.write(f"Total Employee CPF contribution: ${total_employee_contribution:.2f}")
    st.write(f"Total OA (Ordinary Account) balance: ${total_oa:.2f}")
    st.write(f"Total SA (Special Account) balance: ${total_sa:.2f}")
    st.write(f"Total MA (MediSave Account) balance: ${total_ma:.2f}")
    st.write(f"Cumulative Cash Savings: ${cumulative_cash_savings:.2f}")
    st.write(f"Net Monthly Salary: ${net_monthly_salary:.2f}")
    st.write(f"Net Annual Salary: ${net_annual_salary:.2f}")
    st.write(f"Total Investment Premium Paid: ${total_investment_premium_paid:.2f}")
    st.write(f"Total Investment Value: ${investment_value:.2f}")

    # Plotting the investment value and cumulative investment premium
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['Year'], df['Investment Value'], marker='o', linestyle='-', color='b', label='Investment Value')
    ax.plot(df['Year'], df['Cumulative Investment Premium'], marker='o', linestyle='-', color='r',
            label='Cumulative Investment Premium')
    ax.set_xlabel('Year')
    ax.set_ylabel('Amount ($)')
    ax.set_title('Investment Value and Cumulative Investment Premium Over Time')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)