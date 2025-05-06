import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os

# Function to save a profile
def save_profile(profile_name, data):
    if not os.path.exists("profiles"):
        os.makedirs("profiles")
    with open(f"profiles/{profile_name}.json", "w") as f:
        json.dump(data, f)

# Function to load a profile
def load_profile(profile_name):
    with open(f"profiles/{profile_name}.json", "r") as f:
        return json.load(f)

# Function to list all saved profiles
def list_profiles():
    if not os.path.exists("profiles"):
        return []
    return [f.replace(".json", "") for f in os.listdir("profiles") if f.endswith(".json")]

# Function to delete a profile
def delete_profile(profile_name):
    if os.path.exists(f"profiles/{profile_name}.json"):
        os.remove(f"profiles/{profile_name}.json")

# CPF allocation rates based on age
def get_cpf_allocation_rates(age):
    if age < 35:
        return 0.6227, 0.1621, 0.2152
    elif age < 45:
        return 0.5859, 0.1933, 0.2208
    elif age < 55:
        return 0.5117, 0.2421, 0.2462
    elif age < 65:
        return 0.2123, 0.3929, 0.3948
    else:
        return 0.085, 0.405, 0.51

# CPF contribution rates based on age
def get_cpf_rates(age):
    if age < 55:
        return 0.17, 0.20, 0.37
    elif age < 65:
        return 0.13, 0.13, 0.26
    else:
        return 0.075, 0.05, 0.125

# Add a new function to calculate CPF balance without investment
def calculate_cpf_balance_without_investment(salary, bonus, thirteenth_month, monthly_expenses, current_age, projected_age,
                                              milestones, existing_oa=0.0, existing_sa=0.0, existing_ma=0.0, existing_cash=0.0):
    cpf_balance = {
        'Year': [],
        'Age': [],
        'Cumulative Cash Savings': [],
        'Cumulative OA': [],
        'Cumulative SA': [],
        'Cumulative MA': [],
        'Cumulative Total CPF': [],
        'Net Worth': []
    }
    years_worked = projected_age - current_age + 1
    cumulative_cash_savings = existing_cash
    cumulative_oa = existing_oa
    cumulative_sa = existing_sa
    cumulative_ma = existing_ma
    cumulative_total_cpf = existing_oa + existing_sa + existing_ma
    net_worth = existing_cash + existing_oa + existing_sa + existing_ma

    for year in range(years_worked):
        age = current_age + year
        oa_rate, sa_rate, ma_rate = get_cpf_allocation_rates(age)
        employer_rate, employee_rate, total_rate = get_cpf_rates(age)
        annual_income = salary * 12 + bonus + thirteenth_month
        cpf_contribution = annual_income * total_rate
        net_monthly_salary = (salary * (1 - employee_rate)) - monthly_expenses
        net_annual_salary = (net_monthly_salary * 12) + (bonus * (1 - employee_rate)) + (
            thirteenth_month * (1 - employee_rate))
        cumulative_cash_savings += net_annual_salary
        cumulative_oa += cpf_contribution * oa_rate
        cumulative_sa += cpf_contribution * sa_rate
        cumulative_ma += cpf_contribution * ma_rate
        cumulative_total_cpf = cumulative_oa + cumulative_sa + cumulative_ma
        net_worth = cumulative_cash_savings + cumulative_oa + cumulative_sa + cumulative_ma

        # Apply financial milestones
        if age in milestones:
            net_worth += milestones[age]
            cumulative_cash_savings += milestones[age]

        cpf_balance['Year'].append(year + 1)
        cpf_balance['Age'].append(age)
        cpf_balance['Cumulative Cash Savings'].append(round(cumulative_cash_savings, 2))
        cpf_balance['Cumulative OA'].append(round(cumulative_oa, 2))
        cpf_balance['Cumulative SA'].append(round(cumulative_sa, 2))
        cpf_balance['Cumulative MA'].append(round(cumulative_ma, 2))
        cpf_balance['Cumulative Total CPF'].append(round(cumulative_total_cpf, 2))
        cpf_balance['Net Worth'].append(round(net_worth, 2))

    return cpf_balance

# Calculate CPF balance and financial metrics
def calculate_cpf_balance(salary, bonus, thirteenth_month, monthly_expenses, current_age, projected_age,
                          annual_investment_premium, annual_interest_rate, milestones,
                          existing_oa=0.0, existing_sa=0.0, existing_ma=0.0, existing_cash=0.0,
                          investment_current_age=0):
    cpf_balance = {
        'Year': [],
        'Age': [],
        'Cumulative Cash Savings': [],
        'Cumulative OA': [],
        'Cumulative SA': [],
        'Cumulative MA': [],
        'Cumulative Total CPF': [],
        'Cumulative Investment Premium': [],
        'Investment Value': [],
        'Net Worth': []
    }
    years_worked = projected_age - current_age + 1
    cumulative_cash_savings = existing_cash
    cumulative_oa = existing_oa
    cumulative_sa = existing_sa
    cumulative_ma = existing_ma
    cumulative_total_cpf = existing_oa + existing_sa + existing_ma
    cumulative_investment_premium = 0.0
    investment_value = 0.0
    net_worth = existing_cash + existing_oa + existing_sa + existing_ma
    milestone_percentage = 1.0  # Adjust this percentage if needed

    for year in range(years_worked):
        age = current_age + year
        oa_rate, sa_rate, ma_rate = get_cpf_allocation_rates(age)
        employer_rate, employee_rate, total_rate = get_cpf_rates(age)
        annual_income = salary * 12 + bonus + thirteenth_month
        cpf_contribution = annual_income * total_rate
        net_monthly_salary = (salary * (1 - employee_rate)) - monthly_expenses
        net_annual_salary = (net_monthly_salary * 12) + (bonus * (1 - employee_rate)) + (
            thirteenth_month * (1 - employee_rate))
        cumulative_cash_savings += net_annual_salary
        # Apply annual investment premium only after the investment start age
        if age >= investment_current_age:
            cumulative_cash_savings -= annual_investment_premium
            cumulative_investment_premium += annual_investment_premium
            investment_value = (investment_value + annual_investment_premium) * (1 + annual_interest_rate / 100)
        cumulative_oa += cpf_contribution * oa_rate
        cumulative_sa += cpf_contribution * sa_rate
        cumulative_ma += cpf_contribution * ma_rate
        cumulative_total_cpf = cumulative_oa + cumulative_sa + cumulative_ma
        net_worth = cumulative_cash_savings + cumulative_oa + cumulative_sa + cumulative_ma + investment_value
        # Apply financial milestones
        if age in milestones:
            net_worth += milestones[age] * milestone_percentage
            cumulative_cash_savings += milestones[age] * milestone_percentage  # Ensure the effect is permanent
        cpf_balance['Year'].append(year + 1)
        cpf_balance['Age'].append(age)
        cpf_balance['Cumulative Cash Savings'].append(round(cumulative_cash_savings, 2))
        cpf_balance['Cumulative OA'].append(round(cumulative_oa, 2))
        cpf_balance['Cumulative SA'].append(round(cumulative_sa, 2))
        cpf_balance['Cumulative MA'].append(round(cumulative_ma, 2))
        cpf_balance['Cumulative Total CPF'].append(round(cumulative_total_cpf, 2))
        cpf_balance['Cumulative Investment Premium'].append(round(cumulative_investment_premium, 2))
        cpf_balance['Investment Value'].append(round(investment_value, 2))
        cpf_balance['Net Worth'].append(round(net_worth, 2))
    return cpf_balance

