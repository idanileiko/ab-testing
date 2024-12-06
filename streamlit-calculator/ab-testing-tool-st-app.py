# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 08:18:50 2023

@author: irina.danileiko
"""

# Import required libraries
import streamlit as st
import math as m
import statsmodels.stats.api as sms
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
import matplotlib.pyplot as plt
import pandas as pd
 

# Title and centered image
st.title("Experimentation Tools")

col1, col2, col3 = st.columns(3)
with col1:
    st.write("")
with col2:
    st.image("https://github.com/idanileiko/ab-testing-tools/blob/main/streamlit-calculator/ab-testing.png?raw=true")
with col3:
    st.write("")


# Create the sidebar
st.sidebar.title("Example:")
st.sidebar.markdown("Only **10%** of our users currently use a specific product feature. If we showcase this feature on the post-login landing page, it may interest more users. \
                    We want to run an experiment where we show some users this new showcase to see if it's effective.")
st.sidebar.markdown("We'd consider this a success if that feature usage rate of the users who see the showcase goes up to **15%**. \
                    We're also investing a lot into the UX design so we want to be very sure of the results (**95%** confidence level).")
st.sidebar.write("---")
#st.sidebar.markdown("Number of groups = 2")
st.sidebar.markdown("Current conversion rate = 0.10")
st.sidebar.markdown("Desired conversion rate = 0.15")
st.sidebar.markdown("Significance level = 0.05 (1 - confidence level)")
st.sidebar.markdown("Power = 0.8 (traditional value)")
st.sidebar.write("---")
st.sidebar.markdown("We will need at least **1362** users, half of whom will see the old UX design and half of whom will see the new one.")


# Create multiple tabs, or "pages", for the various tools
tab_titles = [
    "Sample Sizing Calculator",
    "A/B Test Calculator",
    "A/B Testing File Upload"
    ]

tabs = st.tabs(tab_titles)

# First tab for sample sizing
with tabs[0]:
    st.markdown(":star: This calculator is for assessing the minimum sample size needed for running an experiment such as an A/B test!")
    st.write("---")

    # User Inputs
    
    #number_groups = st.number_input("Number of groups", value = 2, min_value = 2, max_value = 100)
    #st.markdown("*The number of control + test groups that are in the experiment. In a standard A/B test, there are 2 (control + 1 test) \
    #            but it's possible to have an A/B/C/D/etc. test where there are control + many test groups, which would require a larger sample size.*")
    #st.write("---")
    # can't make number of groups work yet in the a/b test result since it can't auto-populate number inputs
    
    current_rate = st.number_input(label = "Current conversion rate", value = 0.100, min_value = 0.00, max_value = 1.00, format="%.3f")
    st.markdown("*The preexisting conversion rate of the population for the metric of interest. It's expected the control group will exhibit this rate in the experiment.*")
    st.write("---")
    
    desired_rate = st.number_input(label = "Desired conversion rate", value = 0.150, min_value = 0.00, max_value = 1.00, format="%.3f")
    st.markdown("*The desired conversion rate that would show that the experimental change was successful.*")
    st.write("---")

    n_groups = st.number_input(label = "Number of Groups", value = 2, min_value = 2, max_value = 8, step = 1)
    st.markdown("*The number of design variations you want to test, including the control group.*")
    st.write("---")
    
    significance_level = st.number_input(label = "Significance level", value = .05, min_value = 0.0, max_value = 0.5)
    st.markdown("*The maximum risk of making a false positive conclusion that is reasonable to accept. Smaller values are more conservative \
                and a reasonable range is 0.01 - 0.15, depending on how important it is to have a conservative result.*")
    st.write("---")
    
    power = st.number_input(label = "Power", value = .8, min_value = 0.5, max_value = 0.99)
    st.markdown("*The probability of finding an effect when it exists. Traditionally, power is set at 0.8, \
                meaning if there are true effects to be found in 100 different studies, 80 out of 100 statistical tests will detect them.\
                A reasonable range is 0.8 - 0.9.*")
    st.write("---")

    
    # Run calculation for figuring out the needed sample size
    sample_size = 0
    
    def sample_size_calc():

        # calculate effect size based on our base rates and desired increase
        effect_size = sms.proportion_effectsize(current_rate, desired_rate)
            
        # calculated required sample size in each group
        sample_size = sms.NormalIndPower().solve_power(
            effect_size, 
            power = power, 
            alpha = significance_level, 
            ratio = 1 # assumes equal number of users are placed in the control and test group
            )

        # round up to nearest whole number
        sample_size = m.ceil(sample_size)
        total_users = sample_size * n_groups
            
        st.success(f" The required sample size is at least {sample_size} users per group for a total of at least {total_users} users.")
        
    if st.button("Calculate Sample Size"):
        sample_size_calc()
        
    st.write("---")
    st.markdown("*Assumptions & Notes:*")
    st.markdown("- *Assumes the experiment is testing a binary variable (e.g. did or didn't log in, did or didn't purchase, etc.) rather than a continuous one (e.g. amount spent).*")
    st.markdown("- *Assumes the experiment involves two groups of users: one control and one test group.*")
    
with tabs[1]:
    st.markdown(":star: This calculator is for calculating the results of an A/B test!")
    st.write("---")
    
    # User Inputs
    st.markdown("Control group")
    successes_control = st.number_input(label = "Number of successes in control group", value = 70, min_value = 0)
    users_control = st.number_input(label = "Number of users in control group", value = 681, min_value = 0)
    st.write('---')
    
    st.markdown("Test group")
    successes_test = st.number_input(label = "Number of successes in test group", value = 130, min_value = 0)
    users_test = st.number_input(label = "Number of users in test group", value = 681, min_value = 0)
    st.write('---')
    
    method = st.radio("Select a testing method:",
                      ("Frequentist", "Bayesian (coming soon!)"))
        
    def ab_test_calc():
        
        if method == 'Frequentist':
            
            # Calculate A/B test result using a proportion test
            successes = [successes_control, successes_test]
            n_users = [users_control, users_test]
            
            z_stat, pval = proportions_ztest(successes, nobs = n_users)
            (lower_con, lower_treat), (upper_con, upper_treat) = proportion_confint(successes, nobs = n_users, alpha = significance_level)
            
            # Determine if result was significant
            if pval < significance_level:
                result = 'YES!'
            else:
                result = 'NO'
            
            # Print experiment results
            delta = round(((successes_test / users_test) - (successes_control / users_control)) * 100, 2)
            st.success(f"Is there a significant difference between the control and test group? {result}")
            if result == 'YES!':
                if delta >= 0 :
                    st.success(f"The experimental group had a lift of {delta}% over the control group!")
                elif delta < 0 :
                    delta_abs = abs(delta)
                    st.success(f"The experimental group was {delta_abs}% lower than the control group.")
            
            # Create bar chart of experiment results
            data = {'Control': (successes_control / users_control) * 100,
                    'Test': (successes_test / users_test) * 100}
            groups = list(data.keys())
            values = list(data.values())
            fig, ax = plt.subplots()
            ax.bar(groups, values, color = ['midnightblue', 'darkorange'])
            plt.ylabel('Conversion Rate (%)')
            st.pyplot(fig)
            
        elif method == "Bayesian (coming soon!)":
            st.write("Work in progress!")
        
        
    if st.button("Calculate Result"):
        ab_test_calc()
        
with tabs[2]:
    st.markdown(":star: This page is for calculating the results of an A/B test from an uploaded file!")
    st.markdown("The file should be a csv and the expected format is below:")
    
    example = {'Group':['Control','Test'], 'Users':[750,800], 'Successes':[70,130]}
    df_example = pd.DataFrame(example)
    st.dataframe(df_example)
    
    st.write("---")
    
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        #read csv
        df = pd.read_csv(uploaded_file)
    else:
        st.warning("You need to upload a csv file")
