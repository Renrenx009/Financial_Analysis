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

# CPF contribution rates based on age
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

# CPF balance calculation
def calculate_cpf_balance(salary, bonus, thirteenth_month, monthly_expenses, start_age, current_age,
                          annual_investment_premium, annual_interest_rate, milestones, milestone_percentage=1.0,
                          existing_oa=0, existing_sa=0, existing_ma=0, existing_cash=0, investment_start_age=0):
    cpf_balance = {
        'Year': [], 'Age': [], 'Cumulative Cash Savings': [], 'Cumulative OA': [], 'Cumulative SA': [],
        'Cumulative MA': [], 'Cumulative Total CPF': [], 'Cumulative Investment Premium': [],
        'Investment Value': [], 'Net Worth': []
    }
    years_worked = current_age - start_age
    cumulative_cash_savings = existing_cash
    cumulative_oa = existing_oa
    cumulative_sa = existing_sa
    cumulative_ma = existing_ma
    cumulative_investment_premium = investment_value = 0
    net_worth = 0

    for year in range(years_worked):
        age = start_age + year
        oa_rate, sa_rate, ma_rate = get_cpf_allocation_rates(age)
        employer_rate, employee_rate, total_rate = get_cpf_rates(age)
        annual_income = salary * 12 + bonus + thirteenth_month
        cpf_contribution = annual_income * total_rate
        net_monthly_salary = (salary * (1 - employee_rate)) - monthly_expenses
        net_annual_salary = (net_monthly_salary * 12) + (bonus * (1 - employee_rate)) + (
            thirteenth_month * (1 - employee_rate))
        cumulative_cash_savings += net_annual_salary

        # Apply annual investment premium only after the investment start age
        if age >= investment_start_age:
            cumulative_cash_savings -= annual_investment_premium
            cumulative_investment_premium += annual_investment_premium
            investment_value = (investment_value + annual_investment_premium) * (1 + annual_interest_rate / 100)

        cumulative_oa += cpf_contribution * oa_rate
        cumulative_sa += cpf_contribution * sa_rate
        cumulative_ma += cpf_contribution * ma_rate
        cumulative_total_cpf = cumulative_oa + cumulative_sa + cumulative_ma
        net_worth = cumulative_cash_savings + cumulative_oa + cumulative_sa + investment_value

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
def align_financial_data(df1, df2, start_age_1, start_age_2):
    min_age = min(start_age_1, start_age_2)
    max_age = max(df1['Age'].iloc[-1], df2['Age'].iloc[-1])
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
        combined_data['Cumulative Investment Premium'].append(
            cumulative_investment_premium_1 + cumulative_investment_premium_2)
        combined_data['Investment Value'].append(investment_value_1 + investment_value_2)
        combined_data['Net Worth'].append(net_worth_1 + net_worth_2)

    return pd.DataFrame(combined_data)

# Streamlit App
st.header("Financial Analysis")
st.subheader("Key in your information here")

# Initialize session state for profile data
if "profile_data" not in st.session_state:
    st.session_state.profile_data = {
        "analysis_type": "Single",  # Default to "Single"
        "person_1": {
            "salary": 0.0,
            "bonus": 0.0,
            "thirteenth_month": 0.0,
            "monthly_expenses": 0.0,
            "start_age": 0,
            "current_age": 0,
            "annual_investment_premium": 0.0,
            "annual_interest_rate": 0.0,
            "milestones": {},
            "existing_oa": 0.0,
            "existing_sa": 0.0,
            "existing_ma": 0.0,
            "existing_cash": 0.0,
            "investment_start_age": 0
        }
    }