# Align financial data for combined analysis
def align_financial_data(df1, df2, start_year_1, start_year_2):
    min_year = min(start_year_1, start_year_2)
    max_year = max(df1['Year'].iloc[-1], df2['Year'].iloc[-1])
    combined_data = {
        'Year': list(range(min_year, max_year + 1)),
        'Cumulative Cash Savings': [],
        'Cumulative OA': [],
        'Cumulative SA': [],
        'Cumulative MA': [],
        'Cumulative Total CPF': [],
        'Cumulative Investment Premium': [],
        'Investment Value': [],
        'Net Worth': []
    }
    cumulative_cash_savings_1 = cumulative_cash_savings_2 = 0
    cumulative_oa_1 = cumulative_oa_2 = 0
    cumulative_sa_1 = cumulative_sa_2 = 0
    cumulative_ma_1 = cumulative_ma_2 = 0
    cumulative_total_cpf_1 = cumulative_total_cpf_2 = 0
    cumulative_investment_premium_1 = cumulative_investment_premium_2 = 0
    investment_value_1 = investment_value_2 = 0
    net_worth_1 = net_worth_2 = 0
    for year in combined_data['Year']:
        if year in df1['Year'].values:
            idx = df1['Year'].values.tolist().index(year)
            cumulative_cash_savings_1 = df1['Cumulative Cash Savings'].iloc[idx]
            cumulative_oa_1 = df1['Cumulative OA'].iloc[idx]
            cumulative_sa_1 = df1['Cumulative SA'].iloc[idx]
            cumulative_ma_1 = df1['Cumulative MA'].iloc[idx]
            cumulative_total_cpf_1 = df1['Cumulative Total CPF'].iloc[idx]
            # Check if 'Cumulative Investment Premium' exists in df1
            cumulative_investment_premium_1 = df1['Cumulative Investment Premium'].iloc[idx] if 'Cumulative Investment Premium' in df1.columns else 0
            investment_value_1 = df1['Investment Value'].iloc[idx] if 'Investment Value' in df1.columns else 0
            net_worth_1 = df1['Net Worth'].iloc[idx]
        if year in df2['Year'].values:
            idx = df2['Year'].values.tolist().index(year)
            cumulative_cash_savings_2 = df2['Cumulative Cash Savings'].iloc[idx]
            cumulative_oa_2 = df2['Cumulative OA'].iloc[idx]
            cumulative_sa_2 = df2['Cumulative SA'].iloc[idx]
            cumulative_ma_2 = df2['Cumulative MA'].iloc[idx]
            cumulative_total_cpf_2 = df2['Cumulative Total CPF'].iloc[idx]
            # Check if 'Cumulative Investment Premium' exists in df2
            cumulative_investment_premium_2 = df2['Cumulative Investment Premium'].iloc[idx] if 'Cumulative Investment Premium' in df2.columns else 0
            investment_value_2 = df2['Investment Value'].iloc[idx] if 'Investment Value' in df2.columns else 0
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

# Streamlit App
st.header("Financial Analysis")
st.subheader("Key in your information here")

# Initialize session state for profile data
if "profile_data" not in st.session_state:
    st.session_state.profile_data = {
        "analysis_type": "Single",
        "person_1": {
            "name": "",
            "salary": 0.0,
            "bonus": 0.0,
            "thirteenth_month": 0.0,
            "monthly_expenses": 0.0,
            "current_age": 0,
            "projected_age": 0,
            "annual_investment_premium": 0.0,
            "annual_interest_rate": 0.0,
            "milestones": {},
            "existing_oa": 0.0,
            "existing_sa": 0.0,
            "existing_ma": 0.0,
            "existing_cash": 0.0,
            "investment_current_age": 0
        }
    }

# Dynamically add "person_2" only if the analysis type is "Couple"
if st.session_state.profile_data["analysis_type"] == "Couple":
    if "person_2" not in st.session_state.profile_data:
        st.session_state.profile_data["person_2"] = {
            "name": "",
            "salary": 0.0,
            "bonus": 0.0,
            "thirteenth_month": 0.0,
            "monthly_expenses": 0.0,
            "current_age": 0,
            "projected_age": 0,
            "annual_investment_premium": 0.0,
            "annual_interest_rate": 0.0,
            "milestones": {},
            "existing_oa": 0.0,
            "existing_sa": 0.0,
            "existing_ma": 0.0,
            "existing_cash": 0.0,
            "investment_current_age": 0
        }

