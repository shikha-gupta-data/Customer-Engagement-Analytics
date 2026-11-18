import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Customer Retention Analytics", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("European_Bank.csv")
    df["AgeGroup"] = pd.cut(df["Age"], [17,25,35,45,55,65,100],
                            labels=["18-25","26-35","36-45","46-55","56-65","66+"])
    return df

df = load_data()

st.title("📊 Customer Engagement & Product Utilization Analytics")
st.subheader("Retention Strategy Dashboard")
st.caption("European Bank Customer Dataset")

st.sidebar.header("🔎 Filters")
countries = st.sidebar.multiselect("Geography", sorted(df["Geography"].unique()),
                                   default=sorted(df["Geography"].unique()))
activity = st.sidebar.multiselect("Customer Activity", ["Active","Inactive"],
                                   default=["Active","Inactive"])
ages = st.sidebar.multiselect("Age Group", [str(x) for x in df["AgeGroup"].dropna().unique()],
                              default=[str(x) for x in df["AgeGroup"].dropna().unique()])

filtered = df[df["Geography"].isin(countries) &
              df["AgeGroup"].astype(str).isin(ages)].copy()

if activity:
    vals = [1 if x == "Active" else 0 for x in activity]
    filtered = filtered[filtered["IsActiveMember"].isin(vals)]
else:
    filtered = filtered.iloc[0:0]

total = len(filtered)
exited = int(filtered["Exited"].sum()) if total else 0
exit_rate = exited / total if total else 0

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total Customers", f"{total:,}")
c2.metric("Exited Customers", f"{exited:,}")
c3.metric("Exit Rate", f"{exit_rate:.2%}")
c4.metric("Retention Rate", f"{1-exit_rate:.2%}")

st.divider()

a,b = st.columns(2)

with a:
    st.subheader("🌍 Exit Rate by Geography")
    x = filtered.groupby("Geography", as_index=False)["Exited"].mean()
    x["Exit Rate"] = x["Exited"]*100
    fig = px.bar(x, x="Geography", y="Exit Rate", text="Exit Rate")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with b:
    st.subheader("👥 Active vs Inactive")
    x = filtered.copy()
    x["Activity"] = x["IsActiveMember"].map({1:"Active",0:"Inactive"})
    x = x.groupby("Activity", as_index=False)["Exited"].mean()
    x["Exit Rate"] = x["Exited"]*100
    fig = px.bar(x, x="Activity", y="Exit Rate", text="Exit Rate")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

a,b = st.columns(2)

with a:
    st.subheader("📦 Exit Rate by Number of Products")
    x = filtered.groupby("NumOfProducts", as_index=False)["Exited"].mean()
    x["Exit Rate"] = x["Exited"]*100
    fig = px.bar(x, x="NumOfProducts", y="Exit Rate", text="Exit Rate")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with b:
    st.subheader("🎂 Exit Rate by Age Group")
    x = filtered.groupby("AgeGroup", observed=True, as_index=False)["Exited"].mean()
    x["Exit Rate"] = x["Exited"]*100
    fig = px.bar(x, x="AgeGroup", y="Exit Rate", text="Exit Rate")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("🚨 Retention Risk Segments")

filtered["Risk Segment"] = "Lower Priority / Retain"
filtered.loc[(filtered["IsActiveMember"]==0) & (filtered["NumOfProducts"]==1),
             "Risk Segment"] = "High Risk - Inactive + 1 Product"
filtered.loc[(filtered["Geography"]=="Germany") & (filtered["IsActiveMember"]==0),
             "Risk Segment"] = "High Risk - Germany + Inactive"
filtered.loc[(filtered["Age"].between(46,65)) & (filtered["IsActiveMember"]==0),
             "Risk Segment"] = "High Risk - Older + Inactive"

risk = filtered["Risk Segment"].value_counts().reset_index()
risk.columns = ["Risk Segment","Customers"]
st.dataframe(risk, use_container_width=True, hide_index=True)

st.subheader("💡 Retention Recommendations")
st.markdown("""
- **Inactive + 1 product:** personalized engagement, reminders and product education.
- **Germany + inactive:** dedicated retention campaign and proactive outreach.
- **Age 46–65 + inactive:** service reviews, loyalty benefits and personalized products.
- **3–4 products:** investigate product fit, fees and service issues.
- **Active customers:** loyalty and relevant cross-sell campaigns.
""")

st.caption("Note: These are observational patterns and do not prove causation.")