# Dynamically add "person_2" only if the analysis type is "Couple"
if st.session_state.profile_data["analysis_type"] == "Couple":
    if "person_2" not in st.session_state.profile_data:
        st.session_state.profile_data["person_2"] = {
            "salary": 0.0,
            "bonus": 0.0,
            "thirteenth_month": 0.0,
            "monthly_expenses": 0.0,
            "start_age": 0,
            "current_age": 0,
            "annual_investment_premium": 0.0,
            "annual_interest_rate": 0.0,
            "milestones": {},
            "existing_oa": 0.0,
            "existing_sa": 0.0,
            "existing_ma": 0.0,
            "existing_cash": 0.0,
            "investment_start_age": 0
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
        "salary": 0.0,
        "bonus": 0.0,
        "thirteenth_month": 0.0,
        "monthly_expenses": 0.0,
        "start_age": 0,
        "current_age": 0,
        "annual_investment_premium": 0.0,
        "annual_interest_rate": 0.0,
        "milestones": {},
        "existing_oa": 0.0,
        "existing_sa": 0.0,
        "existing_ma": 0.0,
        "existing_cash": 0.0,
        "investment_start_age": 0
    }

if analysis_type == 'Single':
    # Single person inputs
    salary = st.number_input("Enter your monthly gross income:", min_value=0.0, step=100.0,
                             value=st.session_state.profile_data["person_1"]["salary"])
    bonus = st.number_input("Enter your annual bonus:", min_value=0.0, step=100.0,
                            value=st.session_state.profile_data["person_1"]["bonus"])
    thirteenth_month = st.number_input("Enter your 13th month salary:", min_value=0.0, step=100.0,
                                       value=st.session_state.profile_data["person_1"]["thirteenth_month"])
    monthly_expenses = st.number_input("Enter your monthly expenses:", min_value=0.0, step=100.0,
                                       value=st.session_state.profile_data["person_1"]["monthly_expenses"])
    start_age = st.number_input("Enter your starting age:", min_value=0, step=1,
                                value=st.session_state.profile_data["person_1"]["start_age"])
    current_age = st.number_input("Enter your current age:", min_value=0, step=1,
                                  value=st.session_state.profile_data["person_1"]["current_age"])
    investment_start_age = st.number_input("Enter the start age for annual investment premium:", min_value=0, step=1,
                                           value=st.session_state.profile_data["person_1"]["investment_start_age"])
    annual_investment_premium = st.number_input("Enter your annual investment premium:", min_value=0.0, step=100.0,
                                                value=st.session_state.profile_data["person_1"][
                                                    "annual_investment_premium"])
    annual_interest_rate = st.number_input("Enter the annual interest rate (as a percentage):", min_value=0.0, step=0.1,
                                           value=st.session_state.profile_data["person_1"]["annual_interest_rate"])
    existing_oa = st.number_input("Enter your existing OA balance at starting age:", min_value=0.0, step=100.0,
                                  value=st.session_state.profile_data["person_1"]["existing_oa"])
    existing_sa = st.number_input("Enter your existing SA balance at starting age:", min_value=0.0, step=100.0,
                                  value=st.session_state.profile_data["person_1"]["existing_sa"])
    existing_ma = st.number_input("Enter your existing MA balance at starting age:", min_value=0.0, step=100.0,
                                  value=st.session_state.profile_data["person_1"]["existing_ma"])
    existing_cash = st.number_input("Enter your existing cash balance at starting age:", min_value=0.0, step=100.0,
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
        "salary": salary,
        "bonus": bonus,
        "thirteenth_month": thirteenth_month,
        "monthly_expenses": monthly_expenses,
        "start_age": start_age,
        "current_age": current_age,
        "investment_start_age": investment_start_age,
        "annual_investment_premium": annual_investment_premium,
        "annual_interest_rate": annual_interest_rate,
        "milestones": milestones,
        "existing_oa": existing_oa,
        "existing_sa": existing_sa,
        "existing_ma": existing_ma,
        "existing_cash": existing_cash
    }

    if st.button("Calculate"):
        cpf_balance = calculate_cpf_balance(salary, bonus, thirteenth_month, monthly_expenses, start_age,
                                            current_age, annual_investment_premium, annual_interest_rate, milestones,
                                            existing_oa=existing_oa, existing_sa=existing_sa,
                                            existing_ma=existing_ma, existing_cash=existing_cash,
                                            investment_start_age=investment_start_age)
        df = pd.DataFrame(cpf_balance)

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

        # Display Results in a collapsible section
        with st.expander("In-Depth Analysis"):
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
                    current_age - start_age,
                    "${:,.2f}".format(sum(df['Cumulative Total CPF'])),
                    "${:,.2f}".format(sum(df['Cumulative Total CPF']) * 0.2),
                    "${:,.2f}".format(df['Cumulative OA'].iloc[-1]),
                    "${:,.2f}".format(df['Cumulative SA'].iloc[-1]),
                    "${:,.2f}".format(df['Cumulative MA'].iloc[-1]),
                    "${:,.2f}".format(df['Cumulative Cash Savings'].iloc[-1]),
                    "${:,.2f}".format((salary * 0.8) - monthly_expenses),
                    "${:,.2f}".format(((salary * 0.8) - monthly_expenses) * 12),
                    "${:,.2f}".format(df['Cumulative Investment Premium'].iloc[-1]),
                    "${:,.2f}".format(df['Investment Value'].iloc[-1]),
                    "${:,.2f}".format(df['Net Worth'].iloc[-1])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            st.table(summary_df)

        # Plot Net Worth Over Time
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Age'], y=df['Net Worth'], mode='lines+markers', name='Net Worth'))
        fig.update_layout(title='Net Worth Over Time', xaxis_title='Age', yaxis_title='Amount ($)',
                          template='plotly_white')
        st.plotly_chart(fig)