# Profile Management
st.sidebar.header("Profile Management")
profile_action = st.sidebar.radio("Profile Action", ["Create New Profile", "Load Existing Profile", "Delete Profile"])
if profile_action == "Create New Profile":
    profile_name = st.sidebar.text_input("Enter a name for your profile:")
    if st.sidebar.button("Save Profile"):
        if not profile_name:
            st.sidebar.error("Please enter a profile name.")
        else:
            profile_data = {
                "analysis_type": st.session_state.profile_data["analysis_type"],
                "person_1": st.session_state.profile_data["person_1"]
            }
            if st.session_state.profile_data["analysis_type"] == "Couple":
                profile_data["person_2"] = st.session_state.profile_data["person_2"]
            save_profile(profile_name, profile_data)
            st.sidebar.success(f"Profile '{profile_name}' saved successfully!")
elif profile_action == "Load Existing Profile":
    profiles = list_profiles()
    if not profiles:
        st.sidebar.warning("No profiles found. Please create a new profile.")
    else:
        selected_profile = st.sidebar.selectbox("Select a profile to load:", profiles)
        if st.sidebar.button("Load Profile"):
            profile_data = load_profile(selected_profile)
            st.session_state.profile_data = {
                "analysis_type": profile_data.get("analysis_type", "Single"),
                "person_1": profile_data.get("person_1", {}),
                "person_2": profile_data.get("person_2", {}) if profile_data.get("analysis_type") == "Couple" else {}
            }
            st.sidebar.success(f"Profile '{selected_profile}' loaded successfully!")
elif profile_action == "Delete Profile":
    profiles = list_profiles()
    if not profiles:
        st.sidebar.warning("No profiles found. Please create a new profile.")
    else:
        selected_profile = st.sidebar.selectbox("Select a profile to delete:", profiles)
        if st.sidebar.button("Delete Profile"):
            delete_profile(selected_profile)
            st.sidebar.success(f"Profile '{selected_profile}' deleted successfully!")

# Input Fields
analysis_type = st.radio("Is this analysis for a single person or a couple?", ('Single', 'Couple'))
st.session_state.profile_data["analysis_type"] = analysis_type

# Dynamically initialize "person_2" if switching to "Couple"
if analysis_type == "Couple" and "person_2" not in st.session_state.profile_data:
    st.session_state.profile_data["person_2"] = {
        "name": "",
        "salary": 0.0,
        "bonus": 0.0,
        "thirteenth_month": 0.0,
        "monthly_expenses": 0.0,
        "current_age": 0,
        "projected_age": 0,
        "annual_investment_premium": 0.0,
        "annual_interest_rate": 0.0,
        "milestones": {},
        "existing_oa": 0.0,
        "existing_sa": 0.0,
        "existing_ma": 0.0,
        "existing_cash": 0.0,
        "investment_current_age": 0
    }

