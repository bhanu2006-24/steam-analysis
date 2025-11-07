import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

st.set_page_config(page_title="Steam Games Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("clean_data_grouped_v3.csv")
    df2 = pd.read_csv("clean_data_exploded_v3.csv")
    return df, df2

df, df2 = load_data()

st.title("🎮 Steam Games Dashboard")
st.markdown("A **super‑powered** interactive dashboard for Steam dataset exploration")

# --- Sidebar Filters ---
st.sidebar.header("Filters")
year_range = st.sidebar.slider("Release Year Range",
                               int(df['release_year'].min()),
                               int(df['release_year'].max()),
                               (2010, 2020))
price_range = st.sidebar.slider("Price Range",
                                int(df['price'].min()),
                                int(df['price'].max()),
                                (0, 2000))
publisher_filter = st.sidebar.multiselect("Publishers", sorted(df['publisher'].dropna().unique()))
tag_filter = st.sidebar.multiselect("Tags", sorted(df2['tag'].dropna().unique()[:100]))
include_outliers = st.sidebar.checkbox("Include Outliers", value=False)

# Apply filters
filtered_df = df[(df['release_year'].between(*year_range)) &
                 (df['price'].between(*price_range))]

if publisher_filter:
    filtered_df = filtered_df[filtered_df['publisher'].isin(publisher_filter)]
if not include_outliers:
    filtered_df = filtered_df[filtered_df['review_outlier'] == "No"]

# --- KPI Cards ---
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Games", f"{len(filtered_df):,}")
col2.metric("Avg Price", f"{filtered_df['price'].mean():.2f}")
col3.metric("Avg Review %", f"{filtered_df['review_percent'].mean():.1f}")
col4.metric("Top Year", int(filtered_df['release_year'].mode()[0]))
col5.metric("Top Tag", df2['tag'].mode()[0] if not df2.empty else "NA")
col6.metric("Outliers", f"{(df['review_outlier']=='Yes').sum()}")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Overview", "Reviews", "Releases", "Publishers", "Tags", "Cross Analysis"]
)

with tab1:
    st.subheader("Price vs Review %")
    scatter_df = filtered_df.dropna(subset=["review_count","review_percent","price"])
    fig = px.scatter(scatter_df, x="price", y="review_percent",
                     size="review_count", color="release_year",
                     hover_data=["title","publisher"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Free vs Paid")
    fig2 = px.pie(filtered_df, names="is_free", title="Free vs Paid Share")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Price Distribution")
    fig3 = px.histogram(filtered_df, x="price", nbins=50)
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("Review Percent Distribution")
    fig = px.histogram(filtered_df, x="review_percent", nbins=20)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Review Count Distribution")
    fig = px.histogram(filtered_df, x="review_count", nbins=30)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Avg Review % by Publisher")
    pub = filtered_df.groupby("publisher")["review_percent"].mean().nlargest(15).reset_index()
    fig = px.bar(pub, x="review_percent", y="publisher", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Avg Review % by Tag")
    tag = df2.groupby("tag")["review_percent"].mean().nlargest(15).reset_index()
    fig = px.bar(tag, x="review_percent", y="tag", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Releases per Year")
    rel = filtered_df.groupby("release_year").size().reset_index(name="count")
    fig = px.bar(rel, x="release_year", y="count")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Releases Heatmap (Year × Month)")
    rel2 = filtered_df.groupby(["release_year","release_month"]).size().reset_index(name="count")
    fig = px.density_heatmap(rel2, x="release_month", y="release_year", z="count")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Top 20 Publishers by Game Count")
    top_pub = filtered_df['publisher'].value_counts().head(20).reset_index()
    top_pub.columns = ["publisher","count"]
    fig = px.bar(top_pub, x="count", y="publisher", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Avg Price by Publisher")
    pub_price = filtered_df.groupby("publisher")["price"].mean().nlargest(15).reset_index()
    fig = px.bar(pub_price, x="price", y="publisher", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("Top 20 Tags")
    top_tags = df2['tag'].value_counts().head(20).reset_index()
    top_tags.columns = ["tag","count"]
    fig = px.bar(top_tags, x="count", y="tag", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Avg Price by Tag")
    tag_price = df2.groupby("tag")["price"].mean().nlargest(15).reset_index()
    fig = px.bar(tag_price, x="price", y="tag", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.subheader("Correlation Heatmap")
    corr = filtered_df[["price","review_percent","review_count"]].corr()
    fig = ff.create_annotated_heatmap(z=corr.values,
                                      x=list(corr.columns),
                                      y=list(corr.index),
                                      annotation_text=corr.round(2).values,
                                      colorscale="Blues")
    st.plotly_chart(fig, use_container_width=True)
