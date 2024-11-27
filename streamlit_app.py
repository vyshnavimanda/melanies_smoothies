import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import snowflake.snowpark as snowpark
import requests


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

# cnx = st.connection("snowflake")
    session = cnx

    session.sql("SELECT CURRENT_DATABASE()").collect()
    # st.write("Connected to Snowflake successfully!")

except Exception as e:
    st.error(f"Failed to connect to Snowflake: {e}")

# Fetch data from Snowflake and convert to DataFrame
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON')).collect()
# st.dataframe(data=my_dataframe, use_container_width=True)
my_dataframe = pd.DataFrame(my_dataframe)
# st.stop()

# Extract fruit names for multiselect
fruit_names = my_dataframe['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        # st.text((smoothiefroot_response).json())
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # # Use parameterized query for safety
        # insert_stmt = """
        #     INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        #     VALUES (%s, %s)
        # """
        # session.sql(insert_stmt, (ingredients_string.strip(), name_on_order)).collect()

        # st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
        try:
            insert_stmt = """
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES (?, ?)
             """
            session.sql(insert_stmt, (ingredients_string.strip(), name_on_order)).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Error while placing the order: {str(e)}")
            print(f"Error details: {e}")





