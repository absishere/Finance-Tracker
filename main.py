import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import numpy as np

def apply_custom_css():
    """Apply custom CSS for better visual design"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }

    .balance-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    .balance-amount {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }

    .expense-form {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
    }

    .success-message {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }

    .warning-message {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }

    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables with better structure"""
    if 'transactions' not in st.session_state:
        st.session_state.transactions = []
    if 'initial_balance' not in st.session_state:
        st.session_state.initial_balance = 0
    if 'is_initialized' not in st.session_state:
        st.session_state.is_initialized = False

def calculate_current_balance():
    """Calculate current balance from transactions"""
    if not st.session_state.is_initialized:
        return 0

    total_expenses = sum(transaction['amount'] for transaction in st.session_state.transactions)
    return st.session_state.initial_balance - total_expenses

def add_transaction(amount, description="Expense"):
    """Add a new transaction with timestamp"""
    transaction = {
        'amount': amount,
        'description': description,
        'timestamp': datetime.now(),
        'date': date.today()
    }
    st.session_state.transactions.append(transaction)

def create_balance_visualization():
    """Create an enhanced balance visualization"""
    if not st.session_state.transactions:
        return None

    # Prepare data for visualization
    balance_history = [st.session_state.initial_balance]
    dates = [st.session_state.transactions[0]['date'] if st.session_state.transactions else date.today()]

    running_balance = st.session_state.initial_balance
    for transaction in st.session_state.transactions:
        running_balance -= transaction['amount']
        balance_history.append(running_balance)
        dates.append(transaction['date'])

    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Balance': balance_history,
        'Transaction': list(range(len(balance_history)))
    })

    # Create Plotly chart
    fig = go.Figure()

    # Add balance line
    fig.add_trace(go.Scatter(
        x=df['Transaction'],
        y=df['Balance'],
        mode='lines+markers',
        name='Balance',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#667eea'),
        hovertemplate='Transaction: %{x}<br>Balance: ₹%{y:.2f}<extra></extra>'
    ))

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="red",
                  annotation_text="Zero Balance", annotation_position="bottom right")

    # Update layout
    fig.update_layout(
        title=dict(
            text="Balance Over Time",
            x=0.5,
            font=dict(size=20, color='#333')
        ),
        xaxis_title="Transaction Number",
        yaxis_title="Balance (₹)",
        template="plotly_white",
        height=400,
        showlegend=False,
        hovermode='x unified'
    )

    return fig

def create_expense_breakdown():
    """Create expense breakdown visualization"""
    if not st.session_state.transactions:
        return None

    # Group expenses by description
    expense_data = {}
    for transaction in st.session_state.transactions:
        desc = transaction['description']
        if desc in expense_data:
            expense_data[desc] += transaction['amount']
        else:
            expense_data[desc] = transaction['amount']

    if len(expense_data) > 1:
        # Create pie chart
        fig = px.pie(
            values=list(expense_data.values()),
            names=list(expense_data.keys()),
            title="Expense Breakdown",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=400)
        return fig

    return None

def display_transaction_history():
    """Display transaction history in a formatted table"""
    if not st.session_state.transactions:
        st.info("📝 No transactions yet. Add your first expense above!")
        return

    # Create DataFrame
    df = pd.DataFrame([
        {
            'Date': t['date'].strftime('%Y-%m-%d'),
            'Description': t['description'],
            'Amount': f"₹{t['amount']:.2f}",
            'Time': t['timestamp'].strftime('%H:%M:%S')
        }
        for t in reversed(st.session_state.transactions)  # Show most recent first
    ])

    st.subheader("📊 Transaction History")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date"),
            "Description": st.column_config.TextColumn("Description"),
            "Amount": st.column_config.TextColumn("Amount"),
            "Time": st.column_config.TimeColumn("Time")
        }
    )

