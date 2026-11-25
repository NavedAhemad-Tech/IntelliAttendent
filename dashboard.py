
import streamlit as st
from database import get_connection
from datetime import date
import pandas as pd


def show_dashboard():

    st.title("IntelliAttend - Admin Dashboard")
    st.write("Employee Attendance Overview")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Total Employees
        cursor.execute("""
            SELECT COUNT(*) AS total_employees
            FROM employees
        """)

        total_employees = cursor.fetchone()["total_employees"]

        # 2. Present Today
        cursor.execute("""
            SELECT COUNT(DISTINCT employee_id) AS present_today
            FROM attendance_logs
            WHERE DATE(check_in) = %s
        """, (date.today(),))

        present_today = cursor.fetchone()["present_today"]

        # 3. Absent Today
        absent_today = total_employees - present_today

        # 4. Attendance Percentage
        attendance_percentage = (
            (present_today / total_employees) * 100
            if total_employees > 0 else 0
        )

        # Display KPI Cards
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Employees",
            total_employees
        )

        col2.metric(
            "Present Today",
            present_today
        )

        col3.metric(
            "Absent Today",
            absent_today
        )

        col4.metric(
            "Attendance %",
            f"{attendance_percentage:.2f}%"
        )
                # Monthly Attendance Trend
        st.subheader("Monthly Attendance Trend")

        cursor.execute("""
            SELECT
                DATE_FORMAT(attendance_date, '%Y-%m') AS month,
                COUNT(CASE
                    WHEN attendance_status = 'Present'
                    THEN 1
                END) AS present,
                COUNT(CASE
                    WHEN attendance_status = 'Absent'
                    THEN 1
                END) AS absent
            FROM attendance_logs
            GROUP BY month
            ORDER BY month
        """)

        # Fetch MySQL records
        monthly_data = cursor.fetchall()

        # Convert records into Pandas DataFrame
        df = pd.DataFrame(monthly_data)

                # Prepare chart data
        if not df.empty:

            df["month"] = pd.to_datetime(
                df["month"]
            ).dt.strftime("%b %Y")

            df = df.set_index("month")

            # Display monthly attendance chart
            st.line_chart(
                df[["present", "absent"]],
                x_label="Month",
                y_label="Employees",
                color=["#16A34A", "#EF4444"]
            )

        else:
            st.info("No monthly attendance data available.")

        

       

    except Exception as e:
        st.error(f"Unable to load dashboard: {e}")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
