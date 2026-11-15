import streamlit as st
from database import get_connection

def show_employee_page():

    st.title("Employee Registration")
    st.write("Register a new employee")

    with st.form("employee_form"):

        employee_code = st.text_input("Employee Code")
        employee_name = st.text_input("Employee Name")

        department = st.selectbox(
            "Department",
            ["HR", "IT", "Finance", "Administration", "Operations"]
        )

        email = st.text_input("Email Address")

        submit = st.form_submit_button("Register Employee")

        if submit:

            if not employee_code.strip() or not employee_name.strip():
                st.error("Employee Code and Name are required.")

            else:
                connection = None
                cursor = None

                try:
                    connection = get_connection()
                    cursor = connection.cursor()

                    query = """
                    INSERT INTO employees
                    (employee_code, employee_name, department, email)
                    VALUES (%s, %s, %s, %s)
                    """

                    values = (
                        employee_code.strip(),
                        employee_name.strip(),
                        department,
                        email.strip() if email.strip() else None
                    )

                    cursor.execute(query, values)
                    connection.commit()

                    st.success("Employee Registered Successfully!")

                except Exception as error:
                    st.error(f"Registration failed: {error}")

                finally:
                    if cursor:
                        cursor.close()

                    if connection and connection.is_connected():
                        connection.close()


# Select - Retrieve employee Records
# Like  - Seraches mataching text
# %search% - Finds text containing the serach term
# whee - filter records
# ORDER BY - Sorts the records in ascending or descending order
# fetchall() - Fetches all the records from the result set
# st.dataframe() - Displays the records in a tabular format

def show_employee_list():
    st.title("Employee List")
    st.write("View and search registered employees")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary = True)

        #Get availabe departments from the database
        department_query = """SELECT DISTINCT department FROM employees where department IS NOT NULL ORDER BY department"""
        cursor.execute(department_query)

        
        departments = ["All"]+[row ["department"] for row in cursor.fetchall()]
        
        # Search and filter control
        col1,col2 = st.columns(2)

        with col1:
           search= st.text_input("Search Employee", placeholder = "Enter employee code or name")

        with col2:
            department = st.selectbox("Filter by Department", departments)


            # Prapare SQL Query
        query = """ 
       SELECT employee_id, employee_code, employee_name,department, email from employees 
                where ( employee_code like %s OR employee_name Like %s)"""


        serach_value = f"%{search.strip()}%"
        values = [serach_value,serach_value]

        if department !="All":
            query += " AND department = %s"
            values.append(department)

        query += "ORDER BY employee_id DESC"

        cursor.execute(query,tuple(values))

        employees_data = cursor.fetchall()

        st.subheader("Registered Employees")

        if employees_data:
            st.dataframe(
                employees_data,
                use_container_width= True,
                hide_index = True
            )
            st.success(f"Total Employees: {len(employees_data)}")

        else:
            st.info("No employees found.")

    except Exception as error:
        st.error(f"Unable to load employee: {error}")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()




def show_employee_update():

    st.title( "Update Employee")
    st.write("Select and employee and update their details")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary = True)

        # Step 1 : Load Employees
        cursor.execute(""" Select employee_id, employee_code, employee_name from employees order by employee_name""")

        employee_data = cursor.fetchall()

        if not employee_data:
            st.info( "No employees registered yet.")
            return

        # Step 2: Create employee selection 
        employee_options = {
            row["employee_id"]:
            f'{row["employee_code"]} - {row["employee_name"]}'
            for row in employee_data
        }


        selected_id = st.selectbox(
            "Select Employee",
            options=list(employee_options.keys()),
            format_func=lambda x: employee_options[x]
        )

        # Step 3: Load selected employee details
        cursor.execute("""
            SELECT employee_code, employee_name, department, email
            FROM employees
            WHERE employee_id = %s
        """, (selected_id,))

        employee = cursor.fetchone()

        if employee:

            with st.form("update_employee_form"):

                employee_code = st.text_input(
                    "Employee Code",
                    value=employee["employee_code"]
                )

                employee_name = st.text_input(
                    "Employee Name",
                    value=employee["employee_name"]
                )

                department_list = [
                    "HR", "IT", "Finance",
                    "Administration", "Operations"
                ]

                current_department = employee["department"] or "HR"

                if current_department not in department_list:
                    department_list.append(current_department)

                department = st.selectbox(
                    "Department",
                    department_list,
                    index=department_list.index(current_department)
                )

                email = st.text_input(
                    "Email Address",
                    value=employee["email"] or ""
                )

                submit = st.form_submit_button("Update Employee")

                if submit:

                    if not employee_code.strip() or not employee_name.strip():
                        st.error("Employee Code and Name are required.")

                    else:
                        update_query = """
                            UPDATE employees
                            SET employee_code = %s,
                                employee_name = %s,
                                department = %s,
                                email = %s
                            WHERE employee_id = %s
                        """

                        values = (
                            employee_code.strip(),
                            employee_name.strip(),
                            department,
                            email.strip() or None,
                            selected_id
                        )

                        cursor.execute(update_query, values)
                        connection.commit()

                        st.success("Employee updated successfully!")

    except Exception as error:
        st.error(f"Unable to update employee: {error}")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()





def show_employee_delete():

    st.title("Delete Employee")
    st.warning("Deleting an employee cannot be undone.")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Step 1: Load employees
        cursor.execute("""
            SELECT employee_id, employee_code, employee_name
            FROM employees
            ORDER BY employee_name
        """)

        employee_data = cursor.fetchall()

        if not employee_data:
            st.info("No employees available to delete.")
            return

        employee_options = {
            row["employee_id"]:
            f'{row["employee_code"]} - {row["employee_name"]}'
            for row in employee_data
        }

        # Step 2: Select employee
        selected_id = st.selectbox(
            "Select Employee to Delete",
            options=list(employee_options.keys()),
            format_func=lambda x: employee_options[x]
        )

        st.write("Selected employee:", employee_options[selected_id])

        # Step 3: Check related records
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM users
                 WHERE employee_id = %s) AS user_count,
                (SELECT COUNT(*) FROM attendance_logs
                 WHERE employee_id = %s) AS attendance_count,
                (SELECT COUNT(*) FROM face_profiles
                 WHERE employee_id = %s) AS face_count,
                (SELECT COUNT(*) FROM voice_profiles
                 WHERE employee_id = %s) AS voice_count
        """, (selected_id, selected_id, selected_id, selected_id))

        related = cursor.fetchone()

        has_related_records = any(related.values())

        if has_related_records:
            st.error(
                "This employee has linked user, attendance, "
                "face or voice records. Deletion is blocked "
                "to protect related data."
            )
        else:
            # Step 4: Confirmation
            with st.form("delete_employee_form"):

                confirm = st.checkbox(
                    "I confirm that I want to permanently delete this employee."
                )

                submit = st.form_submit_button("Delete Employee")

                if submit:

                    if not confirm:
                        st.error("Please confirm before deleting.")

                    else:
                        cursor.execute(
                            "DELETE FROM employees WHERE employee_id = %s",
                            (selected_id,)
                        )

                        connection.commit()

                        st.success("Employee deleted successfully!")
                        st.rerun()

    except Exception as error:
        if connection and connection.is_connected():
            connection.rollback()

        st.error(f"Unable to delete employee: {error}")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

