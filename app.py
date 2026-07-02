import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Page Configuration
# -------------------------------

st.set_page_config(
    page_title="EduPro Analytics Dashboard",
    page_icon="📚",
    layout="wide"
)

st.title("📚 EduPro Analytics Dashboard")
st.markdown("### Instructor Performance and Course Quality Evaluation")

# -------------------------------
# Load Data
# -------------------------------

@st.cache_data
def load_data():

    teachers = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Teachers")
    courses = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Courses")
    transactions = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Transactions")
    users = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Users")

    teacher_transaction = transactions.merge(
        teachers,
        on="TeacherID",
        how="left"
    )

    final_data = teacher_transaction.merge(
        courses,
        on="CourseID",
        how="left"
    )

    return final_data

final_data = load_data()

# -------------------------------
# Sidebar
# -------------------------------

st.sidebar.title("📚 EduPro Dashboard")

st.sidebar.markdown("---")

st.sidebar.header("Filters")

expertise = st.sidebar.multiselect(
    "Instructor Expertise",
    sorted(final_data["Expertise"].unique()),
    default=sorted(final_data["Expertise"].unique())
)

category = st.sidebar.multiselect(
    "Course Category",
    sorted(final_data["CourseCategory"].unique()),
    default=sorted(final_data["CourseCategory"].unique())
)

level = st.sidebar.multiselect(
    "Course Level",
    sorted(final_data["CourseLevel"].unique()),
    default=sorted(final_data["CourseLevel"].unique())
)

rating = st.sidebar.slider(
    "Teacher Rating",
    float(final_data["TeacherRating"].min()),
    float(final_data["TeacherRating"].max()),
    (
        float(final_data["TeacherRating"].min()),
        float(final_data["TeacherRating"].max())
    )
)

teacher_search = st.sidebar.text_input(
    "Search Instructor"
)

# -------------------------------
# Apply Filters
# -------------------------------

filtered = final_data[
    (final_data["Expertise"].isin(expertise)) &
    (final_data["CourseCategory"].isin(category)) &
    (final_data["CourseLevel"].isin(level)) &
    (final_data["TeacherRating"] >= rating[0]) &
    (final_data["TeacherRating"] <= rating[1])
]

if teacher_search:
    filtered = filtered[
        filtered["TeacherName"].str.contains(
            teacher_search,
            case=False,
            na=False
        )
    ]

st.success(f"Showing {len(filtered)} records")

# ------------------------------------------------
# KPI Dashboard
# ------------------------------------------------

