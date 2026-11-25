
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

                current_time = datetime.now().strftime("%H:%M:%S")

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






def show_attendance_history():

    st.title("Attendance History")
    st.write("View and search employee attendance records.")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        search = st.text_input(
            "Search Employee",
            placeholder="Enter employee name or code"
        )

        selected_date = st.date_input(
            "Select Attendance Date",
            value=date.today()
        )

        query = """
            SELECT
                a.attendance_id,
                e.employee_code,
                e.employee_name,
                e.department,
                a.attendance_date,
                a.check_in,
                a.check_out,
                a.attendance_status,
                a.attendance_source
            FROM attendance_logs a
            INNER JOIN employees e
                ON a.employee_id = e.employee_id
            WHERE a.attendance_date = %s
            AND (
                e.employee_name LIKE %s
                OR e.employee_code LIKE %s
            )
            ORDER BY a.attendance_id DESC
        """

        search_value = f"%{search.strip()}%"

        cursor.execute(
            query,
            (selected_date, search_value, search_value)
        )

        records = cursor.fetchall()

        # Convert time values explicitly to 24-hour strings
        def format_time_24(value):

            if value is None:
                return ""

            if hasattr(value, "strftime"):
                return value.strftime("%H:%M:%S")

            if hasattr(value, "total_seconds"):
                total = int(value.total_seconds())
                hours, remainder = divmod(total, 3600)
                minutes, seconds = divmod(remainder, 60)
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            value = str(value)

            try:
                return datetime.strptime(
                    value, "%I:%M:%S %p"
                ).strftime("%H:%M:%S")
            except ValueError:
                return value

        for record in records:
            record["check_in"] = format_time_24(
                record["check_in"]
            )

            record["check_out"] = format_time_24(
                record["check_out"]
            )

        st.subheader("Attendance Records")

        if records:

            st.dataframe(
                records,
                width="stretch",
                hide_index=True
            )

            st.success(
                f"Total Attendance Records: {len(records)}"
            )

        else:
            st.info("No attendance records found.")

    except Exception as error:
        st.error(f"Unable to load attendance history: {error}")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()



def show_my_attendance(employee_id):

    st.title("My Attendance")
    st.write("Mark your own daily attendance.")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        today = date.today()

        cursor.execute("""
            SELECT employee_code, employee_name
            FROM employees
            WHERE employee_id = %s
        """, (employee_id,))

        employee = cursor.fetchone()

        if employee is None:
            st.error("Employee record not found.")
            return

        st.write("Employee:", employee["employee_name"])
        st.write("Employee Code:", employee["employee_code"])
        st.write("Date:", today)

        cursor.execute("""
            SELECT attendance_id, check_in, check_out
            FROM attendance_logs
            WHERE employee_id = %s
            AND attendance_date = %s
        """, (employee_id, today))

        attendance = cursor.fetchone()

        st.divider()

        if attendance is None:

            if st.button("Check In"):
                current_time = datetime.now().strftime("%H:%M:%S")

                cursor.execute("""
                    INSERT INTO attendance_logs
                    (employee_id, attendance_date, check_in,
                     attendance_status, attendance_source)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    employee_id,
                    today,
                    current_time,
                    "Present",
                    "Manual"
                ))

                connection.commit()
                st.success("Check-In successful!")
                st.rerun()

        else:
            st.success(f"Check-In: {attendance['check_in']}")

            if attendance["check_out"] is None:

                if st.button("Check Out"):
                    current_time = datetime.now().strftime("%H:%M:%S")

                    cursor.execute("""
                        UPDATE attendance_logs
                        SET check_out = %s
                        WHERE attendance_id = %s
                        AND employee_id = %s
                    """, (
                        current_time,
                        attendance["attendance_id"],
                        employee_id
                    ))

                    connection.commit()
                    st.success("Check-Out successful!")
                    st.rerun()

            else:
                st.success(
                    f"Check-Out: {attendance['check_out']}"
                )

    except Exception as error:
        if connection and connection.is_connected():
            connection.rollback()

        st.error(f"Attendance Error: {error}")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()



def show_my_attendance_history(employee_id):

    st.title("My Attendance History")
    st.write("View your previous attendance records.")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                attendance_date,
                check_in,
                check_out,
                TIMEDIFF(check_out, check_in) AS working_hours,
                attendance_status
            FROM attendance_logs
            WHERE employee_id = %s
            ORDER BY attendance_date DESC
        """, (employee_id,))

        records = cursor.fetchall()

        for record in records:
            record["check_in"] = format_time_24(record["check_in"])
            record["check_out"] = format_time_24(record["check_out"])
            record["working_hours"] = format_time_24(record["working_hours"])
        
          
        if records:
            st.success(
                f"Total attendance records: {len(records)}"
            )

            st.dataframe(
                records,
                use_container_width=True
            )

        else:
            st.info("No attendance records found.")

    except Exception as error:
        st.error(f"Attendance History Error: {error}")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


def format_time_24(value):
    if value is None:
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%H:%M:%S")

    if hasattr(value, "total_seconds"):
        total = int(value.total_seconds())
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    value = str(value)






           