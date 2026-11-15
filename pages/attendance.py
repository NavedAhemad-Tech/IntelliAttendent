
import streamlit as st
from database import get_connection
from datetime import date, datetime


def show_attendance_page():

    st.title("Attendance Management")
    st.write("Mark employee daily attendance.")

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

        employees_data = cursor.fetchall()

        if not employees_data:
            st.warning("Please register an employee first.")
            return

        employee_options = {
            row["employee_id"]:
            f'{row["employee_code"]} - {row["employee_name"]}'
            for row in employees_data
        }

        # Step 2: Select employee
        selected_id = st.selectbox(
            "Select Employee",
            options=list(employee_options.keys()),
            format_func=lambda x: employee_options[x]
        )

        attendance_date = date.today()

        st.write("Attendance Date:", attendance_date)

        # Step 3: Check existing attendance
        cursor.execute("""
            SELECT attendance_id, check_in, check_out,
                   attendance_status
            FROM attendance_logs
            WHERE employee_id = %s
            AND attendance_date = %s
        """, (selected_id, attendance_date))

        attendance = cursor.fetchone()

        st.divider()

        # Step 4: Check-In
        st.subheader("Employee Check-In")

        if attendance is None:

            if st.button("Check In"):

                current_time = datetime.now().time().replace(microsecond=0)

                cursor.execute("""
                    INSERT INTO attendance_logs
                    (employee_id, attendance_date, check_in,
                     attendance_status, attendance_source)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    selected_id,
                    attendance_date,
                    current_time,
                    "Present",
                    "Manual"
                ))

                connection.commit()

                st.success("Check-In successful!")
                st.rerun()

        else:
            st.info(f"Check-In Time: {attendance['check_in']}")

        st.divider()

        # Step 5: Check-Out
        st.subheader("Employee Check-Out")

        if attendance is not None and attendance["check_out"] is None:

            if st.button("Check Out"):

                current_time = datetime.now().time().replace(microsecond=0)

                cursor.execute("""
                    UPDATE attendance_logs
                    SET check_out = %s
                    WHERE attendance_id = %s
                """, (
                    current_time,
                    attendance["attendance_id"]
                ))

                connection.commit()

                st.success("Check-Out successful!")
                st.rerun()

        elif attendance is not None:
            st.success(
                f"Check-Out Time: {attendance['check_out']}"
            )

        else:
            st.warning("Please Check-In before Check-Out.")

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        st.error(f"Attendance Error: {error}")

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
