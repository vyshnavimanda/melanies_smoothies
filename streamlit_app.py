# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark.functions import col


# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie.
    """)

# Get name input from the user
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# Use the Snowflake connection to get session
cnx = st.connection("snowflake")
session = cnx.session

# Query the list of available fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]  # Extracting fruit names into a list

# Let the user choose up to 5 fruits for their smoothie
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

# If ingredients are selected, proceed to insert the order into the database
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)  # Join selected fruits into a single string

    # Create the SQL insert statement
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Provide a button to submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Execute the SQL statement to insert the order into the database
        session.sql(my_insert_stmt).collect()

        # Show success message
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
