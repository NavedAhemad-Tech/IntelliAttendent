
from openpyxl import Workbook
import streamlit as st
from database import get_connection
from datetime import date
import pandas as pd
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment


def show_attendance_summary():

    st.title("Attendance Summary Dashboard")
    st.write("Employee attendance overview and monthly reports.")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DATABASE() AS db_name, CURDATE() AS db_date")

        db_info = cursor.fetchone()

        st.write("Connected Database:", db_info["db_name"])
        st.write("Database Date:", db_info["db_date"])
        st.write("Python Date:", date.today())

        today = date.today()

        selected_date = st.date_input(
                "Select Attendance Date",
        value=today
        )

        month_start = selected_date.replace(day=1)
        

        # Step 1: Total employees
        cursor.execute("""
            SELECT COUNT(*) AS total_employees
            FROM employees
        """)

        total_data = cursor.fetchone()
        total_employees = total_data["total_employees"]

        # Step 2: Employees present today
        cursor.execute("""
            SELECT COUNT(DISTINCT employee_id) AS present_today
            FROM attendance_logs
            WHERE attendance_date = %s
            AND attendance_status = 'Present'
        """, (selected_date,))

        present_data = cursor.fetchone()
        present_today = present_data["present_today"]

        # Step 3: Calculate absent employees
        absent_today = max(total_employees - present_today, 0)

        # Step 4: Calculate attendance percentage
        if total_employees > 0:
            attendance_percentage = (
                present_today / total_employees
            ) * 100
        else:
            attendance_percentage = 0

        # Step 5: Display dashboard metrics
        st.subheader("Today's Attendance")

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

        st.divider()

        # Department-wise attendance
        st.subheader("Department-wise Attendance")

        cursor.execute("""
               SELECT
                e.department,
                COUNT(DISTINCT a.employee_id) AS present_employees
                FROM employees e
                LEFT JOIN attendance_logs a
                ON e.employee_id = a.employee_id
                AND a.attendance_date = %s
                AND a.attendance_status = 'Present'
                GROUP BY e.department
                ORDER BY e.department""",(selected_date,))
        
        department_records = cursor.fetchall()

       
        if department_records:
            department_chart = pd.DataFrame(department_records)

            st.bar_chart(
                department_chart,
                x="department",
                y="present_employees"
            )
       

        else:
            st.info("No. department attendance records found.")

        st.subheader("Today's Attendance Distribution")

        attendance_chart = pd.DataFrame(
            { "Status": ["Present","Absent"],
             "Employees": [present_today,absent_today]

            }
        )

        st.write("Present vs Absent Employees")

        st.bar_chart(
            attendance_chart,
            x="Status",
            y="Employees"
        )

        # Step 6: Monthly attendance by date
        st.subheader("Monthly Attendance Records")

        cursor.execute("""
            SELECT
                attendance_date,
                COUNT(DISTINCT employee_id) AS present_employees
            FROM attendance_logs
            WHERE attendance_date BETWEEN %s AND %s
            AND attendance_status = 'Present'
            GROUP BY attendance_date
            ORDER BY attendance_date DESC
        """, (month_start, selected_date))

        monthly_records = cursor.fetchall()

        if monthly_records:
            # Convert database records into DataFrame
            chart_data = pd.DataFrame(monthly_records)

            # Sort dates in ascending order
            chart_data = chart_data.sort_values("attendance_date")

            # Display montly attendance table
            st.dataframe(
                chart_data,
                width = "stretch",
                hide_index=True
            )
            # Display attendance trend chart
            st.subheader("Daily Attendance Trend")

            st.line_chart(
                chart_data,
                x="attendance_date",
                y="present_employees",
                x_label= "Attendance Date",
                y_label ="Present Employees"
            )
        else:
            st.info("No monthly attendance records found")

        st.divider()

        # Step 7: Employee-wise monthly attendance
        st.subheader("Employee-wise Monthly Attendance")

        cursor.execute("""
            SELECT
                e.employee_code,
                e.employee_name,
                e.department,
                COUNT(DISTINCT a.attendance_date) AS present_days
            FROM employees e
            LEFT JOIN attendance_logs a
                ON e.employee_id = a.employee_id
                AND a.attendance_date BETWEEN %s AND %s
                AND a.attendance_status = 'Present'
            GROUP BY
                e.employee_id,
                e.employee_code,
                e.employee_name,
                e.department
            ORDER BY e.employee_name
        """, (month_start, selected_date))

        employee_summary = cursor.fetchall()

        if employee_summary:
            # Convert database records into DataFrame
            employee_df = pd.DataFrame(employee_summary)

            #Display attendance table
            st.dataframe(
                employee_df,
                width="stretch",
                hide_index=True
            )
         # Create Excel file in memory
            excel_buffer = BytesIO()
        
            with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
            ) as writer:
        
        # Sheet 1: Monthly Attendance
                employee_df.to_excel(
                writer,
                index=False,
                sheet_name="Monthly Attendance"
                )
        
                workbook = writer.book
                worksheet = writer.sheets["Monthly Attendance"]
        
            # Header formatting
                header_fill = PatternFill(
                start_color="1F4E78",
                end_color="1F4E78",
                fill_type="solid"
                        )
        
                header_font = Font(
                bold=True,
                color="FFFFFF",
                size=11
                )
        
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center")
        
            # Column widths
                column_widths = {
                 "A": 18,
                 "B": 25,
                 "C": 20,
                 "D": 18
                 }
        
                for column, width in column_widths.items():
                     worksheet.column_dimensions[column].width = width
        
              # Add borders
                thin_border = Border(
                bottom=Side(style="thin", color="D9E2F3")
                )
        
                for row in worksheet.iter_rows(min_row=2):
                    for cell in row:
                        cell.border = thin_border
        
                # Freeze header and enable filters
                worksheet.freeze_panes = "A2"
                worksheet.auto_filter.ref = f"A1:D{worksheet.max_row}"
        
                # Total present days
                last_row = worksheet.max_row
                total_row = last_row + 1
        
                worksheet.cell(
                     row=total_row,
                    column=3,
                    value="Total Present Days"
                    )
        
                worksheet.cell(
                    row=total_row,
                    column=4,
                    value=f"=SUM(D2:D{last_row})" if last_row >= 2 else "=0"
                    )
        
                worksheet.cell(row=total_row, column=3).font = Font(bold=True)
                worksheet.cell(row=total_row, column=4).font = Font(bold=True)
        
            # Sheet 2: Summary
                summary = workbook.create_sheet("Summary")
        
                summary["A1"] = "INTELLIATTENDENT - ATTENDANCE REPORT"
                summary.merge_cells("A1:B1")
        
                summary["A1"].font = Font(bold=True, size=16, color="FFFFFF")
                summary["A1"].fill = header_fill
        
                summary["A3"] = "Report Date"
                summary["B3"] = str(selected_date)
        
                summary["A4"] = "Report Period"
                summary["B4"] = f"{month_start} to {selected_date}"
        
                summary["A5"] = "Total Employees"
                summary["B5"] = len(employee_df)
        
                summary["A6"] = "Total Present Days"
                summary["B6"] = f"='Monthly Attendance'!D{total_row}"
        
                summary.column_dimensions["A"].width = 25
                summary.column_dimensions["B"].width = 35
        
                summary.freeze_panes = "A3"

                
            # Sheet 3: Department Summary

                department_summary = (
                    employee_df.groupby("department")["present_days"]
                    .sum()
                    .reset_index()
)

                department_summary.to_excel(
                    writer,
                    index=False,
                    sheet_name="Department Summary"
                    )

                dept_sheet = writer.sheets["Department Summary"]

            # Format headers
                for cell in dept_sheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center")

            # Column widths
                dept_sheet.column_dimensions["A"].width = 25
                dept_sheet.column_dimensions["B"].width = 20

            # Add borders
                for row in dept_sheet.iter_rows(min_row=2):
                    for cell in row:
                        cell.border = thin_border

            # Add total
                total_row_dept = dept_sheet.max_row + 1

                dept_sheet.cell(
                row=total_row_dept,
                column=1,
                value="Grand Total"
                )

                dept_sheet.cell(
                row=total_row_dept,
                column=2,
                value=f"=SUM(B2:B{total_row_dept - 1})"
                )

                dept_sheet.cell(row=total_row_dept, column=1).font = Font(bold=True)
                dept_sheet.cell(row=total_row_dept, column=2).font = Font(bold=True)

        # Add Bar Chart
                from openpyxl.chart import BarChart, Reference

                chart = BarChart()

                chart.title = "Department-wise Attendance"
                chart.x_axis.title = "Department"
                chart.y_axis.title = "Present Days"

                data = Reference(
                dept_sheet,
                min_col=2,
                min_row=1,
                max_row=dept_sheet.max_row - 1
                )

                categories = Reference(
                dept_sheet,
                min_col=1,
                min_row=2,
                max_row=dept_sheet.max_row - 1
                )

                chart.add_data(data, titles_from_data=True)
                chart.set_categories(categories)

                chart.height = 8
                chart.width = 15

                dept_sheet.add_chart(chart, "D2")









        
             # Download Excel button
            st.download_button(
            label="📥 Download Employee Attendance Excel",
            data=excel_buffer.getvalue(),
            file_name=f"Employee_Attendance_{selected_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )    
         
        else:
            st.info("No employee attendance records found.")


    except Exception as error:
        st.error(f"Unable to load attendance summary: {error}")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
