# %%writefile app.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title('GEO Backpay/Wage Calculator')
value = None
col1, col2, col3 = st.columns(3)
prev_gross1 = 0
prev_gross2 = 0
gross_fall = 0 
gross_spring = 0
percent_fall = 0
percent_spring = 0

st.session_state.show = False
# st.session_state.pay = None

def backpay(gross_fall,gross_spring,prev_gross,reappointed_fall,reappointed_spring,percent_fall,percent_spring,prev_percent,sept_percent =None,year =22,position_fall = None,position_spring = None):
    #if reappointment is for any assistantship
    #if reappointment is for any assistantship
    minimum_yearly_wage_22 = 21230
    monthly_22 = minimum_yearly_wage_22/9
    minimum_yearly_wage_23 = 22080
    monthly_23 = minimum_yearly_wage_23/9
    prev_gross_norm = prev_gross*prev_percent/50
    if prev_gross == 0:
        prev_gross_norm = 0.1
    gross_fall_norm = gross_fall*percent_fall/50
    gross_spring_norm = gross_spring*percent_spring/50
    reapp_fall = 1 + max(1.06-gross_fall_norm/prev_gross_norm,0.06)
    reapp_spring = 1 + max(1.06-gross_spring_norm/prev_gross_norm,0.06)
    fall_pay = 0
    if reappointed_fall == 'Yes':
        fall_pay = max(prev_gross_norm*reapp_fall,monthly_22)
    elif reappointed_fall == 'No':
        fall_pay = max(gross_fall_norm,monthly_22)
    if gross_fall == 0:
        fall_pay = 0
    spring_pay = 0
    if reappointed_spring == 'Yes':
        spring_pay = max(prev_gross_norm*reapp_spring,monthly_22)
    elif reappointed_spring == 'No':
        spring_pay = max(gross_spring_norm,monthly_22)
    if gross_spring == 0:
        spring_pay = 0
    fall_backpay = max(4.52*(fall_pay - gross_fall_norm),0)
    spring_backpay = max(4.48*(spring_pay - gross_spring_norm),0)
    if year == 22: #may paycheck
        backpay_calc = +  fall_backpay*percent_fall/50 + spring_backpay*percent_spring/50
        may_paycheck = gross_spring  + backpay_calc
        return round(may_paycheck,2), round(backpay_calc,2)
    if year == 23: #september
        september_paycheck = max(fall_pay,spring_pay,monthly_23)*sept_percent/50
        return round(september_paycheck,2)

def calculate_backpay():
    prev_gross = 0
    prev_percent = 0
    if prev_gross1 != 0:
        prev_gross = prev_gross1
        prev_percent = prev_percent1
    if prev_gross2 != 0:
        prev_gross = prev_gross2
        prev_percent = prev_percent2
    print(prev_gross, " :: " ,prev_percent)
    may_pay,backpay_calc = backpay(gross_fall,gross_spring,prev_gross,reappointed_fall,reappointed_spring,percent_fall,percent_spring,prev_percent)
    print(may_pay, " :: " ,backpay_calc)
    if may_pay == 0:
        st.warning('You entered no pay! Time to join UIUC', icon="⚠️")
        return None, None
    else:
        return may_pay, backpay_calc

def show_pay():
    st.session_state.may_pay, st.session_state.backpay  = calculate_backpay()
    
with col1:
    st.header("STEP 1:")
    st.subheader('Reappointment Information')
    st.write('A reappointment is holding any assistantship in the last three years before Fall 2022')
    agree = st.checkbox("I understand the definition of reappointment")
    if agree:
        reappointed_fall = st.radio('Were you reappointed for Fall 2022?',options=("No", "Yes"))
        if reappointed_fall == 'Yes': 
            st.write('Enter details for Reappointment')
            prev_gross1 = st.number_input("Please enter your Gross Wage for the last appointment you held prior to Fall 2022:", min_value=0, max_value=10000)
            prev_percent1 =  st.select_slider("Please enter your Total Appointment Percentage(%) for the last appointment you held prior to Fall 2022:",  options=(0,12.5,25,50,66.7))
        
        reappointed_spring = st.radio('Were you reappointed for Spring 2023?',options=("No", "Yes"))
        if reappointed_spring == 'Yes': 
            st.write('Enter details for Reappointment')
            prev_gross2 = st.number_input("Please enter your Gross Wage for the last appointment you held prior to Spring 2023:", min_value=0, max_value=10000, key = 'gross_pay')
            prev_percent2 =  st.select_slider("Please enter your Total Appointment Percentage(%) for the last appointment you held prior to Spring 2023:",  options=(0,12.5,25,50,66.7), key = 'gross_per')
        
        with col2:
            st.header("STEP 2:")
            st.subheader('Fall 2022 Details')
            fall = st.radio('Were you appointed during Fall 2022?',options=("No", "Yes"))
            if fall == 'Yes':
                gross_fall = st.number_input("Please input your monthly gross pay for Fall 2022", min_value=0, max_value=10000)
                fall_postions = st.multiselect("Please select all positions you held during Fall 2022", options =("TA","RA","GA","PGA"))
                percent_fall = st.select_slider("Total appointment percentage(%) in Fall 2022",  options=(0,12.5,25,50,66.7))
                # percent_RA_fall = st.select_slider("RA percentage(%) in Fall 2022",  options=(0,25,50,67.5))

            st.subheader('Spring 2023 Details')
            spring = st.radio('Were you appointed during Spring 2023?',options=("No", "Yes"))
            if spring == 'Yes':
                gross_spring = st.number_input("Please input your monthly gross pay for Spring 2023", min_value=0, max_value=10000)
                fall_postions = st.multiselect("Please select all positions you held during Spring 2023", options =("TA","RA","GA","PGA"))
                percent_spring= st.select_slider("Total appointment percentage(%) in Spring 2023",  options=(0,12.5,25,50,66.7))
            agree2 = st.checkbox("I entered all details accurately to the best of my knowledge. \
                                 I understand that GEO can only legally pursue cases affecting members of the bargaining unit, \
                                 which consists of all graduate students who hold a total Teaching Assistant (TA) and/or Graduate Assistant (GA) position\
                                 with a total TA+GA appointment between 0.25 and 0.67 full-time equivalent (FTE), except for TAs in their first semester \
                                 teaching in the following departments: Animal Biology; Biochemistry; Cell and Structural Biology; Chemistry; \
                                 Germanic Languages & Literature; Microbiology; Plant Biology; and Psychology.")
            if agree2:
                with col3:
                    st.header("STEP 3:")
                    st.button("Calculate My Pay", on_click = show_pay)
                    if "may_pay" in st.session_state:
                        st.metric("Estimated May 2023 Pay Check and Back Pay", st.session_state.may_pay , st.session_state.backpay)