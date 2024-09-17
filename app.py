import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from optimizer import EmailSubjectOptimizer
from mock import generate_mock_open_rate, simulate_email_opens

st.title('Email Subject Line Optimizer')

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write(data)

    if st.button('Run Optimization'):
        factors = ['personalization', 'joining_fees', 'cashback', 'first_year_free', 'urgency']
        optimizer = EmailSubjectOptimizer(factors)

        # Set up the plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        plt.subplots_adjust(hspace=0.4)
        
        # First subplot for open rates
        line1, = ax1.plot([], [], lw=2)
        ax1.set_xlim(0, 100)
        ax1.set_ylim(0, 1)
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('Open Rate')
        ax1.set_title('Open Rate Over Time')
        ax1.grid(True)

        # Second subplot for factor importance
        bar_plot = ax2.bar(factors, [0]*len(factors))
        ax2.set_ylim(0, 1)
        ax2.set_ylabel('Factor Importance')
        ax2.set_title('Factor Importance Over Time')

        results = []
        subject_lines = []
        x = []
        factor_importance = {factor: [] for factor in factors}

        # Use Streamlit's empty containers for dynamic updating
        plot_placeholder = st.empty()
        metrics_placeholder = st.empty()

        for i in range(100):  # Run 100 iterations
            row = data.sample(1).iloc[0]
            state = {factor: row[factor] for factor in factors}
            subject_line = row['subject_line']

            new_state = optimizer.choose_action(state)
            opens, total = simulate_email_opens(subject_line, new_state)
            open_rate = opens / total

            optimizer.update_q_values(state, new_state, open_rate, new_state)
            results.append(open_rate)
            subject_lines.append(subject_line)
            x.append(i)

            # Update factor importance
            for factor in factors:
                importance = sum(q_values[factor] for q_values in optimizer.q_values.values()) / len(optimizer.q_values)
                factor_importance[factor].append(importance)

            # Update the plot
            line1.set_data(x, results)
            for rect, height in zip(bar_plot, [factor_importance[factor][-1] for factor in factors]):
                rect.set_height(height)

            # Update the plot in Streamlit
            plot_placeholder.pyplot(fig)

            # Update metrics
            with metrics_placeholder.container():
                st.write(f"Iteration: {i+1}")
                st.write(f"Current Open Rate: {open_rate:.2%}")
                st.write(f"Best Open Rate: {max(results):.2%}")
                st.write(f"Current Subject Line: {subject_line}")

            # Pause to create animation effect
            time.sleep(0.01)

        st.write("Optimization Complete!")
        st.write("Final Q-values:", optimizer.q_values)

        best_combination = max(optimizer.q_values, key=lambda x: sum(optimizer.q_values[x].values()))
        st.write("Best combination:", best_combination)

        # Find the best performing subject line from our actual data
        best_index = results.index(max(results))
        best_subject = subject_lines[best_index]
        best_open_rate = max(results)

        st.write("Best performing subject line:", best_subject)
        st.write(f"Best open rate achieved: {best_open_rate:.2%}")

        # Display factor importance
        st.write("Factor Importance:")
        for factor in factors:
            st.write(f"{factor}: {factor_importance[factor][-1]:.2f}")

st.sidebar.title("About")
st.sidebar.info("This app demonstrates RL-based optimization of email subject lines. Upload a CSV with subject lines and their factors to see how the model learns and improves open rates over time.")