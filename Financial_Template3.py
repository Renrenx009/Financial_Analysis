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
                          annual_investment_premium, annual_interest_rate, milestones, milestone_percentage=1.0):
    cpf_balance = {'Year': [], 'Age': [], 'Cumulative Cash Savings': [], 'Cumulative OA': [], 'Cumulative SA': [],
                   'Cumulative MA': [], 'Cumulative Total CPF': [], 'Cumulative Investment Premium': [],
                   'Investment Value': [], 'Net Worth': []}

    years_worked = current_age - start_age
    cumulative_cash_savings = cumulative_oa = cumulative_sa = cumulative_ma = cumulative_investment_premium = investment_value = 0
    net_worth = 0

    for year in range(years_worked):
        age = start_age + year
        oa_rate, sa_rate, ma_rate = get_cpf_allocation_rates(age)
        employer_rate, employee_rate, total_rate = get_cpf_rates(age)

        annual_income = salary * 12 + bonus + thirteenth_month
        cpf_contribution = annual_income * total_rate

        net_monthly_salary = (salary * (1 - employee_rate)) - monthly_expenses
        net_annual_salary = (net_monthly_salary * 12) + (bonus * (1 - employee_rate)) + (thirteenth_month * (1 - employee_rate))

        cumulative_cash_savings += net_annual_salary - annual_investment_premium
        cumulative_oa += cpf_contribution * oa_rate
        cumulative_sa += cpf_contribution * sa_rate
        cumulative_ma += cpf_contribution * ma_rate

        cumulative_investment_premium += annual_investment_premium
        investment_value = (investment_value + annual_investment_premium) * (1 + annual_interest_rate / 100)

        cumulative_total_cpf = cumulative_oa + cumulative_sa + cumulative_ma
        net_worth = cumulative_cash_savings + cumulative_oa + cumulative_sa

        # Apply financial milestones
        if age in milestones:
            net_worth += milestones[age] * milestone_percentage
            cumulative_cash_savings += milestones[age] * milestone_percentage  # Ensure the effect is permanent

        cpf_balance['Year'].append(year + 1)
        cpf_balance['Age'].append(age + 1)  # Add 1 to the age for display
        cpf_balance['Cumulative Cash Savings'].append(round(cumulative_cash_savings, 2))
        cpf_balance['Cumulative OA'].append(round(cumulative_oa, 2))
        cpf_balance['Cumulative SA'].append(round(cumulative_sa, 2))
        cpf_balance['Cumulative MA'].append(round(cumulative_ma, 2))
        cpf_balance['Cumulative Total CPF'].append(round(cumulative_total_cpf, 2))
        cpf_balance['Cumulative Investment Premium'].append(round(cumulative_investment_premium, 2))
        cpf_balance['Investment Value'].append(round(investment_value, 2))
        cpf_balance['Net Worth'].append(round(net_worth, 2))

    return cpf_balance

