import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px

# =====================================================
# CONFIGURATION
# =====================================================

FILE_NAME = "expenses_database.csv"

st.set_page_config(
    page_title="FK Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

/* Hide Streamlit UI */

#MainMenu,
footer,
header,
[data-testid="stDecoration"],
[data-testid="stElementToolbar"]{
    display:none;
}
[data-testid="stHeader"]{
    display:none;
}

/* Background */

.stApp{
    background:
    radial-gradient(circle at top left,#312E81 0%,transparent 30%),
    radial-gradient(circle at top right,#2563EB 0%,transparent 30%),
    linear-gradient(135deg,#0F172A,#111827);
    color:white;
}

/* Main Container */

.block-container{
    max-width:1100px;
    padding-top:2rem;
    padding-bottom:3rem;
}

/* Titles */

h1{
    font-size:42px;
    font-weight:800;
}

h2,h3{
    color:#E2E8F0;
}

/* Glass Cards */

.glass{

    background:rgba(255,255,255,.08);

    backdrop-filter:blur(18px);

    border:1px solid rgba(255,255,255,.12);

    border-radius:20px;

    padding:20px;

    margin-bottom:20px;

    box-shadow:0 10px 35px rgba(0,0,0,.30);

}

/* Inputs */

.stTextInput input,
.stNumberInput input,
textarea{

    background:#1E293B !important;

    color:white !important;

    border-radius:12px !important;

    border:1px solid #334155 !important;

}

div[data-baseweb="select"]{

    background:#1E293B !important;

    border-radius:12px;

}

/* Buttons */

.stButton>button,
.stFormSubmitButton>button{

    width:100%;

    height:48px;

    border:none;

    border-radius:14px;

    font-weight:bold;

    color:white;

    background:
    linear-gradient(
    90deg,
    #3B82F6,
    #6366F1);

    transition:.25s;

}

.stButton>button:hover,
.stFormSubmitButton>button:hover{

    transform:translateY(-2px);

    box-shadow:0 12px 25px rgba(59,130,246,.35);

}

/* Metric Cards */

[data-testid="metric-container"]{

    background:rgba(255,255,255,.08);

    border-radius:18px;

    padding:18px;

    border:1px solid rgba(255,255,255,.12);

}

[data-testid="stMetricValue"]{

    color:#38BDF8;

    font-size:34px;

    font-weight:800;

}

/* DataFrame */

[data-testid="stDataFrame"]{

    border-radius:18px;

    overflow:hidden;

}

/* Scrollbar */

::-webkit-scrollbar{

    width:8px;

}

::-webkit-scrollbar-thumb{

    background:#475569;

    border-radius:20px;

}

</style>
""", unsafe_allow_html=True)
# =====================================================
# DATA FUNCTIONS
# =====================================================

CATEGORIES = [
    "🍔 Food",
    "🚗 Transport",
    "🏠 Rent",
    "💡 Bills",
    "🛍️ Shopping",
    "🎮 Entertainment",
    "💊 Health",
    "📚 Education",
    "✈️ Travel",
    "💼 Salary",
    "✨ Other"
]


def load_data() -> pd.DataFrame:
    """
    Load expenses from CSV.
    Create a new database if one doesn't exist.
    """

    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)

        # Backwards compatibility with older versions
        if "ID" not in df.columns:
            df.insert(0, "ID", range(1, len(df) + 1))

        return df

    return pd.DataFrame(
        columns=[
            "ID",
            "Date",
            "Category",
            "Amount",
            "Description"
        ]
    )


def save_data(df: pd.DataFrame) -> None:
    """Save dataframe to CSV."""
    df.to_csv(FILE_NAME, index=False)


def next_id(df: pd.DataFrame) -> int:
    """Return the next available expense ID."""

    if df.empty:
        return 1

    return int(df["ID"].max()) + 1


def add_expense(
    df: pd.DataFrame,
    date,
    category,
    amount,
    description,
) -> pd.DataFrame:
    """Add a new expense."""

    expense = pd.DataFrame(
        [
            {
                "ID": next_id(df),
                "Date": date,
                "Category": category,
                "Amount": amount,
                "Description": description,
            }
        ]
    )

    df = pd.concat([df, expense], ignore_index=True)

    save_data(df)

    return df


def delete_expense(
    df: pd.DataFrame,
    expense_id: int,
) -> pd.DataFrame:
    """Delete an expense by ID."""

    df = (
        df[df["ID"] != expense_id]
        .reset_index(drop=True)
    )

    save_data(df)

    return df


# =====================================================
# LOAD DATABASE
# =====================================================

df = load_data()
st.title("💸 FK Expense Tracker")
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<h4 style='color:#94A3B8;'>Built by Flex power</h4>",
    unsafe_allow_html=True
)

with st.form("expense_form", clear_on_submit=True):

    st.subheader("➕ Add New Expense")

    col1, col2 = st.columns(2)

    with col1:

        expense_date = st.date_input(
            "Date",
            datetime.date.today()
        )

        category = st.selectbox(
            "Category",
            CATEGORIES
        )

    with col2:

        amount = st.number_input(
            "Amount ($)",
            min_value=0.0,
            step=1.0,
            format="%.2f",
        )

        description = st.text_input(
            "Description",
            placeholder="Coffee, Uber, Steam..."
        )

    submitted = st.form_submit_button(
        "➕ Add Expense"
    )

if submitted:

    if amount <= 0:

        st.error("Please enter an amount greater than zero.")

    else:

        df = add_expense(
            df,
            expense_date,
            category,
            amount,
            description,
        )

        st.success("Expense added successfully! 🎉")

        st.rerun()

# =====================================================
# DASHBOARD
# =====================================================

if not df.empty:

    st.divider()

    total_expenses = df["Amount"].sum()

    total_transactions = len(df)

    largest_expense = df["Amount"].max()

    top_category = (
        df.groupby("Category")["Amount"]
        .sum()
        .idxmax()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💸 Total Spent",
            f"${total_expenses:,.2f}"
        )

    with col2:
        st.metric(
            "🧾 Transactions",
            total_transactions
        )

    with col3:
        st.metric(
            "🔥 Largest",
            f"${largest_expense:,.2f}"
        )

with col4:
    st.metric(
        "⭐ Top Category",
        top_category
    )

# =====================================================
# ANALYTICS
# =====================================================

st.divider()

left, right = st.columns(2)

# -------------------------------
# Pie Chart
# -------------------------------

with left:

    st.subheader("🥧 Spending by Category")

    category_totals = (
        df.groupby("Category")["Amount"]
        .sum()
        .reset_index()
    )

    pie = px.pie(
        category_totals,
        values="Amount",
        names="Category",
        hole=0.55,
    )

    pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
    )

    st.plotly_chart(
        pie,
        use_container_width=True,
    )

# -------------------------------
# Bar Chart
# -------------------------------

with right:

    st.subheader("📊 Spending by Category")

    bar = px.bar(
        category_totals,
        x="Category",
        y="Amount",
        text_auto=".2s",
    )
    bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
    )
    st.plotly_chart(
        bar,
        use_container_width=True,
    )
st.write("")
st.subheader("📋 Transaction History")
display_df = (
        df
        .sort_values("Date", ascending=False)
        .reset_index(drop=True)
    )
st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
# =====================================================
# MONTHLY BUDGET
# =====================================================

st.divider()

st.subheader("🎯 Monthly Budget")

budget = st.number_input(
    "Budget ($)",
    min_value=1.0,
    value=1000.0,
)

spent = df["Amount"].sum()

progress = min(spent / budget, 1.0)

st.progress(progress)

left, right = st.columns(2)

left.metric(
    "Spent",
    f"${spent:,.2f}"
)

right.metric(
    "Remaining",
    f"${budget-spent:,.2f}"
)

if spent > budget:

    st.error("⚠️ Budget exceeded!")

elif spent > budget * 0.8:

    st.warning("⚠️ You're close to your budget.")

else:

    st.success("✅ Budget looks healthy.")


    # =====================================================
# INSIGHTS
# =====================================================

st.divider()

st.subheader("🧠 Spending Insights")

highest = df.loc[df["Amount"].idxmax()]

lowest = df.loc[df["Amount"].idxmin()]

c1, c2 = st.columns(2)

with c1:

    st.info(
        f"""
Largest Purchase

**{highest['Category']}**

${highest['Amount']:.2f}

{highest['Description']}
"""
    )

with c2:

    st.info(
        f"""
Smallest Purchase

**{lowest['Category']}**

${lowest['Amount']:.2f}

{lowest['Description']}
"""
    )


    # ==========================
    # DELETE SECTION
    # ==========================

    st.write("")
    st.subheader("🗑 Delete Expense")

    options = {}

    for _, row in df.iterrows():

        label = (
            f"#{int(row['ID'])}"
            f" | {row['Date']}"
            f" | {row['Category']}"
            f" | ${row['Amount']:.2f}"
            f" | {row['Description']}"
        )

        options[label] = int(row["ID"])

    selected = st.selectbox(
        "Choose an expense",
        list(options.keys())
    )

    col1, col2 = st.columns([1, 4])

    with col1:

        if st.button(
            "Delete",
            type="primary"
        ):

            df = delete_expense(
                df,
                options[selected]
            )

            st.success("Expense deleted successfully.")

            st.rerun()
        else:
         st.info("🚀FK")