st.markdown("---")
st.header("📊 Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

avg_teacher = round(filtered["TeacherRating"].mean(), 2) if not filtered.empty else 0
avg_course = round(filtered["CourseRating"].mean(), 2) if not filtered.empty else 0
total_instructors = filtered["TeacherID"].nunique()
total_enrollments = filtered["TransactionID"].count()

col1.metric("⭐ Avg Teacher Rating", avg_teacher)
col2.metric("📚 Avg Course Rating", avg_course)
col3.metric("👨‍🏫 Total Instructors", total_instructors)
col4.metric("🎓 Total Enrollments", total_enrollments)

st.markdown("---")
st.header("🏆 Instructor Performance Leaderboard")

leaderboard = filtered.groupby("TeacherName").agg(
    TeacherRating=("TeacherRating", "mean"),
    CourseRating=("CourseRating", "mean"),
    Enrollments=("TransactionID", "count"),
    Experience=("YearsOfExperience", "mean"),
    Expertise=("Expertise", "first")
).reset_index()

leaderboard = leaderboard.sort_values(
    by="TeacherRating",
    ascending=False
)

st.dataframe(
    leaderboard,
    use_container_width=True
)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:

    st.subheader("🥇 Top 10 Instructors")

    st.dataframe(
        leaderboard.head(10),
        use_container_width=True
    )

with col2:

    st.subheader("⚠️ Bottom 10 Instructors")

    st.dataframe(
        leaderboard.sort_values("TeacherRating").head(10),
        use_container_width=True
    )

st.markdown("---")

# ------------------------------------------------
# Best Performing Instructor
# ------------------------------------------------

st.markdown("---")

if leaderboard.empty:
    st.warning("No instructor data available for the selected filters.")
else:
    best = leaderboard.iloc[0]

    st.success(f"""
### 🌟 Best Performing Instructor

**Name:** {best['TeacherName']}

**Teacher Rating:** {best['TeacherRating']:.2f}

**Course Rating:** {best['CourseRating']:.2f}

**Experience:** {best['Experience']:.0f} Years

**Expertise:** {best['Expertise']}
""")
# ------------------------------------------------
# Experience vs Teacher Rating
# ------------------------------------------------

st.markdown("---")
st.header("📈 Experience vs Teacher Rating")

fig = px.scatter(
    filtered,
    x="YearsOfExperience",
    y="TeacherRating",
    color="CourseCategory",
    hover_name="TeacherName",
    size="CourseRating",
    title="Experience vs Teacher Rating"
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Teacher Rating Distribution
# ------------------------------------------------

st.markdown("---")
st.header("⭐ Teacher Rating Distribution")

fig = px.histogram(
    filtered,
    x="TeacherRating",
    nbins=20,
    color_discrete_sequence=["royalblue"]
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Course Category Distribution
# ------------------------------------------------

st.markdown("---")
st.header("🍩 Course Category Distribution")

category_count = filtered.groupby(
    "CourseCategory"
).size().reset_index(name="Count")

fig = px.pie(
    category_count,
    names="CourseCategory",
    values="Count",
    hole=0.5
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Course Category Performance
# ------------------------------------------------

st.markdown("---")
st.header("📚 Average Course Rating by Category")

category_rating = filtered.groupby(
    "CourseCategory"
)["CourseRating"].mean().reset_index()

category_rating = category_rating.sort_values(
    by="CourseRating",
    ascending=False
)

fig = px.bar(
    category_rating,
    x="CourseCategory",
    y="CourseRating",
    color="CourseRating",
    text_auto=".2f"
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Course Level Performance
# ------------------------------------------------

st.markdown("---")
st.header("🎯 Average Course Rating by Level")

level_rating = filtered.groupby(
    "CourseLevel"
)["CourseRating"].mean().reset_index()

fig = px.bar(
    level_rating,
    x="CourseLevel",
    y="CourseRating",
    color="CourseRating",
    text_auto=".2f"
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Expertise-wise Performance
# ------------------------------------------------

st.markdown("---")
st.header("💼 Expertise-wise Performance")

expertise = filtered.groupby("Expertise").agg(
    TeacherRating=("TeacherRating","mean"),
    CourseRating=("CourseRating","mean")
).reset_index()

fig = px.bar(
    expertise,
    x="Expertise",
    y=["TeacherRating","CourseRating"],
    barmode="group"
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Monthly Enrollment Trend
# ------------------------------------------------

filtered["TransactionDate"] = pd.to_datetime(
    filtered["TransactionDate"]
)

monthly = filtered.groupby(
    filtered["TransactionDate"].dt.to_period("M")
).size().reset_index(name="Enrollments")

monthly["TransactionDate"] = monthly[
    "TransactionDate"
].astype(str)

st.markdown("---")
st.header("📅 Monthly Enrollment Trend")

fig = px.line(
    monthly,
    x="TransactionDate",
    y="Enrollments",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Course Quality Heatmap
# ------------------------------------------------

st.markdown("---")
st.header("🔥 Course Quality Heatmap")

heatmap_data = filtered.pivot_table(
    values="CourseRating",
    index="CourseCategory",
    columns="CourseLevel",
    aggfunc="mean"
)

if heatmap_data.empty:
    st.warning("No data available to display the heatmap.")
else:
    fig, ax = plt.subplots(figsize=(10,6))

    sns.heatmap(
        heatmap_data,
        annot=True,
        cmap="YlGnBu",
        linewidths=0.5,
        fmt=".2f",
        ax=ax
    )

    plt.xlabel("Course Level")
    plt.ylabel("Course Category")

    st.pyplot(fig)

# ------------------------------------------------
# Correlation Heatmap
# ------------------------------------------------

st.markdown("---")
st.header("📊 Correlation Matrix")

corr = filtered[
[
    "TeacherRating",
    "CourseRating",
    "YearsOfExperience",
    "Age",
    "CourseDuration",
    "CoursePrice"
]
].corr()

fig, ax = plt.subplots(figsize=(8,6))

sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=.5,
    ax=ax
)

st.pyplot(fig)

st.markdown("---")
st.header("📈 Rating Summary")

summary = filtered[
[
    "TeacherRating",
    "CourseRating"
]
].describe()

st.dataframe(summary)

st.markdown("---")
st.header("📥 Download Filtered Data")

csv = filtered.to_csv(index=False)

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="EduPro_Filtered_Data.csv",
    mime="text/csv"
)

st.markdown("---")
st.header("📋 Executive Summary")

avg_teacher = round(filtered["TeacherRating"].mean(),2)
avg_course = round(filtered["CourseRating"].mean(),2)

best_teacher = leaderboard.iloc[0]["TeacherName"]
best_rating = round(leaderboard.iloc[0]["TeacherRating"],2)

st.info(f"""

### Key Insights

⭐ Average Teacher Rating : **{avg_teacher}**

📚 Average Course Rating : **{avg_course}**

👨‍🏫 Total Instructors : **{filtered['TeacherID'].nunique()}**

🎓 Total Enrollments : **{filtered['TransactionID'].count()}**

🏆 Best Instructor : **{best_teacher}**

⭐ Best Teacher Rating : **{best_rating}**

""")

st.markdown("---")
st.header("💡 Business Recommendations")

st.success("""

• Continue investing in high-performing instructors.

• Improve course content for lower-rated categories.

• Provide instructor training for low-performing expertise areas.

• Encourage experienced instructors to mentor newer instructors.

• Monitor course ratings regularly to improve learner satisfaction.

• Use instructor ratings and course ratings together for performance evaluation.

""")

st.markdown("---")

st.markdown(
"""
<center>

### 📚 EduPro Analytics Dashboard

Developed by **Pricilla Chinnappan**

Data Analytics Internship Project

© 2026

</center>
""",
unsafe_allow_html=True
)