elif analysis_type == 'Couple':
    # Person 1 inputs
    st.subheader("Person 1")
    salary_1 = st.number_input("Enter Person 1's monthly gross income:", min_value=0.0, step=100.0,
                               value=st.session_state.profile_data["person_1"]["salary"])
    bonus_1 = st.number_input("Enter Person 1's annual bonus:", min_value=0.0, step=100.0,
                              value=st.session_state.profile_data["person_1"]["bonus"])
    thirteenth_month_1 = st.number_input("Enter Person 1's 13th month salary:", min_value=0.0, step=100.0,
                                         value=st.session_state.profile_data["person_1"]["thirteenth_month"])
    monthly_expenses_1 = st.number_input("Enter Person 1's monthly expenses:", min_value=0.0, step=100.0,
                                         value=st.session_state.profile_data["person_1"]["monthly_expenses"])
    start_age_1 = st.number_input("Enter Person 1's starting age:", min_value=0, step=1,
                                  value=st.session_state.profile_data["person_1"]["start_age"])
    current_age_1 = st.number_input("Enter Person 1's current age:", min_value=0, step=1,
                                    value=st.session_state.profile_data["person_1"]["current_age"])
    investment_start_age_1 = st.number_input("Enter Person 1's start age for annual investment premium:", min_value=0,
                                             step=1,
                                             value=st.session_state.profile_data["person_1"]["investment_start_age"])
    annual_investment_premium_1 = st.number_input("Enter Person 1's annual investment premium:", min_value=0.0,
                                                  step=100.0,
                                                  value=st.session_state.profile_data["person_1"][
                                                      "annual_investment_premium"])
    annual_interest_rate_1 = st.number_input("Enter Person 1's annual interest rate (as a percentage):",
                                             min_value=0.0, step=0.1,
                                             value=st.session_state.profile_data["person_1"]["annual_interest_rate"])
    existing_oa_1 = st.number_input("Enter Person 1's existing OA balance at starting age:", min_value=0.0, step=100.0,
                                    value=st.session_state.profile_data["person_1"]["existing_oa"])
    existing_sa_1 = st.number_input("Enter Person 1's existing SA balance at starting age:", min_value=0.0, step=100.0,
                                    value=st.session_state.profile_data["person_1"]["existing_sa"])
    existing_ma_1 = st.number_input("Enter Person 1's existing MA balance at starting age:", min_value=0.0, step=100.0,
                                    value=st.session_state.profile_data["person_1"]["existing_ma"])
    existing_cash_1 = st.number_input("Enter Person 1's existing cash balance at starting age:", min_value=0.0, step=100.0,
                                     value=st.session_state.profile_data["person_1"]["existing_cash"])
    st.subheader("Financial Milestones for Person 1")
    num_milestones_1 = st.number_input("Enter the number of financial milestones for Person 1:", min_value=0, step=1)
    milestones_1 = {}
    for i in range(num_milestones_1):
        age = st.number_input(f"Enter the age for milestone {i + 1} (Person 1's age):", min_value=0, step=1,
                              key=f"age_1_{i}")
        amount = st.number_input(
            f"Enter the amount for milestone {i + 1} (negative for expenses, positive for gains):", step=100.0,
            key=f"amount_1_{i}")
        milestones_1[age] = amount

    # Person 2 inputs
    st.subheader("Person 2")
    salary_2 = st.number_input("Enter Person 2's monthly gross income:", min_value=0.0, step=100.0,
                               value=st.session_state.profile_data["person_2"]["salary"])
    bonus_2 = st.number_input("Enter Person 2's annual bonus:", min_value=0.0, step=100.0,
                              value=st.session_state.profile_data["person_2"]["bonus"])
    thirteenth_month_2 = st.number_input("Enter Person 2's 13th month salary:", min_value=0.0, step=100.0,
                                         value=st.session_state.profile_data["person_2"]["thirteenth_month"])
    monthly_expenses_2 = st.number_input("Enter Person 2's monthly expenses:", min_value=0.0, step=100.0,
                                         value=st.session_state.profile_data["person_2"]["monthly_expenses"])
    start_age_2 = st.number_input("Enter Person 2's starting age:", min_value=0, step=1,
                                  value=st.session_state.profile_data["person_2"]["start_age"])
    current_age_2 = st.number_input("Enter Person 2's current age:", min_value=0, step=1,
                                    value=st.session_state.profile_data["person_2"]["current_age"])
    investment_start_age_2 = st.number_input("Enter Person 2's start age for annual investment premium:", min_value=0,
                                             step=1,
                                             value=st.session_state.profile_data["person_2"]["investment_start_age"])
    annual_investment_premium_2 = st.number_input("Enter Person 2's annual investment premium:", min_value=0.0,
                                                  step=100.0,
                                                  value=st.session_state.profile_data["person_2"][
                                                      "annual_investment_premium"])
    annual_interest_rate_2 = st.number_input("Enter Person 2's annual interest rate (as a percentage):",
                                             min_value=0.0, step=0.1,
                                             value=st.session_state.profile_data["person_2"]["annual_interest_rate"])
    existing_oa_2 = st.number_input("Enter Person 2's existing OA balance at starting age:", min_value=0.0, step=100.0,
                                    value=st.session_state.profile_data["person_2"]["existing_oa"])
    existing_sa_2 = st.number_input("Enter Person 2's existing SA balance at starting age:", min_value=0.0, step=100.0,
                                    value=st.session_state.profile_data["person_2"]["existing_sa"])
    existing_ma_2 = st.number_input("Enter Person 2's existing MA balance at starting age:", min_value=0.0, step=100.0,
                                    value=st.session_state.profile_data["person_2"]["existing_ma"])
    existing_cash_2 = st.number_input("Enter Person 2's existing cash balance at starting age:", min_value=0.0, step=100.0,
                                      value=st.session_state.profile_data["person_2"]["existing_cash"])
    st.subheader("Financial Milestones for Person 2")
    num_milestones_2 = st.number_input("Enter the number of financial milestones for Person 2:", min_value=0, step=1)
    milestones_2 = {}
    for i in range(num_milestones_2):
        age = st.number_input(f"Enter the age for milestone {i + 1} (Person 2's age):", min_value=0, step=1,
                              key=f"age_2_{i}")
        amount = st.number_input(
            f"Enter the amount for milestone {i + 1} (negative for expenses, positive for gains):", step=100.0,
            key=f"amount_2_{i}")
        milestones_2[age] = amount

    # Update session state with current inputs
    st.session_state.profile_data["person_1"] = {
        "salary": salary_1,
        "bonus": bonus_1,
        "thirteenth_month": thirteenth_month_1,
        "monthly_expenses": monthly_expenses_1,
        "start_age": start_age_1,
        "current_age": current_age_1,
        "investment_start_age": investment_start_age_1,
        "annual_investment_premium": annual_investment_premium_1,
        "annual_interest_rate": annual_interest_rate_1,
        "milestones": milestones_1,
        "existing_oa": existing_oa_1,
        "existing_sa": existing_sa_1,
        "existing_ma": existing_ma_1,
        "existing_cash": existing_cash_1
    }
    st.session_state.profile_data["person_2"] = {
        "salary": salary_2,
        "bonus": bonus_2,
        "thirteenth_month": thirteenth_month_2,
        "monthly_expenses": monthly_expenses_2,
        "start_age": start_age_2,
        "current_age": current_age_2,
        "investment_start_age": investment_start_age_2,
        "annual_investment_premium": annual_investment_premium_2,
        "annual_interest_rate": annual_interest_rate_2,
        "milestones": milestones_2,
        "existing_oa": existing_oa_2,
        "existing_sa": existing_sa_2,
        "existing_ma": existing_ma_2,
        "existing_cash": existing_cash_2
    }

    if st.button("Calculate"):
        # Calculate CPF balance for Person 1
        cpf_balance_1 = calculate_cpf_balance(
            salary=salary_1,
            bonus=bonus_1,
            thirteenth_month=thirteenth_month_1,
            monthly_expenses=monthly_expenses_1,
            start_age=start_age_1,
            current_age=current_age_1,
            annual_investment_premium=annual_investment_premium_1,
            annual_interest_rate=annual_interest_rate_1,
            milestones=milestones_1,
            existing_oa=existing_oa_1,
            existing_sa=existing_sa_1,
            existing_ma=existing_ma_1,
            existing_cash=existing_cash_1,
            investment_start_age=investment_start_age_1
        )
        # Calculate CPF balance for Person 2
        cpf_balance_2 = calculate_cpf_balance(
            salary=salary_2,
            bonus=bonus_2,
            thirteenth_month=thirteenth_month_2,
            monthly_expenses=monthly_expenses_2,
            start_age=start_age_2,
            current_age=current_age_2,
            annual_investment_premium=annual_investment_premium_2,
            annual_interest_rate=annual_interest_rate_2,
            milestones=milestones_2,
            existing_oa=existing_oa_2,
            existing_sa=existing_sa_2,
            existing_ma=existing_ma_2,
            existing_cash=existing_cash_2,
            investment_start_age=investment_start_age_2
        )

        # Convert results to DataFrames
        df_1 = pd.DataFrame(cpf_balance_1)
        df_2 = pd.DataFrame(cpf_balance_2)

        # Align financial data for combined analysis
        df_combined = align_financial_data(df_1, df_2, start_age_1, start_age_2)

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

        # Display individual financial analyses in collapsible sections
        with st.expander("Person 1's In-Depth Financial Analysis"):
            st.write("\nIn-Depth Analysis for Person 1:")
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
                    current_age_1 - start_age_1,
                    "${:,.2f}".format(sum(df_1['Cumulative Total CPF'])),
                    "${:,.2f}".format(sum(df_1['Cumulative Total CPF']) * 0.2),
                    "${:,.2f}".format(df_1['Cumulative OA'].iloc[-1]),
                    "${:,.2f}".format(df_1['Cumulative SA'].iloc[-1]),
                    "${:,.2f}".format(df_1['Cumulative MA'].iloc[-1]),
                    "${:,.2f}".format(df_1['Cumulative Cash Savings'].iloc[-1]),
                    "${:,.2f}".format((salary_1 * 0.8) - monthly_expenses_1),
                    "${:,.2f}".format(((salary_1 * 0.8) - monthly_expenses_1) * 12),
                    "${:,.2f}".format(df_1['Cumulative Investment Premium'].iloc[-1]),
                    "${:,.2f}".format(df_1['Investment Value'].iloc[-1]),
                    "${:,.2f}".format(df_1['Net Worth'].iloc[-1])
                ]
            }
            summary_df_1 = pd.DataFrame(summary_data_1)
            st.table(summary_df_1)

        with st.expander("Person 2's In-Depth Financial Analysis"):
            st.write("\nIn-Depth Analysis for Person 2:")
            st.write(df_2_formatted)

            # Beautified Summary Table for Person 2
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
                    total_years_worked_2,
                    "${:,.2f}".format(total_cpf_contribution_2),
                    "${:,.2f}".format(total_employee_contribution_2),
                    "${:,.2f}".format(total_oa_2),
                    "${:,.2f}".format(total_sa_2),
                    "${:,.2f}".format(total_ma_2),
                    "${:,.2f}".format(cumulative_cash_savings_2),
                    "${:,.2f}".format(net_monthly_salary_2),
                    "${:,.2f}".format(net_annual_salary_2),
                    "${:,.2f}".format(total_investment_premium_paid_2),
                    "${:,.2f}".format(investment_value_2),
                    "${:,.2f}".format(net_worth_2)
                ]
            }
            summary_df_2 = pd.DataFrame(summary_data_2)

            with st.expander("Person 2's Summary"):
                st.table(summary_df_2)

            # Beautified Summary Table for Combined Analysis
            total_years_worked_combined = max(current_age_1 - start_age_1, current_age_2 - start_age_2)
            total_cpf_contribution_combined = total_cpf_contribution_1 + total_cpf_contribution_2
            total_employee_contribution_combined = total_cpf_contribution_combined * 0.2
            total_oa_combined = total_oa_1 + total_oa_2
            total_sa_combined = total_sa_1 + total_sa_2
            total_ma_combined = total_ma_1 + total_ma_2
            cumulative_cash_savings_combined = df_combined['Cumulative Cash Savings'].iloc[-1]
            net_monthly_salary_combined = ((salary_1 + salary_2) * 0.8) - (monthly_expenses_1 + monthly_expenses_2)
            net_annual_salary_combined = net_monthly_salary_combined * 12
            total_investment_premium_paid_combined = (
                    total_investment_premium_paid_1 + total_investment_premium_paid_2
            )
            investment_value_combined = investment_value_1 + investment_value_2
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
                    "${:,.2f}".format(total_cpf_contribution_combined),
                    "${:,.2f}".format(total_employee_contribution_combined),
                    "${:,.2f}".format(total_oa_combined),
                    "${:,.2f}".format(total_sa_combined),
                    "${:,.2f}".format(total_ma_combined),
                    "${:,.2f}".format(cumulative_cash_savings_combined),
                    "${:,.2f}".format(net_monthly_salary_combined),
                    "${:,.2f}".format(net_annual_salary_combined),
                    "${:,.2f}".format(total_investment_premium_paid_combined),
                    "${:,.2f}".format(investment_value_combined),
                    "${:,.2f}".format(net_worth_combined)
                ]
            }
            summary_df_combined = pd.DataFrame(summary_data_combined)

            with st.expander("Combined Summary"):
                st.table(summary_df_combined)
