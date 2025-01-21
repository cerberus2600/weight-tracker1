import sqlite3
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
!pip install matplotlib

# Database setup
def setup_database():
    conn = sqlite3.connect('weight_tracker.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    person TEXT PRIMARY KEY,
                    height REAL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS weights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person TEXT,
                    date TEXT,
                    current_weight REAL,
                    target_weight REAL,
                    FOREIGN KEY(person) REFERENCES users(person)
                )''')
    conn.commit()
    conn.close()

# Add or update user height
def add_or_update_user(person, height):
    conn = sqlite3.connect('weight_tracker.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (person, height) VALUES (?, ?)', (person, height))
    conn.commit()
    conn.close()

# Get user height
def get_user_height(person):
    conn = sqlite3.connect('weight_tracker.db')
    c = conn.cursor()
    c.execute('SELECT height FROM users WHERE person = ?', (person,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# Add weight entry
def add_weight(person, date, current_weight, target_weight):
    conn = sqlite3.connect('weight_tracker.db')
    c = conn.cursor()
    c.execute('INSERT INTO weights (person, date, current_weight, target_weight) VALUES (?, ?, ?, ?)',
              (person, date, current_weight, target_weight))
    conn.commit()
    conn.close()

# Fetch weight entries
def get_weights(person):
    conn = sqlite3.connect('weight_tracker.db')
    c = conn.cursor()
    c.execute('SELECT date, current_weight, target_weight FROM weights WHERE person = ? ORDER BY date', (person,))
    rows = c.fetchall()
    conn.close()
    return rows

# Calculate target weight based on BMI 23 kg/m^2
def calculate_target_weight(height):
    return 23 * (height / 100) ** 2

# Initialize database
setup_database()

# Streamlit UI
st.title('Weight Tracker for Two Persons')

# User selection
person = st.selectbox('Select Person', ['Person 1', 'Person 2'])

# Check if height is already recorded
user_height = get_user_height(person)
if user_height is None:
    st.subheader(f'First-time setup for {person}')
    height = st.number_input('Height (cm)', min_value=100.0, max_value=250.0, step=0.1, format='%.1f')
    if st.button('Save Height'):
        add_or_update_user(person, height)
        st.success(f'Height of {height:.1f} cm saved for {person}.')
else:
    st.subheader(f'Welcome back, {person}')
    st.write(f'Recorded height: {user_height:.1f} cm')

    # Input form for weight
    with st.form('weight_form'):
        date = st.date_input('Date')
        current_weight = st.number_input('Current Weight (kg)', min_value=0.0, step=0.1, format='%.1f')
        submit = st.form_submit_button('Add Record')

    if submit:
        target_weight = calculate_target_weight(user_height)
        add_weight(person, date, current_weight, target_weight)
        st.success(f'Record added for {person}. Target weight is {target_weight:.2f} kg.')

    # Display weight data
    weights = get_weights(person)
    if weights:
        st.subheader(f'Weight Records for {person}')
        df = pd.DataFrame(weights, columns=['Date', 'Current Weight', 'Target Weight'])
        st.write(df)

        # Plot weight data
        st.subheader('Weight Progress')
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        plt.figure(figsize=(10, 6))
        plt.plot(df['Date'], df['Current Weight'], marker='o', label='Current Weight')
        plt.axhline(y=df['Target Weight'].iloc[0], color='r', linestyle='--', label='Target Weight')
        plt.xlabel('Date')
        plt.ylabel('Weight (kg)')
        plt.title(f'Weight Progress for {person}')
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)
    else:
        st.write(f'No records found for {person}.')
