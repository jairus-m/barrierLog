import streamlit as st
import pandas as pd
from barrierReferralData import BarrierReferralData
import plotly.express as px
from uszipcode import SearchEngine
search = SearchEngine()

BARRIERS = BarrierReferralData()

def zco(x: str) -> str:
    """
    Get the city name from the zip code.

    Args:
        x (int): Zip code.
    Returns:
        str: City name or the zip code if city name is not found.
    """
    try:
        city = search.by_zipcode(x).major_city
        return city 
    except AttributeError:
        return x

def load_csv_data(df: pd.DataFrame):
    """
    Generate a download button to download data as a CSV file.

    Args:
        df (pandas.DataFrame): DataFrame to be converted to CSV.
    Returns:
        None
    """
    @st.cache_data
    def convert_df(df):
       return df.to_csv(index=False).encode('utf-8')
    csv = convert_df(df)
    st.sidebar.download_button(
        "Download Barrier Data",
        csv,
        "barriers_oc.csv",
        "text/csv",
        key='download-csv'
    )

def display_top_barriers(i: int, barriers: BarrierReferralData,col: str = 'barrier_list'):
    """
    Display the top barriers based on the specified column.
    
    Args:
        i (int): Number of top barriers to display.
        barriers: BarrierReferralData class object.
        col (str): Column name to consider for displaying top barriers.
    Returns:
        None
    """
    top_values = barriers.topValues(col, i)
    st.write(f'##### Top {i} Barriers')
    st.write(top_values)

def display_city_distribution(i: int, barriers: BarrierReferralData):
    """
    Display the distribution of cities.

    Args:
        i (int): Number of cities to display in the distribution.
        barriers: BarrierReferralData class object.
    Returns:
        None
    """
    city_counts = barriers.barriers['zipcode'].apply(zco).astype('string').value_counts().reset_index()[:i]
    city_counts.columns = ['zipcode', 'count']
    fig_city = px.bar(city_counts, x='zipcode', y='count',
                    title='City Distribution',
                    labels={'zipcode': 'City', 'count': 'Count'})
    st.plotly_chart(fig_city, use_container_width=True)

def display_solution_pathways(i: int, barriers: BarrierReferralData):
    """
    Display the counts of Solution Pathways based.

    Args:
        i (int): Number of solution paths to display in the bar graph.
        barriers: BarrierReferralData class object.
    Returns:
        None
    """
    top_solution_data = BARRIERS.topValues('solution_path', 10)[:i]
    fig_solution = px.bar(top_solution_data, x=top_solution_data.index, y=top_solution_data.values,
                        labels={'y': 'Count', 'index': ' '},
                        title='Top Solution Pathways')
    st.plotly_chart(fig_solution, use_container_width=True)

def main():
    """
    Main function that builds Streamlit app.
    
    Args:
        None
    Returns:
        None
    """
    # Load and update data
    BARRIERS.updateData()

    # Get ethnicity Distribution and create figure
    ethnicity_counts = BARRIERS.barriers['ethnicity'].value_counts().reset_index()
    ethnicity_counts.columns = ['ethnicity', 'count']
    fig_ethnicity = px.pie(ethnicity_counts, names='ethnicity', values='count',
                        title='Ethnicity Distribution',
                        labels={'ethnicity': 'Ethnicity', 'count': 'Count'},
                        hole=0.3)
    fig_ethnicity.update_traces(textinfo='percent+label', pull=[0.1] * len(ethnicity_counts))

    # Get sex ratio and create figure
    sex_counts = BARRIERS.barriers['sex'].value_counts().reset_index()
    sex_counts.columns = ['sex', 'count']
    fig_sex = px.pie(sex_counts, names='sex', values='count',
                    title='Sex Distribution',
                    labels={'sex': 'Sex', 'count': 'Count'},
                    hole=0.3)
    fig_sex.update_traces(textinfo='percent+label', pull=[0.1] * len(sex_counts))

    # Get age distribution and create figure
    age_distribution = BARRIERS.barriers['age'].value_counts().sort_index().reset_index()
    age_distribution.columns = ['age', 'count']
    fig_age = px.histogram(age_distribution, x='age', y='count',
                           title='Age Distribution',
                           labels={'age': 'Age', 'count': 'Count'},
                           hover_data=['age', 'count'],
                           category_orders={"age": list(range(26))},
                           nbins=20)

    # Streamlit App Title (App components starts here)
    st.title('Orange County Healthcare Barriers for Children w/ IDD/MH')

    # Link to Barrier Log
    st.sidebar.markdown("[Barrier Log Link](https://form.jotform.com/240215836883158)")
    st.sidebar.markdown("[More information and context about this data.](https://github.com/jairus-m/barrierLog/blob/master/README.md)")
    

    # Sidebar for user input
    i = st.sidebar.number_input("Filter Barrier Count", min_value=1, value=5)
    i_city = st.sidebar.number_input("Filter City Count", min_value=1, value=5)
    i_solution_path = st.sidebar.number_input("Filter Solution Path", min_value=1, value=5)

    # all figures plotted below

    display_top_barriers(i, BARRIERS)

    st.plotly_chart(fig_ethnicity, use_container_width=True)

    st.plotly_chart(fig_sex, use_container_width=True)

    st.plotly_chart(fig_age, use_container_width=True)

    display_city_distribution(i_city, BARRIERS)

    display_solution_pathways(i_solution_path, BARRIERS)

    st.dataframe(BARRIERS.barriers.drop(columns=['date']))

    # Load button in sidebar
    load_csv_data(BARRIERS.barriers)


if __name__ == '__main__':
    main()
    