def align_financial_data(df1, df2, start_age_1, start_age_2):
    # Determine the age range for alignment
    min_age = min(start_age_1, start_age_2)
    max_age = max(df1['Age'].iloc[-1], df2['Age'].iloc[-1])

    # Create a new DataFrame to hold the combined data
    combined_data = {
        'Year': list(range(1, max_age - min_age + 2)),
        'Cumulative Cash Savings': [],
        'Cumulative OA': [],
        'Cumulative SA': [],
        'Cumulative MA': [],
        'Cumulative Total CPF': [],
        'Cumulative Investment Premium': [],
        'Investment Value': [],
        'Net Worth': []
    }

    # Initialize financial values
    cumulative_cash_savings_1 = cumulative_cash_savings_2 = 0
    cumulative_oa_1 = cumulative_oa_2 = 0
    cumulative_sa_1 = cumulative_sa_2 = 0
    cumulative_ma_1 = cumulative_ma_2 = 0
    cumulative_total_cpf_1 = cumulative_total_cpf_2 = 0
    cumulative_investment_premium_1 = cumulative_investment_premium_2 = 0
    investment_value_1 = investment_value_2 = 0
    net_worth_1 = net_worth_2 = 0

    for year in combined_data['Year']:
        age = min_age + year - 1
        if age in df1['Age'].values:
            idx = df1['Age'].values.tolist().index(age)
            cumulative_cash_savings_1 = df1['Cumulative Cash Savings'].iloc[idx]
            cumulative_oa_1 = df1['Cumulative OA'].iloc[idx]
            cumulative_sa_1 = df1['Cumulative SA'].iloc[idx]
            cumulative_ma_1 = df1['Cumulative MA'].iloc[idx]
            cumulative_total_cpf_1 = df1['Cumulative Total CPF'].iloc[idx]
            cumulative_investment_premium_1 = df1['Cumulative Investment Premium'].iloc[idx]
            investment_value_1 = df1['Investment Value'].iloc[idx]
            net_worth_1 = df1['Net Worth'].iloc[idx]

        if age in df2['Age'].values:
            idx = df2['Age'].values.tolist().index(age)
            cumulative_cash_savings_2 = df2['Cumulative Cash Savings'].iloc[idx]
            cumulative_oa_2 = df2['Cumulative OA'].iloc[idx]
            cumulative_sa_2 = df2['Cumulative SA'].iloc[idx]
            cumulative_ma_2 = df2['Cumulative MA'].iloc[idx]
            cumulative_total_cpf_2 = df2['Cumulative Total CPF'].iloc[idx]
            cumulative_investment_premium_2 = df2['Cumulative Investment Premium'].iloc[idx]
            investment_value_2 = df2['Investment Value'].iloc[idx]
            net_worth_2 = df2['Net Worth'].iloc[idx]

        combined_data['Cumulative Cash Savings'].append(cumulative_cash_savings_1 + cumulative_cash_savings_2)
        combined_data['Cumulative OA'].append(cumulative_oa_1 + cumulative_oa_2)
        combined_data['Cumulative SA'].append(cumulative_sa_1 + cumulative_sa_2)
        combined_data['Cumulative MA'].append(cumulative_ma_1 + cumulative_ma_2)
        combined_data['Cumulative Total CPF'].append(cumulative_total_cpf_1 + cumulative_total_cpf_2)
        combined_data['Cumulative Investment Premium'].append(cumulative_investment_premium_1 + cumulative_investment_premium_2)
        combined_data['Investment Value'].append(investment_value_1 + investment_value_2)
        combined_data['Net Worth'].append(net_worth_1 + net_worth_2)

    return pd.DataFrame(combined_data)

st.header("Financial Analysis")
st.subheader("Key in your information here")

analysis_type = st.radio("Is this analysis for a single person or a couple?", ('Single', 'Couple'))

if analysis_type == 'Single':
    salary = st.number_input("Enter your monthly gross income:", min_value=0.0, step=100.0)
    bonus = st.number_input("Enter your annual bonus:", min_value=0.0, step=100.0)
    thirteenth_month = st.number_input("Enter your 13th month salary:", min_value=0.0, step=100.0)
    monthly_expenses = st.number_input("Enter your monthly expenses:", min_value=0.0, step=100.0)
    start_age = st.number_input("Enter your starting age:", min_value=0, step=1)
    current_age = st.number_input("Enter your current age:", min_value=0, step=1)
    annual_investment_premium = st.number_input("Enter your annual investment premium:", min_value=0.0, step=100.0)
    annual_interest_rate = st.number_input("Enter the annual interest rate (as a percentage):", min_value=0.0, step=0.1)

    st.subheader("Financial Milestones")
    num_milestones = st.number_input("Enter the number of financial milestones:", min_value=0, step=1)
    milestones = {}
    for i in range(num_milestones):
        age = st.number_input(f"Enter the age for milestone {i + 1}:", min_value=0, step=1)
        amount = st.number_input(f"Enter the amount for milestone {i + 1} (negative for expenses, positive for gains):",
                                 step=100.0)
        milestones[age] = amount

    if st.button("Calculate"):
        cpf_balance = calculate_cpf_balance(salary, bonus, thirteenth_month, monthly_expenses,
                                            start_age, current_age,
                                            annual_investment_premium,
                                            annual_interest_rate,
                                            milestones)

        df = pd.DataFrame(cpf_balance)

        total_years_worked = current_age - start_age
        total_cpf_contribution = df['Cumulative OA'].iloc[-1] + df['Cumulative SA'].iloc[-1] + df['Cumulative MA'].iloc[
            -1]
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
        net_worth = df['Net Worth'].iloc[-1]

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
        st.write(f"Net Worth: ${net_worth:.2f}")

        # Format the DataFrame to show dollar signs and two decimal places
        df = df.style.format({
            'Cumulative Cash Savings': '${:,.2f}',
            'Cumulative OA': '${:,.2f}',
            'Cumulative SA': '${:,.2f}',
            'Cumulative MA': '${:,.2f}',
            'Cumulative Total CPF': '${:,.2f}',
            'Cumulative Investment Premium': '${:,.2f}',
            'Investment Value': '${:,.2f}',
            'Net Worth': '${:,.2f}'
        })

        st.write(df)

        # Plotting the net worth
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df.data['Age'], df.data['Net Worth'], marker='o', linestyle='-', color='b', label='Net Worth')
        ax.set_xlabel('Age')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Net Worth Over Time')
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