if analysis_type == 'Single':
    # Current Year Input
    current_year = st.number_input("Enter the current year:", min_value=1900, step=1, value=2025)

    # Single person inputs
    st.subheader("Person 1")
    name_1 = st.text_input("Enter the name of Person 1:", value=st.session_state.profile_data["person_1"]["name"])
    salary = st.number_input("Enter your monthly gross income:", min_value=0.0, step=100.0,
                             value=st.session_state.profile_data["person_1"]["salary"])
    bonus = st.number_input("Enter your annual bonus:", min_value=0.0, step=100.0,
                            value=st.session_state.profile_data["person_1"]["bonus"])
    thirteenth_month = st.number_input("Enter your 13th month salary:", min_value=0.0, step=100.0,
                                       value=st.session_state.profile_data["person_1"]["thirteenth_month"])
    monthly_expenses = st.number_input("Enter your monthly expenses:", min_value=0.0, step=100.0,
                                       value=st.session_state.profile_data["person_1"]["monthly_expenses"])
    current_age = st.number_input("Enter your current age:", min_value=0, step=1,
                                  value=st.session_state.profile_data["person_1"]["current_age"])
    projected_age = st.number_input("Enter your projected age:", min_value=0, step=1,
                                    value=st.session_state.profile_data["person_1"]["projected_age"])
    investment_current_age = st.number_input("Enter the start age for annual investment premium:", min_value=0, step=1,
                                             value=st.session_state.profile_data["person_1"]["investment_current_age"])
    annual_investment_premium = st.number_input("Enter your annual investment premium:", min_value=0.0, step=100.0,
                                                value=st.session_state.profile_data["person_1"]["annual_investment_premium"])
    annual_interest_rate = st.number_input("Enter the annual investment interest rate (as a percentage):", min_value=0.0, step=0.1,
                                           value=st.session_state.profile_data["person_1"]["annual_interest_rate"])
    existing_oa = st.number_input("Enter your OA balance before you started working full time:", min_value=0.0, step=100.0,
                                  value=st.session_state.profile_data["person_1"]["existing_oa"])
    existing_sa = st.number_input("Enter your SA balance before you started working full time:", min_value=0.0, step=100.0,
                                  value=st.session_state.profile_data["person_1"]["existing_sa"])
    existing_ma = st.number_input("Enter your MA balance before you started working full time:", min_value=0.0, step=100.0,
                                  value=st.session_state.profile_data["person_1"]["existing_ma"])
    existing_cash = st.number_input("Enter your cash balance before you started working full time:", min_value=0.0, step=100.0,
                                    value=st.session_state.profile_data["person_1"]["existing_cash"])

    st.subheader("Financial Milestones")
    num_milestones = st.number_input("Enter the number of financial milestones:", min_value=0, step=1)
    milestones = {}
    for i in range(num_milestones):
        age = st.number_input(f"Enter the age for milestone {i + 1}:", min_value=0, step=1, key=f"age_{i}")
        amount = st.number_input(
            f"Enter the amount for milestone {i + 1} (negative for expenses, positive for gains):",
            step=100.0, key=f"amount_{i}")
        milestones[age] = amount

    # Update session state with current inputs
    st.session_state.profile_data["person_1"] = {
        "name": name_1,
        "salary": salary,
        "bonus": bonus,
        "thirteenth_month": thirteenth_month,
        "monthly_expenses": monthly_expenses,
        "current_age": current_age,
        "projected_age": projected_age,
        "investment_current_age": investment_current_age,
        "annual_investment_premium": annual_investment_premium,
        "annual_interest_rate": annual_interest_rate,
        "milestones": milestones,
        "existing_oa": existing_oa,
        "existing_sa": existing_sa,
        "existing_ma": existing_ma,
        "existing_cash": existing_cash
    }

    if st.button("Calculate"):
        cpf_balance = calculate_cpf_balance(salary, bonus, thirteenth_month, monthly_expenses, current_age,
                                            projected_age, annual_investment_premium, annual_interest_rate, milestones,
                                            existing_oa=existing_oa, existing_sa=existing_sa,
                                            existing_ma=existing_ma, existing_cash=existing_cash,
                                            investment_current_age=investment_current_age)
        cpf_balance_no_investment = calculate_cpf_balance_without_investment(
            salary, bonus, thirteenth_month, monthly_expenses, current_age, projected_age, milestones,
            existing_oa=existing_oa, existing_sa=existing_sa, existing_ma=existing_ma, existing_cash=existing_cash
        )
        df = pd.DataFrame(cpf_balance)
        df_no_investment = pd.DataFrame(cpf_balance_no_investment)

        # Add Year column based on current year
        df['Year'] = df['Age'].apply(lambda age: current_year + (age - current_age))
        df_no_investment['Year'] = df_no_investment['Age'].apply(lambda age: current_year + (age - current_age))

        # Format DataFrame for better readability
        df_formatted = df.style.format({
            "Cumulative Cash Savings": "${:,.2f}",
            "Cumulative OA": "${:,.2f}",
            "Cumulative SA": "${:,.2f}",
            "Cumulative MA": "${:,.2f}",
            "Cumulative Total CPF": "${:,.2f}",
            "Cumulative Investment Premium": "${:,.2f}",
            "Investment Value": "${:,.2f}",
            "Net Worth": "${:,.2f}"
        })
        df_no_investment_formatted = df_no_investment.style.format({
            "Cumulative Cash Savings": "${:,.2f}",
            "Cumulative OA": "${:,.2f}",
            "Cumulative SA": "${:,.2f}",
            "Cumulative MA": "${:,.2f}",
            "Cumulative Total CPF": "${:,.2f}",
            "Net Worth": "${:,.2f}"
        })

        # Display Results in a collapsible section
        st.subheader(f"{name_1}'s Full Analysis")
        with st.expander(f"{name_1}'s Full Analysis"):
            st.write(f"In-Depth Analysis for {name_1}:")
            st.write(df_formatted)

            # Beautified Summary Table
            summary_data = {
                "Metric": [
                    "Total Years Worked",
                    "Total CPF Contribution",
                    "Total Employee CPF Contribution",
                    "Total OA (Ordinary Account) Balance",
                    "Total SA (Special Account) Balance",
                    "Total MA (MediSave Account) Balance",
                    "Cumulative Cash Savings",
                    "Net Monthly Salary",
                    "Net Annual Salary",
                    "Total Investment Premium Paid",
                    "Total Investment Value",
                    "Net Worth"
                ],
                "Value": [
                    projected_age - current_age,
                    sum(df['Cumulative Total CPF']),
                    sum(df['Cumulative Total CPF']) * 0.2,
                    df['Cumulative OA'].iloc[-1],
                    df['Cumulative SA'].iloc[-1],
                    df['Cumulative MA'].iloc[-1],
                    df['Cumulative Cash Savings'].iloc[-1],
                    (salary * 0.8) - monthly_expenses,
                    ((salary * 0.8) - monthly_expenses) * 12,
                    df['Cumulative Investment Premium'].iloc[-1],
                    df['Investment Value'].iloc[-1],
                    df['Net Worth'].iloc[-1]
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df_display = summary_df.copy()
            summary_df_display['Value'] = summary_df_display.apply(
                lambda row: f"{int(row['Value'])}" if row['Metric'] == "Total Years Worked" else (
                    "${:,.2f}".format(row['Value']) if isinstance(row['Value'], (int, float)) else row['Value']
                ), axis=1
            )
            st.table(summary_df_display)

            # Format the summary table for display
            summary_df_display = summary_df.copy()
            summary_df_display['Value'] = summary_df_display.apply(
                lambda row: f"{int(row['Value'])}" if row['Metric'] == "Total Years Worked" else (
                    "${:,.2f}".format(row['Value']) if isinstance(row['Value'], (int, float)) else row['Value']
                ), axis=1
            )

            st.table(summary_df_display)

            # Plot Net Worth Over Time (With and Without Investment)
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=df['Age'], y=df['Net Worth'], mode='lines+markers', name='Net Worth (With Investment)'))
            fig.add_trace(go.Scatter(x=df_no_investment['Age'], y=df_no_investment['Net Worth'], mode='lines+markers',
                                     name='Net Worth (Without Investment)'))
            fig.update_layout(title=f"{name_1}'s Net Worth Over Time", xaxis_title='Age', yaxis_title='Amount ($)',
                              template='plotly_white')
            st.plotly_chart(fig)

