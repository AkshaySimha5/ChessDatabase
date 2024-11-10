import streamlit as st
import mysql.connector
import pandas as pd

# Function to connect to the database
def connect_to_db():
    return mysql.connector.connect(
        host="localhost", 
        user=st.session_state.get('admin_id'),
        password=st.session_state.get('admin_password'),
        database="chess_db"
    )

def view_table(cursor, table_name, title):
    if(table_name=="tournament"):
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = ["Tournament ID", "Name", "Date", "Duration", "Location", "Type", "Organizer"]
    elif(table_name=="player"):
        cursor.execute(f"SELECT player_id, name, country, rating, email FROM {table_name}")
        columns = ["Player ID", "Name", "Country", "Rating", "Email"]
    elif(table_name=="game"):
        cursor.execute(f"SELECT game_id, site, white_name, black_name, result, termination, number_of_moves FROM {table_name}")
        columns = ["Game ID", "Site", "White", "Black", "Result", "Termination", "Total moves"]

    records = cursor.fetchall()
    if records:
        # Convert records to DataFrame
        df = pd.DataFrame(records)
        # Ensure the DataFrame uses specified columns
        df.columns = columns
        # Add an Index column starting from 1
        df.insert(0, "Index", range(1, len(df) + 1))
        # Set the Index column as the index
        df = df.set_index("Index")
        st.subheader(title)
        items_per_page = 20
        total_items = len(df)
        total_pages = (total_items + items_per_page - 1) // items_per_page

        # Create a pagination control
        page = st.number_input("Page", min_value=1, max_value=total_pages, step=1, value=1)

        # Calculate start and end indices of the current page
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page

        # Display the current page of data with pagination
        st.dataframe(df.iloc[start_index:end_index], use_container_width=True)
    else:
        st.subheader(title)
        st.info(f"No records found in {title.lower()}.")

# Delete a record by ID from a specified table
def delete_record(cursor, db, table_name, record_id, id_column):
    cursor.execute(f"SELECT * FROM {table_name} WHERE {id_column} = %s", (record_id,))
    if cursor.fetchone():
        cursor.execute(f"DELETE FROM {table_name} WHERE {id_column} = %s", (record_id,))
        db.commit()
        st.success(f"Deleted {table_name} with ID {record_id}.")
    else:
        st.warning(f"No record with ID {record_id} found in {table_name}.")

# Function to log out the admin
def logout():
    st.session_state['logged_in'] = False
    st.session_state['admin_id'] = None
    st.session_state['admin_password'] = None  # Reset the password as well
    st.success("You have been logged out.")
    st.rerun()  # Refreshes the page

# Main function for the admin dashboard
def admin_dashboard():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)

    # Navigation menu
    choice = st.sidebar.selectbox("Options", ["View Players", "View Games", "View Tournaments", "Delete Data"])
    if choice == "View Players":
        view_table(cursor, "player", "Players")
    elif choice == "View Games":
        view_table(cursor, "game", "Games")
    elif choice == "View Tournaments":
        view_table(cursor, "tournament", "Tournaments")
    elif choice == "Delete Data":
        delete_choice = st.radio("Choose what to delete", ["Player", "Game", "Tournament"])
        record_id = st.text_input("Enter ID to delete")
        if st.button(f"Delete {delete_choice}"):
            table_name = delete_choice.lower()
            id_column = f"{table_name}_id"
            delete_record(cursor, db, table_name, record_id, id_column)

    # Logout button
    if st.sidebar.button("Logout"):
        logout()

    cursor.close()
    db.close()

# Run the admin dashboard if this file is the entry point
if __name__ == "__main__":
    admin_dashboard()