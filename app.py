# %%writefile app.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title('GEO Backpay/Wage Calculator')
agree1 = st.checkbox("I understand that GEO can only legally pursue cases affecting members of the bargaining unit, \
                            which consists of all graduate students who hold a Teaching Assistant (TA) and/or Graduate Assistant (GA) position\
                            with a total TA+GA appointment between 0.25 and 0.67 full-time equivalent (FTE), except for TAs in their first semester \
                            teaching in the following departments: Animal Biology; Biochemistry; Cell and Structural Biology; Chemistry; \
                            Germanic Languages & Literature; Microbiology; Plant Biology; and Psychology.")

value = None
col1, col2, col3 = st.columns(3)
prev_gross1 = 0
prev_gross2 = 0
gross_fall = 0 
gross_spring = 0
percent_fall = -1
percent_spring = -1
reappointed_sept = 'No'
# Glob variables
NEW_MINIMUM_2022_2023 = 21230. / 9.
NEW_MINIMUM_2023_2024 = 22080. / 9.

st.session_state.show = False
# st.session_state.pay = None
def calculate_pay(
        prev_wage,
        fall_wage,
        spring_wage,
        prev_app_pct,
        fall_app_pct,
        spring_app_pct,
        reappointed_fall,
        reappointed_spring,
        reappointed_sep23,
        sept23_pct = 50.0,
        new_minimum_2022_2023=NEW_MINIMUM_2022_2023,
        new_minimum_2023_2024=NEW_MINIMUM_2023_2024
):
    reappointed_fall = (reappointed_fall == 'Yes')
    reappointed_spring = (reappointed_spring == 'Yes')
    reappointed_sep23 = (reappointed_sep23 == 'Yes')
    
    prev_app_pct = float(prev_app_pct)
    fall_app_pct = float(fall_app_pct)
    spring_app_pct = float(spring_app_pct)

    reappointed_sep23 = (not reappointed_fall) & (not reappointed_spring) & reappointed_sep23

    # Normalization
    prev_wage = float(prev_wage) / (prev_app_pct / 50.)
    fall_wage = float(fall_wage) / (fall_app_pct / 50.)
    spring_wage = float(spring_wage) / (spring_app_pct / 50.)

    # Wages adjusted according to new contract

    wage_with_reappointment_raise = prev_wage * 1.06

    fall_wage_adj = max(fall_wage, wage_with_reappointment_raise, new_minimum_2022_2023) if reappointed_fall else max(
        fall_wage, new_minimum_2022_2023) if fall_wage > 0 else 0
    spring_wage_adj = max(spring_wage, wage_with_reappointment_raise, new_minimum_2022_2023) if reappointed_spring else max(
        spring_wage, new_minimum_2022_2023) if spring_wage > 0 else 0 

    # Backpay

    fall_backpay = 4.52 * (fall_wage_adj - fall_wage) * (fall_app_pct / 50.) * (fall_wage > 0)
    spring_backpay = 4.48 * (spring_wage_adj - spring_wage) * (spring_app_pct / 50.) * (spring_wage > 0)
    backpay_total = fall_backpay + spring_backpay
    may_paycheck = spring_wage * (spring_app_pct / 50.) + backpay_total
    print("Fall wage adj", fall_wage_adj)
    print(reappointed_sep23)
    print(spring_wage_adj)
    print((spring_wage_adj if spring_wage_adj > 0 else fall_wage_adj) * (1. + 0.06 * reappointed_sep23))
    september_wage = max((spring_wage_adj if spring_wage_adj > 0 else fall_wage_adj) * (1. + 0.06 * reappointed_sep23), new_minimum_2023_2024) * float(sept23_pct) / 50.
    print(september_wage)
    return may_paycheck, backpay_total, september_wage

