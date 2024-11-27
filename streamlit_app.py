import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import snowflake.snowpark as snowpark

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie.")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

try:
    cnx = snowpark.Session.builder.configs({
        "account": "UITVMUC-HYB64296",
        "user": "vyshnaviM",
        "password": "Password@598",
        "role": "SYSADMIN",
        "warehouse": "COMPUTE_WH",
        "database": "SMOOTHIES",
        "schema": "PUBLIC"
    }).create()

cnx = st.connection("snowflake")
session = cnx.session


session.sql("SELECT CURRENT_DATABASE()").collect()
    st.write("Connected to Snowflake successfully!")

except Exception as e:
    st.error(f"Failed to connect to Snowflake: {e}")

# Fetch data from Snowflake and convert to DataFrame
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
my_dataframe = pd.DataFrame(my_dataframe)

# Extract fruit names for multiselect
fruit_names = my_dataframe['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Use parameterized query for safety
        insert_stmt = """
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (%s, %s)
        """
        session.sql(insert_stmt, (ingredients_string.strip(), name_on_order)).collect()

        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