def main():
    """Main application function"""
    # Set page config
    st.set_page_config(
        page_title="Cash Flow Tracker",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS
    apply_custom_css()

    # Initialize session state
    initialize_session_state()

    # Header
    st.markdown('<h1 class="main-header">💰 Enhanced Cash Flow Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Track your expenses and monitor your financial health with beautiful visualizations</p>', unsafe_allow_html=True)

    # Sidebar for settings and summary
    with st.sidebar:
        st.header("📋 Summary")

        if st.session_state.is_initialized:
            current_balance = calculate_current_balance()
            total_expenses = sum(t['amount'] for t in st.session_state.transactions)

            st.metric("💵 Initial Balance", f"₹{st.session_state.initial_balance:.2f}")
            st.metric("💸 Total Expenses", f"₹{total_expenses:.2f}")
            st.metric("💰 Current Balance", f"₹{current_balance:.2f}",
                     delta=f"{current_balance - st.session_state.initial_balance:.2f}")

            # Progress bar
            if st.session_state.initial_balance > 0:
                progress = max(0, current_balance / st.session_state.initial_balance)
                st.progress(progress, text=f"Remaining: {progress*100:.1f}%")

        st.markdown("---")

        # Reset button
        if st.button("🔄 Reset All Data", type="secondary"):
            st.session_state.transactions = []
            st.session_state.initial_balance = 0
            st.session_state.is_initialized = False
            st.success("✅ Data reset successfully!")
            st.rerun()

    # Main content
    if not st.session_state.is_initialized:
        # Initial balance setup
        st.markdown("### 🚀 Let's Get Started!")
        st.markdown("Enter your initial balance to begin tracking your expenses.")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            initial_balance = st.number_input(
                "💵 Enter your initial balance:",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                help="This is the amount of money you start with"
            )

            if st.button("✅ Set Initial Balance", type="primary"):
                if initial_balance > 0:
                    st.session_state.initial_balance = initial_balance
                    st.session_state.is_initialized = True
                    st.success(f"🎉 Initial balance of ₹{initial_balance:.2f} set successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please enter a positive amount")

    else:
        # Main dashboard
        current_balance = calculate_current_balance()

        # Balance display
        balance_color = "green" if current_balance >= 0 else "red"
        balance_emoji = "💰" if current_balance >= 0 else "⚠️"

        st.markdown(f"""
        <div class="balance-card">
            <h2>{balance_emoji} Current Balance</h2>
            <div class="balance-amount" style="color: {'#fff' if current_balance >= 0 else '#ffcccb'}">
                ₹{current_balance:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Expense input form
        st.markdown("### 💸 Add New Expense")

        col1, col2 = st.columns([2, 1])

        with col1:
            expense_amount = st.number_input(
                "Amount (₹):",
                min_value=0.01,
                step=1.0,
                format="%.2f",
                key="expense_amount"
            )

        with col2:
            expense_description = st.text_input(
                "Description:",
                placeholder="e.g., Groceries, Gas, Coffee",
                key="expense_description"
            )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("➕ Add Expense", type="primary"):
                if expense_amount > 0:
                    description = expense_description if expense_description else "General Expense"
                    add_transaction(expense_amount, description)

                    new_balance = calculate_current_balance()

                    if new_balance < 0:
                        st.error("⚠️ Warning: You've exceeded your initial balance!")
                    elif new_balance == 0:
                        st.warning("⚠️ You've spent all your money!")
                    else:
                        st.success(f"✅ Expense of ₹{expense_amount:.2f} added successfully!")

                    st.rerun()
                else:
                    st.error("❌ Please enter a valid expense amount")

        # Visualizations
        if st.session_state.transactions:
            st.markdown("---")

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                balance_chart = create_balance_visualization()
                if balance_chart:
                    st.plotly_chart(balance_chart, use_container_width=True)

            with col2:
                expense_chart = create_expense_breakdown()
                if expense_chart:
                    st.plotly_chart(expense_chart, use_container_width=True)
                else:
                    st.info("💡 Add expenses with different descriptions to see breakdown chart")

            # Transaction history
            st.markdown("---")
            display_transaction_history()

if __name__ == "__main__":
    main()