def calculate_backpay(year, sept_percent = 50.0):
    prev_gross = 0
    prev_percent = -1
    if reappointed_fall == 'Yes':
        if prev_gross1 != 0: # If they had an appointment BEFORE fall 2022 AND an appointment IN fall 2022
            prev_gross = prev_gross1
            prev_percent = prev_percent1
        else:
            st.error('This is an error')
            st.warning("You didn't enter pay for reappointment before Fall 2022", icon="⚠️")
    # elif reappointed_spring == 'Yes':
    #     if prev_gross2 != 0:
    #         prev_gross = prev_gross2
    #         prev_percent = prev_percent2
    #     else:
    #         st.error('This is an error')
    #         st.warning("You didn't enter pay for reappointment before Spring 2023", icon="⚠️")

    print(prev_gross, " :: " ,prev_percent)
    print(prev_gross,gross_fall,gross_spring,prev_percent,percent_fall,percent_spring,reappointed_fall,reappointed_spring,reappointed_sept, sept_percent)
    # may_pay,backpay_calc = backpay(gross_fall,gross_spring,prev_gross,reappointed_fall,reappointed_spring,percent_fall,percent_spring,prev_percent, year=year, sept_percent=sept_percent)
    if gross_fall == 0 and gross_spring == 0:
        st.warning('You entered no pay for Fall 2022 or Spring 2023. Time to join UIUC', icon="⚠️")
        return None, None, None
    
    may_pay,backpay_calc, sep_pay = calculate_pay(
        prev_wage  =prev_gross,
        fall_wage = gross_fall,
        spring_wage = gross_spring,
        prev_app_pct = prev_percent,
        fall_app_pct = percent_fall,
        spring_app_pct = percent_spring,
        reappointed_fall = reappointed_fall,
        reappointed_spring = reappointed_spring,
        reappointed_sep23 = reappointed_sept,   
        sept23_pct = sept_percent,
        new_minimum_2022_2023=NEW_MINIMUM_2022_2023,
        new_minimum_2023_2024=NEW_MINIMUM_2023_2024
    )
    
    print(may_pay, " :: " ,backpay_calc, " ::" , sep_pay)
    # if gross_spring == 0:
    #     st.error('This is an error')
    #     st.warning('You entered no pay for Spring 2023', icon="⚠️")
    #     return 0, 0, 0  
    
    if may_pay == 0:
        st.warning('You are already making above minimum and have no reappointment for this year', icon="⚠️")
        return 0, 0 , round(sep_pay,2)
    else:
        return round(may_pay,2), round(backpay_calc,2) , round(sep_pay,2)

def show_pay_may():
    st.session_state.may_pay, st.session_state.backpay, st.session_state.sep_pay = calculate_backpay(year = 22)
 

def show_pay_sep():
    st.session_state.may_pay, st.session_state.backpay, st.session_state.sep_pay = calculate_backpay(year = 23, sept_percent= sept_percent)
    
