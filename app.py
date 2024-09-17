import streamlit as st
import pandas as pd
import numpy as np
import time
from collections import defaultdict
from mock import simulate_email_campaign

# Load subject lines from CSV
@st.cache_data
def load_subject_lines():
    df = pd.read_csv('subject-lines.csv')
    for factor in ['personalization', 'joining_fees', 'cashback', 'first_year_free', 'urgency']:
        df[factor] = df[factor].map({0: 'No', 1: 'Yes'})
    return df

# Constant factors
FACTORS = ['personalization', 'joining_fees', 'cashback', 'first_year_free', 'urgency']

# Multi-armed bandit algorithm (epsilon-greedy)
class MultiArmedBandit:
    def __init__(self, n_arms, epsilon=0.1):
        self.n_arms = n_arms
        self.epsilon = epsilon
        self.counts = np.zeros(n_arms)
        self.values = np.zeros(n_arms)

    def select_arm(self):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_arms)
        return np.argmax(self.values)

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] += 1
        n = self.counts[chosen_arm]
        value = self.values[chosen_arm]
        new_value = ((n - 1) / n) * value + (1 / n) * reward
        self.values[chosen_arm] = new_value

# Streamlit app
st.title('Advanced Email Subject Line Optimizer')

# Step 1: Email content and audience selection
email_content = st.text_area("Enter what the email is about:")
gender_options = st.multiselect("Select gender(s):", ["Male", "Female"], default=["Male", "Female"])
age_options = st.multiselect("Select age group(s):", ["18-30", "30-50", "50+"], default=["18-30", "30-50", "50+"])

if st.button("Submit"):
    st.session_state.step1_complete = True

# Step 2: Display factors
if 'step1_complete' in st.session_state and st.session_state.step1_complete:
    st.write("Factors to be considered:", ", ".join(FACTORS))
    if st.button("Continue"):
        st.session_state.step2_complete = True

# Step 3: Load subject line variations
if 'step2_complete' in st.session_state and st.session_state.step2_complete:
    subject_lines_df = load_subject_lines()
    
    with st.spinner("Loading subject line variations..."):
        time.sleep(2)  # Simulate loading time
    
    st.write("Subject Line Variations:")
    st.dataframe(subject_lines_df)
    
    if st.button("Simulate Campaign"):
        st.session_state.step3_complete = True

# Step 4: Campaign simulation
if 'step3_complete' in st.session_state and st.session_state.step3_complete:
    audiences = [f"{gender} {age}" for gender in gender_options for age in age_options]
    results = {audience: pd.DataFrame() for audience in audiences}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    tabs = st.tabs(audiences)
    table_placeholders = {audience: tab.empty() for audience, tab in zip(audiences, tabs)}
    
    num_iterations = 10000
    emails_per_iteration = 100
    update_frequency = 10  # Update display every 10 iterations
    
    bandits = {audience: MultiArmedBandit(len(subject_lines_df)) for audience in audiences}
    
    for i in range(num_iterations):
        for audience in audiences:
            bandit = bandits[audience]
            chosen_arm = bandit.select_arm()
            row = subject_lines_df.iloc[chosen_arm]
            subject = row['subject_line']
            factors = {factor: 1 if row[factor] == 'Yes' else 0 for factor in FACTORS}
            
            clicks, total = simulate_email_campaign(subject, factors, audience, num_emails=emails_per_iteration)
            ctr = clicks / total
            
            bandit.update(chosen_arm, ctr)
        
        if i % update_frequency == 0 or i == num_iterations - 1:
            for audience in audiences:
                bandit = bandits[audience]
                audience_results = []
                for j, row in subject_lines_df.iterrows():
                    audience_results.append({
                        "Subject Line": row['subject_line'],
                        "Emails Sent": int(bandit.counts[j] * emails_per_iteration),
                        "Clicks": int(bandit.counts[j] * bandit.values[j] * emails_per_iteration),
                        "CTR": f"{bandit.values[j] * 100:.2f}%"
                    })
                    audience_results[-1].update({factor: row[factor] for factor in FACTORS})
                
                df = pd.DataFrame(audience_results)
                df = df.sort_values("CTR", ascending=False)
                results[audience] = df
                
                with tabs[audiences.index(audience)]:
                    table_placeholders[audience].dataframe(df)
        
        # Update progress
        progress_bar.progress((i + 1) / num_iterations)
        status_text.text(f"Simulation iteration {i+1}/{num_iterations} completed")
        
        # Add a small delay to make the updates visible
        time.sleep(0.01)
    
    progress_bar.progress(1.0)  # Ensure the progress bar completes
    st.success("Campaign simulation completed!")

st.sidebar.title("About")
st.sidebar.info("This app simulates email campaign performance across different audience segments using a multi-armed bandit algorithm. It adapts and learns the best-performing subject lines over time.")