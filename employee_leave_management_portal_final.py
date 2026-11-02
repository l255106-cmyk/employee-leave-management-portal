# Employee Leave Management Portal
# Backend-only Python project for Jupyter Notebook

import json
import os
from datetime import datetime

DATA_FILE = "leave_data.json"

# Demo accounts for testing
ACCOUNTS = {
    "admin": {"password": "admin123", "role": "admin"},
    "employee": {"password": "emp123", "role": "employee"}
}


def load_data():
    """Read saved leave requests from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        print("The data file has an incorrect format. Starting with empty records.")
        return []

    except (json.JSONDecodeError, OSError) as error:
        print("Could not read the data file:", error)
        return []


def save_data(leaves):
    """Save leave requests to the JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(leaves, file, indent=4)
        return True

    except OSError as error:
        print("Could not save the data:", error)
        return False


def login():
    """Check the username and password."""
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    if username in ACCOUNTS and ACCOUNTS[username]["password"] == password:
        print("Login successful.")
        return username, ACCOUNTS[username]["role"]

    print("Incorrect username or password.")
    return None, None


def read_date(message):
    """Ask for a date and check that it uses YYYY-MM-DD format."""
    while True:
        date_text = input(message).strip()

        try:
            return datetime.strptime(date_text, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD, for example 2026-11-10.")


def apply_leave(leaves, username):
    """Create a leave request for the logged-in employee."""
    print("\n--- Apply for Leave ---")

    employee_name = input("Employee name: ").strip()
    leave_type = input("Leave type (Annual/Sick/Casual): ").strip().title()

    if leave_type not in ["Annual", "Sick", "Casual"]:
        print("Please choose Annual, Sick, or Casual.")
        return

    start_date = read_date("Start date (YYYY-MM-DD): ")
    end_date = read_date("End date (YYYY-MM-DD): ")

    if end_date < start_date:
        print("End date cannot be before the start date.")
        return

    reason = input("Reason for leave: ").strip()

    if not employee_name or not reason:
        print("Employee name and reason cannot be empty.")
        return

    # Use the next available ID
    request_id = 1
    for item in leaves:
        if item["id"] >= request_id:
            request_id = item["id"] + 1

    request = {
        "id": request_id,
        "username": username,
        "employee_name": employee_name,
        "leave_type": leave_type,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "reason": reason,
        "status": "Pending"
    }

    leaves.append(request)

    if save_data(leaves):
        print("Leave request submitted successfully.")
        print("Your request ID is:", request_id)
    else:
        leaves.pop()


def view_leaves(leaves, username, role):
    """Admin sees all requests; employees see their own requests."""
    print("\n--- Leave Requests ---")

    if role == "admin":
        visible_leaves = leaves
    else:
        visible_leaves = [
            item for item in leaves if item["username"] == username
        ]

    if not visible_leaves:
        print("No leave requests found.")
        return

    for item in visible_leaves:
        print("-" * 35)
        print("Request ID:", item["id"])
        print("Employee:", item["employee_name"])
        print("Leave type:", item["leave_type"])
        print("Dates:", item["start_date"], "to", item["end_date"])
        print("Reason:", item["reason"])
        print("Status:", item["status"])


def search_leave(leaves, username, role):
    """Search for a request by its ID."""
    try:
        request_id = int(input("Enter request ID: "))
    except ValueError:
        print("Request ID must be a number.")
        return

    for item in leaves:
        if item["id"] == request_id:
            if role == "admin" or item["username"] == username:
                print("\nRequest found:")
                print("Employee:", item["employee_name"])
                print("Leave type:", item["leave_type"])
                print("Dates:", item["start_date"], "to", item["end_date"])
                print("Reason:", item["reason"])
                print("Status:", item["status"])
                return

    print("Request not found, or you do not have permission to view it.")


def update_leave(leaves):
    """Admin can approve or reject a pending request."""
    try:
        request_id = int(input("Enter request ID: "))
    except ValueError:
        print("Request ID must be a number.")
        return

    for item in leaves:
        if item["id"] == request_id:
            if item["status"] != "Pending":
                print("This request has already been processed.")
                return

            print("1. Approve")
            print("2. Reject")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                item["status"] = "Approved"
            elif choice == "2":
                item["status"] = "Rejected"
            else:
                print("Invalid option.")
                return

            if save_data(leaves):
                print("Request status updated to:", item["status"])
            return

    print("Request ID not found.")


def generate_report(leaves, username, role):
    """Show totals for leave requests."""
    if role == "admin":
        report_leaves = leaves
    else:
        report_leaves = [
            item for item in leaves if item["username"] == username
        ]

    total = len(report_leaves)
    pending = 0
    approved = 0
    rejected = 0

    for item in report_leaves:
        if item["status"] == "Pending":
            pending += 1
        elif item["status"] == "Approved":
            approved += 1
        elif item["status"] == "Rejected":
            rejected += 1

    print("\n--- Leave Report ---")
    print("Total requests:", total)
    print("Pending:", pending)
    print("Approved:", approved)
    print("Rejected:", rejected)


def employee_menu(leaves, username):
    """Display options for employees."""
    while True:
        print("\n--- Employee Menu ---")
        print("1. Apply for leave")
        print("2. View my leave requests")
        print("3. Search my request")
        print("4. Generate my report")
        print("5. Logout")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            apply_leave(leaves, username)
        elif choice == "2":
            view_leaves(leaves, username, "employee")
        elif choice == "3":
            search_leave(leaves, username, "employee")
        elif choice == "4":
            generate_report(leaves, username, "employee")
        elif choice == "5":
            print("Logged out.")
            break
        else:
            print("Invalid option. Please choose 1 to 5.")


def admin_menu(leaves, username):
    """Display options for the administrator."""
    while True:
        print("\n--- Admin Menu ---")
        print("1. View all leave requests")
        print("2. Search leave request")
        print("3. Approve or reject leave")
        print("4. Generate report")
        print("5. Logout")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            view_leaves(leaves, username, "admin")
        elif choice == "2":
            search_leave(leaves, username, "admin")
        elif choice == "3":
            update_leave(leaves)
        elif choice == "4":
            generate_report(leaves, username, "admin")
        elif choice == "5":
            print("Logged out.")
            break
        else:
            print("Invalid option. Please choose 1 to 5.")


def main():
    """Start the portal."""
    leaves = load_data()

    while True:
        print("\n===== Employee Leave Management Portal =====")
        print("1. Login")
        print("2. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            username, role = login()

            if role == "employee":
                employee_menu(leaves, username)
            elif role == "admin":
                admin_menu(leaves, username)

            # Reload data when the user returns to the main menu
            leaves = load_data()

        elif choice == "2":
            print("Thank you for using the portal.")
            break
        else:
            print("Invalid option. Please choose 1 or 2.")


# Run the portal
main()