elif analysis_type == 'Couple':
    # Current Year Input
    current_year = st.number_input("Enter the current year:", min_value=1900, step=1, value=2025)

    # Person 1 inputs
    st.subheader("Person 1")
    name_1 = st.text_input("Enter the name of Person 1:", value=st.session_state.profile_data["person_1"]["name"],
                           key="name_1")
    salary_1 = st.number_input(f"Enter {name_1}'s monthly gross income:", min_value=0.0, step=100.0,
                               value=st.session_state.profile_data["person_1"]["salary"], key="salary_1")
    bonus_1 = st.number_input(f"Enter {name_1}'s annual bonus:", min_value=0.0, step=100.0,
                              value=st.session_state.profile_data["person_1"]["bonus"], key="bonus_1")
    thirteenth_month_1 = st.number_input(f"Enter {name_1}'s 13th month salary:", min_value=0.0, step=100.0,
                                         value=st.session_state.profile_data["person_1"]["thirteenth_month"],
                                         key="thirteenth_month_1")
    monthly_expenses_1 = st.number_input(f"Enter {name_1}'s monthly expenses:", min_value=0.0, step=100.0,
                                         value=st.session_state.profile_data["person_1"]["monthly_expenses"],
                                         key="monthly_expenses_1")
    current_age_1 = st.number_input(f"Enter {name_1}'s current age:", min_value=0,
                                    step=1,
                                    value=st.session_state.profile_data["person_1"]["current_age"], key="current_age_1")
    projected_age_1 = st.number_input(f"Enter {name_1}'s projected age:", min_value=0, step=1,
                                      value=st.session_state.profile_data["person_1"]["projected_age"],
                                      key="projected_age_1")
    investment_current_age_1 = st.number_input(f"Enter {name_1}'s start age for annual investment premium:",
                                               min_value=0, step=1,
                                               value=st.session_state.profile_data["person_1"][
                                                   "investment_current_age"], key="investment_current_age_1")
    annual_investment_premium_1 = st.number_input(f"Enter {name_1}'s annual investment premium:", min_value=0.0,
                                                  step=100.0,
                                                  value=st.session_state.profile_data["person_1"][
                                                      "annual_investment_premium"], key="annual_investment_premium_1")
    annual_interest_rate_1 = st.number_input(f"Enter {name_1}'s annual investment interest rate (as a percentage):",
                                             min_value=0.0, step=0.1,
                                             value=st.session_state.profile_data["person_1"]["annual_interest_rate"],
                                             key="annual_interest_rate_1")
    existing_oa_1 = st.number_input(f"Enter {name_1}'s OA balance before you start working full time:", min_value=0.0,
                                    step=100.0,
                                    value=st.session_state.profile_data["person_1"]["existing_oa"], key="existing_oa_1")
    existing_sa_1 = st.number_input(f"Enter {name_1}'s SA balance before you start working full time:", min_value=0.0,
                                    step=100.0,
                                    value=st.session_state.profile_data["person_1"]["existing_sa"], key="existing_sa_1")
    existing_ma_1 = st.number_input(f"Enter {name_1}'s MA balance before you start working full time:", min_value=0.0,
                                    step=100.0,
                                    value=st.session_state.profile_data["person_1"]["existing_ma"], key="existing_ma_1")
    existing_cash_1 = st.number_input(f"Enter {name_1}'s cash balance before you start working full time:",
                                      min_value=0.0, step=100.0,
                                      value=st.session_state.profile_data["person_1"]["existing_cash"],
                                      key="existing_cash_1")

    # Person 1 Milestones
    st.subheader(f"Financial Milestones for {name_1}")
    num_milestones_1 = st.number_input(
        f"Enter the number of financial milestones for {name_1}:",
        min_value=0,
        step=1,
        key=f"num_milestones_1"  # Unique key for Person 1's milestone count
    )
    milestones_1 = {}
    for i in range(num_milestones_1):
        age = st.number_input(
            f"Enter the age for milestone {i + 1} ({name_1}'s age):",
            min_value=0,
            step=1,
            key=f"age_1_{i}"  # Unique key for Person 1's milestone age
        )
        amount = st.number_input(
            f"Enter the amount for milestone {i + 1} (negative for expenses, positive for gains):",
            step=100.0,
            key=f"amount_1_{i}"  # Unique key for Person 1's milestone amount
        )
        milestones_1[age] = amount

    # Person 2 inputs
    st.subheader("Person 2")
    name_2 = st.text_input("Enter the name of Person 2:", value=st.session_state.profile_data["person_2"]["name"],
                           key="name_2")
    salary_2 = st.number_input(f"Enter {name_2}'s monthly gross income:", min_value=0.0, step=100.0,
                               value=st.session_state.profile_data["person_2"]["salary"], key="salary_2")
    bonus_2 = st.number_input(f"Enter {name_2}'s annual bonus:", min_value=0.0, step=100.0,
                              value=st.session_state.profile_data["person_2"]["bonus"], key="bonus_2")
    thirteenth_month_2 = st.number_input(f"Enter {name_2}'s 13th month salary:", min_value=0.0, step=100.0,
                                         value=st.session_state.profile_data["person_2"]["thirteenth_month"],
                                         key="thirteenth_month_2")
    monthly_expenses_2 = st.number_input(f"Enter {name_2}'s monthly expenses:", min_value=0.0, step=100.0,
                                         value=st.session_state.profile_data["person_2"]["monthly_expenses"],
                                         key="monthly_expenses_2")
    current_age_2 = st.number_input(f"Enter {name_2}'s current age:", min_value=0,
                                    step=1,
                                    value=st.session_state.profile_data["person_2"]["current_age"], key="current_age_2")
    projected_age_2 = st.number_input(f"Enter {name_2}'s projected age:", min_value=0, step=1,
                                      value=st.session_state.profile_data["person_2"]["projected_age"],
                                      key="projected_age_2")
    investment_current_age_2 = st.number_input(f"Enter {name_2}'s start age for annual investment premium:",
                                               min_value=0, step=1,
                                               value=st.session_state.profile_data["person_2"][
                                                   "investment_current_age"], key="investment_current_age_2")
    annual_investment_premium_2 = st.number_input(f"Enter {name_2}'s annual investment premium:", min_value=0.0,
                                                  step=100.0,
                                                  value=st.session_state.profile_data["person_2"][
                                                      "annual_investment_premium"], key="annual_investment_premium_2")
    annual_interest_rate_2 = st.number_input(f"Enter {name_2}'s annual investment interest rate (as a percentage):",
                                             min_value=0.0, step=0.1,
                                             value=st.session_state.profile_data["person_2"]["annual_interest_rate"],
                                             key="annual_interest_rate_2")
    existing_oa_2 = st.number_input(f"Enter {name_2}'s OA balance before you start working full time:", min_value=0.0,
                                    step=100.0,
                                    value=st.session_state.profile_data["person_2"]["existing_oa"], key="existing_oa_2")
    existing_sa_2 = st.number_input(f"Enter {name_2}'s SA balance before you start working full time:", min_value=0.0,
                                    step=100.0,
                                    value=st.session_state.profile_data["person_2"]["existing_sa"], key="existing_sa_2")
    existing_ma_2 = st.number_input(f"Enter {name_2}'s MA balance before you start working full time:", min_value=0.0,
                                    step=100.0,
                                    value=st.session_state.profile_data["person_2"]["existing_ma"], key="existing_ma_2")
    existing_cash_2 = st.number_input(f"Enter {name_2}'s cash balance before you start working full time:",
                                      min_value=0.0, step=100.0,
                                      value=st.session_state.profile_data["person_2"]["existing_cash"],
                                      key="existing_cash_2")

    st.subheader(f"Financial Milestones for {name_2}")
    num_milestones_2 = st.number_input(f"Enter the number of financial milestones for {name_2}:", min_value=0, step=1)
    milestones_2 = {}
    for i in range(num_milestones_2):
        age = st.number_input(f"Enter the age for milestone {i + 1} ({name_2}'s age):", min_value=0, step=1,
                              key=f"age_2_{i}")
        amount = st.number_input(
            f"Enter the amount for milestone {i + 1} (negative for expenses, positive for gains):", step=100.0,
            key=f"amount_2_{i}")
        milestones_2[age] = amount

    # Update session state with current inputs
    st.session_state.profile_data["person_1"] = {
        "name": name_1,
        "salary": salary_1,
        "bonus": bonus_1,
        "thirteenth_month": thirteenth_month_1,
        "monthly_expenses": monthly_expenses_1,
        "current_age": current_age_1,
        "projected_age": projected_age_1,
        "investment_current_age": investment_current_age_1,
        "annual_investment_premium": annual_investment_premium_1,
        "annual_interest_rate": annual_interest_rate_1,
        "milestones": milestones_1,
        "existing_oa": existing_oa_1,
        "existing_sa": existing_sa_1,
        "existing_ma": existing_ma_1,
        "existing_cash": existing_cash_1
    }
    st.session_state.profile_data["person_2"] = {
        "name": name_2,
        "salary": salary_2,
        "bonus": bonus_2,
        "thirteenth_month": thirteenth_month_2,
        "monthly_expenses": monthly_expenses_2,
        "current_age": current_age_2,
        "projected_age": projected_age_2,
        "investment_current_age": investment_current_age_2,
        "annual_investment_premium": annual_investment_premium_2,
        "annual_interest_rate": annual_interest_rate_2,
        "milestones": milestones_2,
        "existing_oa": existing_oa_2,
        "existing_sa": existing_sa_2,
        "existing_ma": existing_ma_2,
        "existing_cash": existing_cash_2
    }

    if st.button("Calculate"):
        # Calculate CPF balance for Person 1 (with and without investment)
        cpf_balance_1 = calculate_cpf_balance(
            salary=salary_1,
            bonus=bonus_1,
            thirteenth_month=thirteenth_month_1,
            monthly_expenses=monthly_expenses_1,
            current_age=current_age_1,
            projected_age=projected_age_1,
            annual_investment_premium=annual_investment_premium_1,
            annual_interest_rate=annual_interest_rate_1,
            milestones=milestones_1,
            existing_oa=existing_oa_1,
            existing_sa=existing_sa_1,
            existing_ma=existing_ma_1,
            existing_cash=existing_cash_1,
            investment_current_age=investment_current_age_1
        )
        cpf_balance_1_no_investment = calculate_cpf_balance_without_investment(
            salary=salary_1,
            bonus=bonus_1,
            thirteenth_month=thirteenth_month_1,
            monthly_expenses=monthly_expenses_1,
            current_age=current_age_1,
            projected_age=projected_age_1,
            milestones=milestones_1,
            existing_oa=existing_oa_1,
            existing_sa=existing_sa_1,
            existing_ma=existing_ma_1,
            existing_cash=existing_cash_1
        )

        # Calculate CPF balance for Person 2 (with and without investment)
        cpf_balance_2 = calculate_cpf_balance(
            salary=salary_2,
            bonus=bonus_2,
            thirteenth_month=thirteenth_month_2,
            monthly_expenses=monthly_expenses_2,
            current_age=current_age_2,
            projected_age=projected_age_2,
            annual_investment_premium=annual_investment_premium_2,
            annual_interest_rate=annual_interest_rate_2,
            milestones=milestones_2,
            existing_oa=existing_oa_2,
            existing_sa=existing_sa_2,
            existing_ma=existing_ma_2,
            existing_cash=existing_cash_2,
            investment_current_age=investment_current_age_2
        )
        cpf_balance_2_no_investment = calculate_cpf_balance_without_investment(
            salary=salary_2,
            bonus=bonus_2,
            thirteenth_month=thirteenth_month_2,
            monthly_expenses=monthly_expenses_2,
            current_age=current_age_2,
            projected_age=projected_age_2,
            milestones=milestones_2,
            existing_oa=existing_oa_2,
            existing_sa=existing_sa_2,
            existing_ma=existing_ma_2,
            existing_cash=existing_cash_2
        )

        # Convert results to DataFrames
        df_1 = pd.DataFrame(cpf_balance_1)
        df_1_no_investment = pd.DataFrame(cpf_balance_1_no_investment)
        df_2 = pd.DataFrame(cpf_balance_2)
        df_2_no_investment = pd.DataFrame(cpf_balance_2_no_investment)

        # Add Year column based on current year
        df_1['Year'] = df_1['Age'].apply(lambda age: current_year + (age - current_age_1))
        df_1_no_investment['Year'] = df_1_no_investment['Age'].apply(lambda age: current_year + (age - current_age_1))
        df_2['Year'] = df_2['Age'].apply(lambda age: current_year + (age - current_age_2))
        df_2_no_investment['Year'] = df_2_no_investment['Age'].apply(lambda age: current_year + (age - current_age_2))

        # Align financial data for combined analysis
        df_combined = align_financial_data(df_1, df_2, current_year + (current_age_1 - current_age_1),
                                           current_year + (current_age_2 - current_age_2))
        df_combined_no_investment = align_financial_data(df_1_no_investment, df_2_no_investment,
                                                         current_year + (current_age_1 - current_age_1),
                                                         current_year + (current_age_2 - current_age_2))

        # Format DataFrames for better readability
        df_1_formatted = df_1.style.format({
            "Cumulative Cash Savings": "${:,.2f}",
            "Cumulative OA": "${:,.2f}",
            "Cumulative SA": "${:,.2f}",
            "Cumulative MA": "${:,.2f}",
            "Cumulative Total CPF": "${:,.2f}",
            "Cumulative Investment Premium": "${:,.2f}",
            "Investment Value": "${:,.2f}",
            "Net Worth": "${:,.2f}"
        })
        df_1_no_investment_formatted = df_1_no_investment.style.format({
            "Cumulative Cash Savings": "${:,.2f}",
            "Cumulative OA": "${:,.2f}",
            "Cumulative SA": "${:,.2f}",
            "Cumulative MA": "${:,.2f}",
            "Cumulative Total CPF": "${:,.2f}",
            "Net Worth": "${:,.2f}"
        })
        df_2_formatted = df_2.style.format({
            "Cumulative Cash Savings": "${:,.2f}",
            "Cumulative OA": "${:,.2f}",
            "Cumulative SA": "${:,.2f}",
            "Cumulative MA": "${:,.2f}",
            "Cumulative Total CPF": "${:,.2f}",
            "Cumulative Investment Premium": "${:,.2f}",
            "Investment Value": "${:,.2f}",
            "Net Worth": "${:,.2f}"
        })
        df_2_no_investment_formatted = df_2_no_investment.style.format({
            "Cumulative Cash Savings": "${:,.2f}",
            "Cumulative OA": "${:,.2f}",
            "Cumulative SA": "${:,.2f}",
            "Cumulative MA": "${:,.2f}",
            "Cumulative Total CPF": "${:,.2f}",
            "Net Worth": "${:,.2f}"
        })
        df_combined_formatted = df_combined.style.format({
            "Cumulative Cash Savings": "${:,.2f}",
            "Cumulative OA": "${:,.2f}",
            "Cumulative SA": "${:,.2f}",
            "Cumulative MA": "${:,.2f}",
            "Cumulative Total CPF": "${:,.2f}",
            "Cumulative Investment Premium": "${:,.2f}",
            "Investment Value": "${:,.2f}",
            "Net Worth": "${:,.2f}"
        })
        df_combined_no_investment_formatted = df_combined_no_investment.style.format({
            "Cumulative Cash Savings": "${:,.2f}",
            "Cumulative OA": "${:,.2f}",
            "Cumulative SA": "${:,.2f}",
            "Cumulative MA": "${:,.2f}",
            "Cumulative Total CPF": "${:,.2f}",
            "Net Worth": "${:,.2f}"
        })

        # Display individual financial analyses in collapsible sections
        st.subheader(f"{name_1}'s Full Analysis")
        with st.expander(f"{name_1}'s Full Analysis"):
            st.write(f"In-Depth Analysis for {name_1}:")
            st.write(df_1_formatted)

            # Beautified Summary Table for Person 1
            summary_data_1 = {
                "Metric": [
                    "Total Years Worked",
                    "Total CPF Contribution",
                    "Total Employee CPF Contribution",
                    "Total OA (Ordinary Account) Balance",
                    "Total SA (Special Account) Balance",
                    "Total MA (MediSave Account) Balance",
                    "Cumulative Cash Savings",
                    "Net Monthly Salary",
                    "Net Annual Salary",
                    "Total Investment Premium Paid",
                    "Total Investment Value",
                    "Net Worth"
                ],
                "Value": [
                    projected_age_1 - current_age_1,
                    sum(df_1['Cumulative Total CPF']),
                    sum(df_1['Cumulative Total CPF']) * 0.2,
                    df_1['Cumulative OA'].iloc[-1],
                    df_1['Cumulative SA'].iloc[-1],
                    df_1['Cumulative MA'].iloc[-1],
                    df_1['Cumulative Cash Savings'].iloc[-1],
                    (salary_1 * 0.8) - monthly_expenses_1,
                    ((salary_1 * 0.8) - monthly_expenses_1) * 12,
                    df_1['Cumulative Investment Premium'].iloc[-1],
                    df_1['Investment Value'].iloc[-1],
                    df_1['Net Worth'].iloc[-1]
                ]
            }
            summary_df_1 = pd.DataFrame(summary_data_1)
            summary_df_1_display = summary_df_1.copy()
            summary_df_1_display['Value'] = summary_df_1_display.apply(
                lambda row: f"{int(row['Value'])}" if row['Metric'] == "Total Years Worked" else (
                    "${:,.2f}".format(row['Value']) if isinstance(row['Value'], (int, float)) else row['Value']
                ), axis=1
            )
            st.table(summary_df_1_display)

            # Format the summary table for display
            summary_df_1_display = summary_df_1.copy()
            summary_df_1_display['Value'] = summary_df_1_display.apply(
                lambda row: f"{int(row['Value'])}" if row['Metric'] == "Total Years Worked" else (
                    "${:,.2f}".format(row['Value']) if isinstance(row['Value'], (int, float)) else row['Value']
                ), axis=1
            )
            st.table(summary_df_1_display)

            # Plot Net Worth for Person 1
            # Plot Net Worth Over Time (With and Without Investment)
            fig_person_1 = go.Figure()
            fig_person_1.add_trace(go.Scatter(x=df_1['Age'], y=df_1['Net Worth'], mode='lines+markers',
                                              name=f"{name_1}'s Net Worth (With Investment)"))
            fig_person_1.add_trace(
                go.Scatter(x=df_1_no_investment['Age'], y=df_1_no_investment['Net Worth'], mode='lines+markers',
                           name=f"{name_1}'s Net Worth (Without Investment)"))
            fig_person_1.update_layout(title=f"{name_1}'s Net Worth Over Time", xaxis_title='Age',
                                       yaxis_title='Amount ($)', template='plotly_white')
            st.plotly_chart(fig_person_1)

        # Beautified Summary Table for Person 2
        st.subheader(f"{name_2}'s Full Analysis")
        with st.expander(f"{name_2}'s Full Analysis"):
            st.write(f"In-Depth Analysis for {name_2}:")
            st.write(df_2_formatted)

            summary_data_2 = {
                "Metric": [
                    "Total Years Worked",
                    "Total CPF Contribution",
                    "Total Employee CPF Contribution",
                    "Total OA (Ordinary Account) Balance",
                    "Total SA (Special Account) Balance",
                    "Total MA (MediSave Account) Balance",
                    "Cumulative Cash Savings",
                    "Net Monthly Salary",
                    "Net Annual Salary",
                    "Total Investment Premium Paid",
                    "Total Investment Value",
                    "Net Worth"
                ],
                "Value": [
                    projected_age_2 - current_age_2,
                    sum(df_2['Cumulative Total CPF']),
                    sum(df_2['Cumulative Total CPF']) * 0.2,
                    df_2['Cumulative OA'].iloc[-1],
                    df_2['Cumulative SA'].iloc[-1],
                    df_2['Cumulative MA'].iloc[-1],
                    df_2['Cumulative Cash Savings'].iloc[-1],
                    (salary_2 * 0.8) - monthly_expenses_2,
                    ((salary_2 * 0.8) - monthly_expenses_2) * 12,
                    df_2['Cumulative Investment Premium'].iloc[-1],
                    df_2['Investment Value'].iloc[-1],
                    df_2['Net Worth'].iloc[-1]
                ]
            }
            summary_df_2 = pd.DataFrame(summary_data_2)
            summary_df_2_display = summary_df_2.copy()
            summary_df_2_display['Value'] = summary_df_2_display.apply(
                lambda row: f"{int(row['Value'])}" if row['Metric'] == "Total Years Worked" else (
                    "${:,.2f}".format(row['Value']) if isinstance(row['Value'], (int, float)) else row['Value']
                ), axis=1
            )
            st.table(summary_df_2_display)

            # Format the summary table for display person 2
            summary_df_2_display = summary_df_2.copy()
            summary_df_2_display['Value'] = summary_df_2_display.apply(
                lambda row: f"{int(row['Value'])}" if row['Metric'] == "Total Years Worked" else (
                    "${:,.2f}".format(row['Value']) if isinstance(row['Value'], (int, float)) else row['Value']
                ), axis=1
            )
            st.table(summary_df_2_display)

            # Plot Net Worth for Person 2
            # Plot Net Worth Over Time (With and Without Investment)
            fig_person_2 = go.Figure()
            fig_person_2.add_trace(go.Scatter(x=df_2['Age'], y=df_2['Net Worth'], mode='lines+markers',
                                              name=f"{name_2}'s Net Worth (With Investment)"))
            fig_person_2.add_trace(
                go.Scatter(x=df_2_no_investment['Age'], y=df_2_no_investment['Net Worth'], mode='lines+markers',
                           name=f"{name_2}'s Net Worth (Without Investment)"))
            fig_person_2.update_layout(title=f"{name_2}'s Net Worth Over Time", xaxis_title='Age',
                                       yaxis_title='Amount ($)', template='plotly_white')
            st.plotly_chart(fig_person_2)

        # Combined Financial Analysis
        st.subheader("Combined Financial Analysis")
        with st.expander("Combined Financial Analysis"):
            st.write("\nCombined Financial Analysis:")
            st.write(df_combined_formatted)

            # Beautified Summary Table for Combined Analysis
            total_years_worked_combined = max(projected_age_1 - current_age_1, projected_age_2 - current_age_2)
            total_cpf_contribution_combined = sum(df_1['Cumulative Total CPF']) + sum(df_2['Cumulative Total CPF'])
            total_employee_contribution_combined = total_cpf_contribution_combined * 0.2
            total_oa_combined = df_1['Cumulative OA'].iloc[-1] + df_2['Cumulative OA'].iloc[-1]
            total_sa_combined = df_1['Cumulative SA'].iloc[-1] + df_2['Cumulative SA'].iloc[-1]
            total_ma_combined = df_1['Cumulative MA'].iloc[-1] + df_2['Cumulative MA'].iloc[-1]
            cumulative_cash_savings_combined = df_combined['Cumulative Cash Savings'].iloc[-1]
            net_monthly_salary_combined = ((salary_1 + salary_2) * 0.8) - (monthly_expenses_1 + monthly_expenses_2)
            net_annual_salary_combined = net_monthly_salary_combined * 12
            total_investment_premium_paid_combined = (
                    df_1['Cumulative Investment Premium'].iloc[-1] + df_2['Cumulative Investment Premium'].iloc[-1]
            )
            investment_value_combined = df_1['Investment Value'].iloc[-1] + df_2['Investment Value'].iloc[-1]
            net_worth_combined = df_combined['Net Worth'].iloc[-1]

            summary_data_combined = {
                "Metric": [
                    "Total Years Worked",
                    "Total CPF Contribution",
                    "Total Employee CPF Contribution",
                    "Total OA (Ordinary Account) Balance",
                    "Total SA (Special Account) Balance",
                    "Total MA (MediSave Account) Balance",
                    "Cumulative Cash Savings",
                    "Net Monthly Salary",
                    "Net Annual Salary",
                    "Total Investment Premium Paid",
                    "Total Investment Value",
                    "Net Worth"
                ],
                "Value": [
                    total_years_worked_combined,
                    total_cpf_contribution_combined,
                    total_employee_contribution_combined,
                    total_oa_combined,
                    total_sa_combined,
                    total_ma_combined,
                    cumulative_cash_savings_combined,
                    net_monthly_salary_combined,
                    net_annual_salary_combined,
                    total_investment_premium_paid_combined,
                    investment_value_combined,
                    net_worth_combined
                ]
            }

            summary_df_combined = pd.DataFrame(summary_data_combined)

            # Format the summary table for display for couple
            summary_df_combined_display = summary_df_combined.copy()
            summary_df_combined_display['Value'] = summary_df_combined_display.apply(
                lambda row: f"{int(row['Value'])}" if row['Metric'] == "Total Years Worked" else (
                    "${:,.2f}".format(row['Value']) if isinstance(row['Value'], (int, float)) else row['Value']
                ), axis=1
            )
            st.table(summary_df_combined_display)

            # Plot Combined Net Worth (With and Without Investment)
            fig_combined = go.Figure()
            fig_combined.add_trace(go.Scatter(x=df_combined['Year'], y=df_combined['Net Worth'], mode='lines+markers',
                                              name="Combined Net Worth (With Investment)"))
            fig_combined.add_trace(
                go.Scatter(x=df_combined_no_investment['Year'], y=df_combined_no_investment['Net Worth'],
                           mode='lines+markers', name="Combined Net Worth (Without Investment)"))
            fig_combined.update_layout(title="Combined Net Worth Over Time", xaxis_title='Year',
                                       yaxis_title='Amount ($)', template='plotly_white')
            st.plotly_chart(fig_combined)
