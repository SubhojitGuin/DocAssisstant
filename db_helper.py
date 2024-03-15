import mysql.connector

# Connect to the database
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="pandeyji_eatery"
)


def insert_order_item(food_item: str, quantity: int, order_id: int):
    try:
        # Create a cursor object
        cursor = cnx.cursor()

        # Calling the stored procedure
        cursor.callproc("insert_order_item", (food_item, quantity, order_id))

        # Commit the changes
        cnx.commit()

        # Close the cursor and the connection
        cursor.close()
        # cnx.close()

        print("Order item inserted successfully")

        return 1

    except Exception as e:
        print(f"An error occurred: {e}")

        # Rollback the changes if necessary
        cnx.rollback()

        return -1


def get_total_order_price(order_id: int):
    # Create a cursor object
    cursor = cnx.cursor()

    # Write the SQL query
    query = f"SELECT get_total_order_price({order_id})"

    # Execute the query
    cursor.execute(query)

    # Fetch the result
    result = cursor.fetchone()[0]

    # Close the cursor and the connection
    cursor.close()
    # cnx.close()

    return result


def insert_order_tracking(order_id: int, status: str):
    try:
        # Create a cursor object
        cursor = cnx.cursor()

        # Calling the stored procedure
        insert_query = (
            "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)")
        cursor.execute(insert_query, (order_id, status))

        # Commit the changes
        cnx.commit()

        # Close the cursor and the connection
        cursor.close()
        # cnx.close()

    except Exception as e:
        print(f"An error occurred: {e}")

        # Rollback the changes if necessary
        cnx.rollback()

        return -1


def get_order_status(order_id: int):
    # Create a cursor object
    cursor = cnx.cursor()

    # Write the SQL query
    query = ("SELECT status FROM order_tracking WHERE order_id = %s")

    # Execute the query
    cursor.execute(query, (order_id,))

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and the connection
    cursor.close()
    # cnx.close()

    if result is not None:
        return result[0]
    else:
        return None


def get_next_order_id():
    cursor = cnx.cursor()

    # Executing the SQL query to get the next available order_id
    query = ("SELECT MAX(order_id) FROM order_tracking")
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Close the cursor
    cursor.close()

    # Returning the next available order_id
    if result is None:
        return 1
    else:
        return result + 1