with col1:
    st.header("STEP 1:")
    st.write(r'\* Your Gross Monthly Wage is the current "Taxable Gross" entry on your earnings statement, found here: https://www.hr.uillinois.edu/pay/earnstmt')
    if agree1:
        st.subheader('Fall 2022 Details')
        fall = st.radio('Were you appointed during Fall 2022?',options=("No", "Yes"))
        if fall == 'Yes':
            gross_fall = st.number_input("Please input your Gross Monthly Wage* for Fall 2022", min_value=0.0, max_value=10000.00,step=0.000001)
            fall_postions = st.multiselect("Please select all positions you held during Fall 2022", options =("TA", "GA", "RA","PGA", "Fellow/Other"))
            percent_fall = st.slider("Total appointment percentage(%) in Fall 2022", min_value = 10.0 , max_value = 66.7, value = 50.0 , step = 0.5)
            # percent_RA_fall = st.slider("RA percentage(%) in Fall 2022",  options=(0,25,50,67.5))

        st.subheader('Spring 2023 Details')
        spring = st.radio('Were you appointed during Spring 2023?',options=("No", "Yes"))
        if spring == 'Yes':
            gross_spring = st.number_input("Please input your Gross Monthly Wage* for Spring 2023", min_value=0.0, max_value=10000.00,step=0.000001)
            fall_postions = st.multiselect("Please select all positions you held during Spring 2023", options =("TA","GA","RA","PGA", "Fellow/Other"))
            percent_spring= st.slider("Total appointment percentage(%) in Spring 2023", min_value = 10.0 , max_value = 66.7, value = 50.0 , step = 0.5)
        st.write(r'\* Your Gross Monthly Wage is the current "Taxable Gross" entry on your earnings statement, found here: https://www.hr.uillinois.edu/pay/earnstmt')
        with col2:
            st.header("STEP 2:")
            st.subheader('Reappointment Information')
            st.write('A reappointment is holding any assistantship in the last three years before Fall 2022')
            agree = st.checkbox("I understand the definition of reappointment")
            if agree:
                if fall == 'Yes':
                    reappointed_fall = st.radio('Were you reappointed for Fall 2022?',options=("No", "Yes"))
                    if reappointed_fall == 'Yes' and fall == 'Yes':
                        st.write('Enter details for Reappointment')
                        prev_gross1 = st.number_input("Please enter your Gross Monthly Wage* for the last appointment you held prior to Fall 2022:", min_value=0.0, max_value=10000.00,step=0.000001)
                        prev_percent1 =  st.slider("Please enter your Total Appointment Percentage (%) for the last appointment you held prior to Fall 2022:", min_value = 10.0 , max_value = 66.7, value = 50.0 , step = 0.5)
                        reappointed_spring = spring
                    elif reappointed_fall == 'No' and spring == 'Yes':
                        if fall == 'No':
                            reappointed_spring = st.radio('Were you reappointed for Spring 2023?',options=("No", "Yes"))
                            if reappointed_spring == 'Yes':
                                st.write('Enter details for Reappointment')
                                prev_gross2 = st.number_input("Please enter your Gross Monthly Wage* for the last appointment you held prior to Spring 2023:", min_value=0.0, max_value=10000.00,step=0.000001, key = 'gross_pay')
                                prev_percent2 =  st.slider("Please enter your Total Appointment Percentage (%) for the last appointment you held prior to Spring 2023:", min_value = 10.0 , max_value = 66.7, value = 50.0 , step = 0.5, key = 'gross_per')
                        else:
                            reappointed_spring = 'Yes'
                            prev_gross1 = prev_gross2 = gross_fall
                            prev_percent1 = prev_percent2 = percent_fall
                    else:
                        reappointed_spring = fall
                elif spring == 'Yes':
                    reappointed_fall = 'No'
                    reappointed_spring = st.radio('Were you reappointed for Spring 2023?', options=("No", "Yes"))
                    if reappointed_spring == 'Yes':
                        st.write('Enter details for Reappointment')
                        prev_gross2 = st.number_input(
                            "Please enter your Gross Monthly Wage* for the last appointment you held prior to Spring 2023:",
                            min_value=0.0, max_value=10000.00, step=0.000001, key='gross_pay')
                        prev_percent2 = st.slider(
                            "Please enter your Total Appointment Percentage (%) for the last appointment you held prior to Spring 2023:",
                           min_value = 10.0 , max_value = 66.7, value = 50.0 , step = 0.5, key='gross_per')
                else:
                    reappointed_spring = reappointed_fall = 'No'
                agree2 = st.checkbox("I entered all details accurately to the best of my knowledge.")
                if agree2:
                    with col3:
                        st.header("STEP 3:")
                        st.button("Calculate My May Pay", on_click = show_pay_may)
                        if "may_pay" in st.session_state:
                            st.metric("Estimated May 2023 Pay Check and Back Pay", st.session_state.may_pay , st.session_state.backpay)
                        reappointed_sept = st.radio('Will you have an appointment for Sept 2023?',options=("No", "Yes"))
                        if reappointed_sept == "Yes":
                            sept_percent = st.slider("Please enter your Total Appointment Percentage(%) for Fall 2023:", min_value = 10.0 , max_value = 66.7, value = 50.0 , step = 0.5)
                            st.button("Calculate My September Pay", on_click = show_pay_sep)
                            if "sep_pay" in st.session_state:
                                st.metric("Estimated September 2023 Pay Check: ", st.session_state.sep_pay)
                            st.write("Disclaimer: Your actual monthly pay for Fall 2023 could be higher if your department chooses to increase your monthly pay beyond the minimum as stipulated by the contract.")    
                                        
                                    