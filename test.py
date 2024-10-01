import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import requests
import io

# Set page configuration
st.set_page_config(
    page_title="GitHub Repository Dashboard",
    page_icon="🐙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Load the data
@st.cache_data(ttl=3600)
def load_data():
    url = "https://github.com/AmariahAK/Github-Repo-Dashboard/releases/download/v1.0.0/github_dataset.csv"
    response = requests.get(url)
    data = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
    data['stars_count'] = pd.to_numeric(data['stars_count'], errors='coerce').fillna(0).astype(int)
    return data

data = load_data()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Repository Analysis", "Language Trends", "About"])

# Sidebar filters
st.sidebar.header("Filters")
min_stars = st.sidebar.slider("Minimum Stars", 0, int(data['stars_count'].max()), 0)
languages = st.sidebar.multiselect("Select Languages", options=data['language'].unique())

# Advanced filters
st.sidebar.header("Advanced Filters")
min_size = st.sidebar.number_input("Minimum Repository Size", min_value=0, value=0)
max_size = st.sidebar.number_input("Maximum Repository Size", min_value=0, value=int(data['contributors'].max()))

# Apply filters
filtered_data = data[
    (data['stars_count'] >= min_stars) &
    (data['contributors'] >= min_size) & 
    (data['contributors'] <= max_size)
]
if languages:
    filtered_data = filtered_data[filtered_data['language'].isin(languages)]

# Display filtered data count
st.sidebar.write(f"Showing {len(filtered_data)} repositories")

if page == "Overview":
    st.markdown('<p class="big-font">Welcome to the GitHub Repository Dashboard</p>', unsafe_allow_html=True)
    st.write("A comprehensive dashboard showcasing GitHub repository data")

    # Display basic statistics
    st.header("Dataset Overview")
    st.write(f"Total number of repositories: {len(data)}")
    st.write(f"Number of unique languages: {data['language'].nunique()}")
    st.write(f"Average stars per repository: {data['stars_count'].mean():.2f}")

    # Top repositories by stars
    st.header("Top 10 Repositories by Stars")
    top_repos = data.nlargest(10, 'stars_count')[['repositories', 'stars_count']]
    st.table(top_repos)

    # Correlation Analysis
    st.header("Correlation Analysis")
    correlation = data[['stars_count', 'forks_count', 'issues_count', 'pull_requests']].corr()
    fig = px.imshow(correlation, text_auto=True, aspect="auto")
    st.plotly_chart(fig)

elif page == "Repository Analysis":
    st.title("Repository Analysis")

    # Scatter plot of stars vs. forks
    st.header("Stars vs. Forks")
    st.write("""
    This scatter plot shows the relationship between stars and forks for each repository.
    A logarithmic scale is used to better visualize the distribution, as star and fork counts
    can vary widely between popular and less popular repositories.
    """)
    fig = px.scatter(filtered_data, x='stars_count', y='forks_count', hover_name='repositories', 
                     log_x=True, log_y=True, title="Stars vs. Forks (Log Scale)")
    st.plotly_chart(fig)

    # Distribution of repository sizes
    st.header("Repository Size Distribution")
    fig, ax = plt.subplots()
    sns.histplot(filtered_data['contributors'], bins=50, kde=True, ax=ax)
    plt.title("Distribution of Repository Sizes")
    plt.xlabel("Size")
    st.pyplot(fig)

    # Repository comparison
    st.header("Repository Comparison")
    selected_repos = st.multiselect("Select repositories to compare", options=filtered_data['repositories'].unique())
    if selected_repos:
        comparison_data = filtered_data[filtered_data['repositories'].isin(selected_repos)]
        fig = px.bar(comparison_data, x='repositories', y=['stars_count', 'forks_count'], 
                     title="Comparison of Selected Repositories")
        st.plotly_chart(fig)

elif page == "Language Trends":
    st.title("Programming Language Trends")

    # Top programming languages
    st.header("Top Programming Languages")
    top_languages = filtered_data['language'].value_counts().head(10)
    fig = px.bar(top_languages, x=top_languages.index, y=top_languages.values, 
                 title="Top 10 Programming Languages")
    st.plotly_chart(fig)

    # Language vs. Average Stars
    st.header("Average Stars by Language")
    lang_stars = filtered_data.groupby('language')['stars_count'].mean().sort_values(ascending=False).head(10)
    fig = px.bar(lang_stars, x=lang_stars.index, y=lang_stars.values, 
                 title="Top 10 Languages by Average Stars")
    st.plotly_chart(fig)

    # Language Distribution (Treemap)
    st.header("Language Distribution (Treemap)")
    treemap_data = filtered_data[filtered_data['language'].notna() & (filtered_data['language'] != '')]
    fig = px.treemap(treemap_data, path=['language'], values='stars_count', 
                     title="Distribution of Languages by Star Count")
    st.plotly_chart(fig)

else:  # About page
    st.title("About This Dashboard")
    st.write("""
    This dashboard provides insights into GitHub repository data. It showcases various aspects of repositories including popularity, size, and programming language trends.

    Data source: GitHub Dataset (available on Kaggle)
    Created by: [Your Name]
    Last updated: [Date]

    The dashboard includes features such as:
    - Basic statistics and top repositories
    - Interactive visualizations of repository data
    - Language trend analysis
    - Advanced filtering options
    - Correlation analysis between different metrics

    For any questions or feedback, please contact [Your Contact Information].
    """)
