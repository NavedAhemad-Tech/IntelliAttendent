
import streamlit as st

from pages import employees
from pages import attendance

# Appliction configuration
st.set_page_config(
    page_title="IntelliAttendent",
    page_icon="👨‍💼",
    layout="wide"
    )

# Application heading
st.title("IntelliAttendent")
st.subheader("AI - Based Employee Attendance Management")

st.write(
    "Welcome to IntelliAttendent."
    "This application will manage employee records"
    "and biometric attendance."
)
# Sidebar menu
st.sidebar.title("Menu")

menu = st.sidebar.selectbox(
    "Select Module",
    [   
         "Dashboard",
         "Employee Management",
         "Employee List",
         "Update Employee",
         "Delete Employee",
         "Attendance",
         "Reports"
    ]
)

# Display selected module
if menu == "Dashboard":
    st.subheader("Dashboard")
    st.info("welcome to the IntelliAttendent Dashboard")
elif menu == "Employee Management":
     st.header("Employee Management")
     employees.show_employee_page()

elif menu == "Attendance":
    attendance.show_attendance_page()

elif menu == "Reports":
    st.header("Attendance Reports")
    st.info("Reports module will be developed here.")


elif menu == "Employee List":
    employees.show_employee_list()

elif menu == "Update Employee":
    employees.show_employee_update()

elif menu == "Delete Employee":
    employees.show_employee_delete()