else:
    st.subheader("Person 1")
    salary_1 = st.number_input("Enter Person 1's monthly gross income:", min_value=0.0, step=100.0)
    bonus_1 = st.number_input("Enter Person 1's annual bonus:", min_value=0.0, step=100.0)
    thirteenth_month_1 = st.number_input("Enter Person 1's 13th month salary:", min_value=0.0, step=100.0)
    monthly_expenses_1 = st.number_input("Enter Person 1's monthly expenses:", min_value=0.0, step=100.0)
    start_age_1 = st.number_input("Enter Person 1's starting age:", min_value=0, step=1)
    current_age_1 = st.number_input("Enter Person 1's current age:", min_value=0, step=1)
    annual_investment_premium_1 = st.number_input("Enter Person 1's annual investment premium:", min_value=0.0,
                                                  step=100.0)
    annual_interest_rate_1 = st.number_input("Enter Person 1's annual interest rate (as a percentage):", min_value=0.0,
                                             step=0.1)

    st.subheader("Person 2")
    salary_2 = st.number_input("Enter Person 2's monthly gross income:", min_value=0.0, step=100.0)
    bonus_2 = st.number_input("Enter Person 2's annual bonus:", min_value=0.0, step=100.0)
    thirteenth_month_2 = st.number_input("Enter Person 2's 13th month salary:", min_value=0.0, step=100.0)
    monthly_expenses_2 = st.number_input("Enter Person 2's monthly expenses:", min_value=0.0, step=100.0)
    start_age_2 = st.number_input("Enter Person 2's starting age:", min_value=0, step=1)
    current_age_2 = st.number_input("Enter Person 2's current age:", min_value=0, step=1)
    annual_investment_premium_2 = st.number_input("Enter Person 2's annual investment premium:", min_value=0.0,
                                                  step=100.0)
    annual_interest_rate_2 = st.number_input("Enter Person 2's annual interest rate (as a percentage):", min_value=0.0,
                                             step=0.1)

    st.subheader("Financial Milestones")
    num_milestones = st.number_input("Enter the number of financial milestones:", min_value=0, step=1)
    milestones = {}
    for i in range(num_milestones):
        age = st.number_input(f"Enter the age for milestone {i + 1} (Person 1's age):", min_value=0, step=1)
        amount = st.number_input(f"Enter the amount for milestone {i + 1} (negative for expenses, positive for gains):",
                                 step=100.0)
        milestones[age] = amount

    if st.button("Calculate"):
        cpf_balance_1 = calculate_cpf_balance(salary_1, bonus_1, thirteenth_month_1, monthly_expenses_1,
                                              start_age_1, current_age_1,
                                              annual_investment_premium_1,
                                              annual_interest_rate_1,
                                              milestones, milestone_percentage=0.5)
        cpf_balance_2 = calculate_cpf_balance(salary_2, bonus_2, thirteenth_month_2, monthly_expenses_2,
                                              start_age_2, current_age_2,
                                              annual_investment_premium_2,
                                              annual_interest_rate_2,
                                              milestones, milestone_percentage=0.5)

        # Create separate dataframes for each person
        df_1 = pd.DataFrame(cpf_balance_1)
        df_2 = pd.DataFrame(cpf_balance_2)

        total_years_worked_1 = current_age_1 - start_age_1
        total_cpf_contribution_1 = df_1['Cumulative OA'].iloc[-1] + df_1['Cumulative SA'].iloc[-1] + \
                                   df_1['Cumulative MA'].iloc[-1]
        total_employee_contribution_1 = total_cpf_contribution_1 * (
                df_1['Age'].apply(get_cpf_rates).apply(lambda x: x[1]).mean() / df_1['Age'].apply(get_cpf_rates).apply(
            lambda x: x[2]).mean())
        total_oa_1 = df_1['Cumulative OA'].iloc[-1]
        total_oa_1 = df_1['Cumulative OA'].iloc[-1]
        total_sa_1 = df_1['Cumulative SA'].iloc[-1]
        total_ma_1 = df_1['Cumulative MA'].iloc[-1]
        cumulative_cash_savings_1 = df_1['Cumulative Cash Savings'].iloc[-1]
        net_monthly_salary_1 = (salary_1 * (1 - get_cpf_rates(current_age_1)[1])) - monthly_expenses_1
        net_annual_salary_1 = net_monthly_salary_1 * 12 + bonus_1 + thirteenth_month_1

        total_investment_premium_paid_1 = df_1['Cumulative Investment Premium'].iloc[-1]
        investment_value_1 = df_1['Investment Value'].iloc[-1]
        net_worth_1 = df_1['Net Worth'].iloc[-1]

        st.subheader("Person 1's Financial Analysis")
        st.write("\nIn-Depth Analysis for Person 1:")
        st.write(f"Total years worked: {total_years_worked_1}")
        st.write(f"Total CPF contribution: ${total_cpf_contribution_1:.2f}")
        st.write(f"Total Employee CPF contribution: ${total_employee_contribution_1:.2f}")
        st.write(f"Total OA (Ordinary Account) balance: ${total_oa_1:.2f}")
        st.write(f"Total SA (Special Account) balance: ${total_sa_1:.2f}")
        st.write(f"Total MA (MediSave Account) balance: ${total_ma_1:.2f}")
        st.write(f"Cumulative Cash Savings: ${cumulative_cash_savings_1:.2f}")
        st.write(f"Net Monthly Salary: ${net_monthly_salary_1:.2f}")
        st.write(f"Net Annual Salary: ${net_annual_salary_1:.2f}")
        st.write(f"Total Investment Premium Paid: ${total_investment_premium_paid_1:.2f}")
        st.write(f"Total Investment Value: ${investment_value_1:.2f}")
        st.write(f"Net Worth: ${net_worth_1:.2f}")

        # Format the DataFrame to show dollar signs and two decimal places
        df_1 = df_1.style.format({
            'Cumulative Cash Savings': '${:,.2f}',
            'Cumulative OA': '${:,.2f}',
            'Cumulative SA': '${:,.2f}',
            'Cumulative MA': '${:,.2f}',
            'Cumulative Total CPF': '${:,.2f}',
            'Cumulative Investment Premium': '${:,.2f}',
            'Investment Value': '${:,.2f}',
            'Net Worth': '${:,.2f}'
        })

        st.write(df_1)

        # Plotting the net worth for Person 1
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df_1.data['Age'], df_1.data['Net Worth'], marker='o', linestyle='-', color='b', label='Net Worth')
        ax.set_xlabel('Age')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Net Worth Over Time for Person 1')
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        total_years_worked_2 = current_age_2 - start_age_2
        total_cpf_contribution_2 = df_2['Cumulative OA'].iloc[-1] + df_2['Cumulative SA'].iloc[-1] + \
                                   df_2['Cumulative MA'].iloc[-1]
        total_employee_contribution_2 = total_cpf_contribution_2 * (
                df_2['Age'].apply(get_cpf_rates).apply(lambda x: x[1]).mean() / df_2['Age'].apply(get_cpf_rates).apply(
            lambda x: x[2]).mean())
        total_oa_2 = df_2['Cumulative OA'].iloc[-1]
        total_sa_2 = df_2['Cumulative SA'].iloc[-1]
        total_ma_2 = df_2['Cumulative MA'].iloc[-1]
        cumulative_cash_savings_2 = df_2['Cumulative Cash Savings'].iloc[-1]
        net_monthly_salary_2 = (salary_2 * (1 - get_cpf_rates(current_age_2)[1])) - monthly_expenses_2
        net_annual_salary_2 = net_monthly_salary_2 * 12 + bonus_2 + thirteenth_month_2

        total_investment_premium_paid_2 = df_2['Cumulative Investment Premium'].iloc[-1]
        investment_value_2 = df_2['Investment Value'].iloc[-1]
        net_worth_2 = df_2['Net Worth'].iloc[-1]

        st.subheader("Person 2's Financial Analysis")
        st.write("\nIn-Depth Analysis for Person 2:")
        st.write(f"Total years worked: {total_years_worked_2}")
        st.write(f"Total CPF contribution: ${total_cpf_contribution_2:.2f}")
        st.write(f"Total Employee CPF contribution: ${total_employee_contribution_2:.2f}")
        st.write(f"Total OA (Ordinary Account) balance: ${total_oa_2:.2f}")
        st.write(f"Total SA (Special Account) balance: ${total_sa_2:.2f}")
        st.write(f"Total MA (MediSave Account) balance: ${total_ma_2:.2f}")
        st.write(f"Cumulative Cash Savings: ${cumulative_cash_savings_2:.2f}")
        st.write(f"Net Monthly Salary: ${net_monthly_salary_2:.2f}")
        st.write(f"Net Annual Salary: ${net_annual_salary_2:.2f}")
        st.write(f"Total Investment Premium Paid: ${total_investment_premium_paid_2:.2f}")
        st.write(f"Total Investment Value: ${investment_value_2:.2f}")
        st.write(f"Net Worth: ${net_worth_2:.2f}")

        # Format the DataFrame to show dollar signs and two decimal places
        df_2 = df_2.style.format({
            'Cumulative Cash Savings': '${:,.2f}',
            'Cumulative OA': '${:,.2f}',
            'Cumulative SA': '${:,.2f}',
            'Cumulative MA': '${:,.2f}',
            'Cumulative Total CPF': '${:,.2f}',
            'Cumulative Investment Premium': '${:,.2f}',
            'Investment Value': '${:,.2f}',
            'Net Worth': '${:,.2f}'
        })

        st.write(df_2)

        # Plotting the net worth for Person 2
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df_2.data['Age'], df_2.data['Net Worth'], marker='o', linestyle='-', color='b', label='Net Worth')
        ax.set_xlabel('Age')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Net Worth Over Time for Person 2')
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        # Align financial data based on age range
        df_combined = align_financial_data(df_1.data, df_2.data, start_age_1, start_age_2)

        # Format the combined DataFrame to show dollar signs and two decimal places
        df_combined = df_combined.style.format({
            'Cumulative Cash Savings': '${:,.2f}',
            'Cumulative OA': '${:,.2f}',
            'Cumulative SA': '${:,.2f}',
            'Cumulative MA': '${:,.2f}',
            'Cumulative Total CPF': '${:,.2f}',
            'Cumulative Investment Premium': '${:,.2f}',
            'Investment Value': '${:,.2f}',
            'Net Worth': '${:,.2f}'
        })

        st.subheader("Combined Financial Analysis")
        st.write(df_combined)

        total_years_worked_combined = max(total_years_worked_1, total_years_worked_2)
        total_cpf_contribution_combined = total_cpf_contribution_1 + total_cpf_contribution_2
        total_employee_contribution_combined = total_employee_contribution_1 + total_employee_contribution_2
        total_oa_combined = total_oa_1 + total_oa_2
        total_sa_combined = total_sa_1 + total_sa_2
        total_ma_combined = total_ma_1 + total_ma_2
        cumulative_cash_savings_combined = cumulative_cash_savings_1 + cumulative_cash_savings_2
        net_monthly_salary_combined = net_monthly_salary_1 + net_monthly_salary_2
        net_annual_salary_combined = net_annual_salary_1 + net_annual_salary_2
        total_investment_premium_paid_combined = total_investment_premium_paid_1 + total_investment_premium_paid_2
        investment_value_combined = investment_value_1 + investment_value_2
        net_worth_combined = net_worth_1 + net_worth_2

        st.write("\nCombined In-Depth Analysis:")
        st.write(f"Total years worked: {total_years_worked_combined}")
        st.write(f"Total CPF contribution: ${total_cpf_contribution_combined:.2f}")
        st.write(f"Total Employee CPF contribution: ${total_employee_contribution_combined:.2f}")
        st.write(f"Total OA (Ordinary Account) balance: ${total_oa_combined:.2f}")
        st.write(f"Total SA (Special Account) balance: ${total_sa_combined:.2f}")
        st.write(f"Total MA (MediSave Account) balance: ${total_ma_combined:.2f}")
        st.write(f"Cumulative Cash Savings: ${cumulative_cash_savings_combined:.2f}")
        st.write(f"Net Monthly Salary: ${net_monthly_salary_combined:.2f}")
        st.write(f"Net Annual Salary: ${net_annual_salary_combined:.2f}")
        st.write(f"Total Investment Premium Paid: ${total_investment_premium_paid_combined:.2f}")
        st.write(f"Total Investment Value: ${investment_value_combined:.2f}")
        st.write(f"Net Worth: ${net_worth_combined:.2f}")

        # Plotting the combined net worth
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df_combined.data['Year'], df_combined.data['Net Worth'], marker='o', linestyle='-', color='b',
                label='Net Worth')
        ax.set_xlabel('Year')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Combined Net Worth Over Time')
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
