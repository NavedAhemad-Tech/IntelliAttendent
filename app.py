
import streamlit as st

from pages import employees
from pages import attendance
from pages import reports
from modules.auth import authenticate_user
import dashboard

# Appliction configuration
st.set_page_config(
    page_title="IntelliAttendent",
    page_icon="👨‍💼",
    layout="wide"
    )

# ADD THE NEW CODE HERE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

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



# Login screen
if not st.session_state.logged_in:

    st.title("IntelliAttendent Login")
    st.subheader("Please enter your credentials")

    with st.form("login_form"):

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button("Login")

        if login_button:

            user = authenticate_user(
                username.strip(),
                password
            )

            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success("Login successful!")
                st.rerun()

            else:
                st.error("Invalid username or password.")

    st.stop()


# Get logged-in user's role
user_role = st.session_state.user["role"]

# Define menu permissions
if user_role == "Admin":

    allowed_menus = [
        "Dashboard",
        "Employee Management",
        "Employee List",
        "Update Employee",
        "Delete Employee",
        "Attendance",
        "Attendance History",
        "Reports"
    ]

elif user_role == "HR":

    allowed_menus = [
        "Dashboard",
        "Employee Management",
        "Employee List",
        "Update Employee",
        "Attendance",
        "Attendance History",
        "Reports"
    ]


elif user_role == "Manager":

    allowed_menus = [
        "Dashboard",
        "Attendance",
        "Attendance History",
        "Reports"
    ]

elif user_role == "Employee":
    allowed_menus = [
        "Dashboard",
        "My Attendance",
        "My Attendance History"
    ]
else:
    allowed_menus = ["Dashboard"]

# 3. Create menu variable
menu = st.sidebar.selectbox(
    "Select Module",
    allowed_menus
)

# 4. Display selected module
if menu == "Dashboard":
    st.subheader("Dashboard")
    st.info("welcome to the IntelliAttendent Dashboard")
    dashboard.show_dashboard()
elif menu == "Employee Management":
     st.header("Employee Management")
     employees.show_employee_page()

elif menu == "Attendance":
    attendance.show_attendance_page()

elif menu == "Reports":
    reports.show_attendance_summary()


elif menu == "Employee List":
    employees.show_employee_list()

elif menu == "Update Employee":
    employees.show_employee_update()

elif menu == "Delete Employee":
    employees.show_employee_delete()

elif menu == "Attendance History":
    attendance.show_attendance_history()

elif menu == "My Attendance":
    attendance.show_my_attendance(
        st.session_state.user["employee_id"]
    )
elif menu == "My Attendance History":
    attendance.show_my_attendance_history(
        st.session_state.user["employee_id"]
    )

# Initialize login session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# Display login screen
if not st.session_state.logged_in:

    st.title("IntelliAttendent Login")
    st.subheader("Please log in to continue")

    with st.form("login_form"):

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button("Login")

        if login_button:

            if not username.strip() or not password:
                st.warning("Please enter username and password.")

            else:
                user = authenticate_user(
                    username.strip(),
                    password
                )

                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user

                    st.success("Login successful!")
                    st.rerun()

                else:
                    st.error("Invalid username or password.")

    st.stop()


# Display logged-in user
st.sidebar.success(
    f"Welcome, {st.session_state.user['username']}"
)

st.sidebar.write(
    f"Role: {st.session_state.user['role']}"
)

st.sidebar.write(
    f"Employee ID: {st.session_state.user['employee_id']}"
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()


    




