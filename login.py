from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as tkMessageBox
import mysql.connector
from tkinter import messagebox
import tkinter.filedialog as filedialog
import json


def Database():
    global conn, cursor
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="", database=""
        )
        cursor = conn.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS hrdbsystem")
        conn.commit()

        conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="hrdbsystem"
        )
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INT AUTO_INCREMENT PRIMARY KEY,
            position VARCHAR(225),
            firstname VARCHAR(225),
            lastname VARCHAR(225),
            address VARCHAR(225),
            birthdate VARCHAR(225),
            age INT,
            stat VARCHAR(225),
            gender VARCHAR(225),
            username VARCHAR(225),
            upass VARCHAR(225)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            employee_id INT,
            username VARCHAR(225),
            upass VARCHAR(225),
            role INT,
            PRIMARY KEY (employee_id),
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS position_history (
            history_id INT PRIMARY KEY AUTO_INCREMENT,
            employee_id INT,
            old_position VARCHAR(100),
            new_position VARCHAR(100),
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )

        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payroll (
            employee_id INT,
            rate_per_day FLOAT,
            work_days INT,
            gross_pay FLOAT,
            sss_contribution FLOAT,
            phil_health FLOAT,
            cash_advance FLOAT,
            total_deductions FLOAT,
            net_pay FLOAT,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
        )
        """)

        procedure = """
        CREATE PROCEDURE IF NOT EXISTS insert_employee_user (
            IN position_param VARCHAR(225),
            IN firstname_param VARCHAR(225),
            IN lastname_param VARCHAR(225),
            IN address_param VARCHAR(225),
            IN birthdate_param VARCHAR(225),
            IN age_param INT,
            IN stat_param VARCHAR(225),
            IN gender_param VARCHAR(225),
            IN username_param VARCHAR(225),
            IN upass_param VARCHAR(225),
            IN role_param INT
        )
        BEGIN
            DECLARE employee_id INT;

            INSERT INTO employees (position, firstname, lastname, address, birthdate, age, stat, gender, username, upass)
            VALUES (position_param, firstname_param, lastname_param, address_param, birthdate_param, age_param, stat_param, gender_param, username_param, upass_param);

            SET employee_id = LAST_INSERT_ID();

            INSERT INTO users (employee_id, username, upass, role)
            VALUES (employee_id, username_param, upass_param, role_param);

            SELECT employee_id;
        END
        """
        cursor.execute(procedure)

        procedure = """
        CREATE PROCEDURE IF NOT EXISTS update_employee_role (
            IN employee_id_param INT,
            IN new_role_param INT
        )
        BEGIN
            UPDATE users
            SET role = new_role_param
            WHERE employee_id = employee_id_param;
            
            SELECT CONCAT('Role updated for employee_id ', employee_id_param) AS 'Result';
        END
        """
        cursor.execute(procedure)

        trigger = """
        CREATE TRIGGER IF NOT EXISTS after_update_position
        AFTER UPDATE ON employees
        FOR EACH ROW
        BEGIN
            IF OLD.position != NEW.position THEN
                INSERT INTO position_history (employee_id, old_position, new_position, update_time)
                VALUES (NEW.employee_id, OLD.position, NEW.position, NOW());
            END IF;
        END
        """
        cursor.execute(trigger)
        
        conn.commit()
    except mysql.connector.Error as e:
        tkMessageBox.showerror("Database Error", str(e))

def Login():
    Database()
    username = loginUsernameEntry.get()
    password = loginPasswordEntry.get()

    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count == 0:
            # If no users exist in the database, create a default admin user
            cursor.execute("""
            INSERT INTO employees (position, firstname, lastname, address, birthdate, age, stat, gender, username, upass) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ('Admin', 'Admin', 'Admin', 'Admin Address', '25 December 1998', 25, 'Single', 'Male', 'admin', 'admin'))
            
            cursor.execute("SELECT LAST_INSERT_ID()")
            employee_id = cursor.fetchone()[0]

            cursor.execute("""
            INSERT INTO users (employee_id, username, upass, role)
            VALUES (%s, %s, %s, %s)
            """, (employee_id, 'admin', 'admin', 0))
            conn.commit()

        cursor.execute("SELECT * FROM users WHERE username = %s AND upass = %s", (username, password))
        user = cursor.fetchone()

        if user:
            role = user[3]  # Assuming role is stored at index 3 in the users table
            if role == 0:
                # Admin login
                loginWindow.withdraw()
                adminManagement()
            elif role == 1:
                # Employee login
                loginWindow.withdraw()
                employeeManagement(user[0])
            else:
                tkMessageBox.showerror("Login Error", "Invalid role for user")
        else:
            tkMessageBox.showerror("Login Error", "Invalid username or password")
    except Exception as e:
        tkMessageBox.showerror("Database Error", str(e))


def employeeManagement(employee_id):

    def fetch_data(employee_id):
        try:
            cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
            row = cursor.fetchone()
            if row:
                employeeIDEntry.config(state='normal')
                employeeNameEntry.config(state='normal')
                employeeLastEntry.config(state='normal')
                employeeAddressEntry.config(state='normal')
                employeeBirthdateEntry.config(state='normal')
                employeeAgeEntry.config(state='normal')
                employeeStatusEntry.config(state='normal')
                employeeGenderEntry.config(state='normal')
                employeeIDEntry.delete(0, END)
                employeeIDEntry.insert(0, row[0])
                employeeNameEntry.delete(0, END)
                employeeNameEntry.insert(0, row[2])
                employeeLastEntry.delete(0, END)
                employeeLastEntry.insert(0, row[3])
                employeeAddressEntry.delete(0, END)
                employeeAddressEntry.insert(0, row[4])
                employeeBirthdateEntry.delete(0, END)
                employeeBirthdateEntry.insert(0, row[5])
                employeeAgeEntry.delete(0, END)
                employeeAgeEntry.insert(0, row[6])
                employeeStatusEntry.delete(0, END)
                employeeStatusEntry.insert(0, row[7])
                employeeGenderEntry.delete(0, END)
                employeeGenderEntry.insert(0, row[8])
                employeeIDEntry.config(state='disabled')
                employeeNameEntry.config(state='disabled')
                employeeLastEntry.config(state='disabled')
                employeeAddressEntry.config(state='disabled')
                employeeBirthdateEntry.config(state='disabled')
                employeeAgeEntry.config(state='disabled')
                employeeStatusEntry.config(state='disabled')
                employeeGenderEntry.config(state='disabled')
                pass
            else:
                messagebox.showinfo("No Data", "No data found for the given ID.")

        except mysql.connector.Error as e:
            tkMessageBox.showerror("Database Error", str(e))

    employeeWindow = Toplevel()
    employeeWindow.title("Administration Management")
    employeeWindow.geometry("900x450")
    employeeWindow.resizable(0, 0)


    def logout():
        confirm = messagebox.askyesno("Confirmation", "Are you sure you want to logout?")
        if confirm:
            employeeWindow.destroy()
            # Open the login window again
            loginWindow.deiconify()
            clear_login_fields()

    def clear_login_fields():
        loginUsernameEntry.delete(0, 'end')
        loginPasswordEntry.delete(0, 'end')
        
    def fetch_payroll_data(employee_id):
        try:
            cursor.execute("SELECT * FROM payroll WHERE employee_id = %s", (employee_id,))
            payroll_data = cursor.fetchone()
            if payroll_data:
                # Display payroll details in the employeePayrollFrame
                Label(employeePayrollFrame, text=f"Rate per Day: {payroll_data[1]}", font=('Times New Roman', 15), bg='white').pack(anchor='w')
                Label(employeePayrollFrame, text=f"Work Days: {payroll_data[2]}", font=('Times New Roman', 15), bg='white').pack(anchor='w')
                Label(employeePayrollFrame, text=f"Gross Pay: {payroll_data[3]}", font=('Times New Roman', 15), bg='white').pack(anchor='w')
                Label(employeePayrollFrame, text=f"SSS Contribution: {payroll_data[4]}", font=('Times New Roman', 15), bg='white').pack(anchor='w')
                Label(employeePayrollFrame, text=f"Phil Health Contribution: {payroll_data[5]}", font=('Times New Roman', 15), bg='white').pack(anchor='w')
                Label(employeePayrollFrame, text=f"Cash Advance: {payroll_data[6]}", font=('Times New Roman', 15), bg='white').pack(anchor='w')
                Label(employeePayrollFrame, text=f"Total Deductions: {payroll_data[7]}", font=('Times New Roman', 15), bg='white').pack(anchor='w')
                Label(employeePayrollFrame, text=f"Net Pay: {payroll_data[8]}", font=('Times New Roman', 15), bg='white').pack(anchor='w')
            else:
                messagebox.showinfo("No Data", "No payroll data found for the selected employee.")
        except mysql.connector.Error as e:
            tkMessageBox.showerror("Database Error", str(e))

    employeeFrame = Frame(employeeWindow, bd=2, relief='raised', bg='lightblue')
    employeeFrame.place(x=20, y=10, width=860, height=430)
    employeePayrollFrame = Frame(employeeFrame, bd=2, relief='sunken', bg='white')
    employeePayrollFrame.place(x=420, y=10, width=420, height=400)
    fetch_payroll_data(employee_id)


    employeeIDWindow = Label(employeeWindow, text="ID Number:", font=('Times New Roman', 14), bg='lightblue')
    employeeIDWindow.place(x=40, y=50)
    employeeIDEntry = Entry(employeeWindow, font=('Times New Roman', 12), state='disabled')
    employeeIDEntry.place(x=145, y=50, width=240)

    employeeNameWindow = Label(employeeWindow, text="Firstname:", font=('Times New Roman', 14), bg='lightblue')
    employeeNameWindow.place(x=40, y=90)
    employeeNameEntry = Entry(employeeWindow, font=('Times New Roman', 12), state='disabled')
    employeeNameEntry.place(x=145, y=90, width=240)

    employeeLastWindow = Label(employeeWindow, text="Lastname:", font=('Times New Roman', 14), bg='lightblue')
    employeeLastWindow.place(x=40, y=130)
    employeeLastEntry = Entry(employeeWindow, font=('Times New Roman', 12), state='disabled')
    employeeLastEntry.place(x=145, y=130, width=240)

    employeeAddressWindow = Label(employeeWindow, text="Address:", font=('Times New Roman', 14), bg='lightblue')
    employeeAddressWindow.place(x=40, y=170)
    employeeAddressEntry = Entry(employeeWindow, font=('Times New Roman', 12), state='disabled')
    employeeAddressEntry.place(x=145, y=170, width=240)

    employeeBirthdateWindow = Label(employeeWindow, text="Birthdate:", font=('Times New Roman', 14), bg='lightblue')
    employeeBirthdateWindow.place(x=40, y=210)
    employeeBirthdateEntry = Entry(employeeWindow, font=('Times New Roman', 12), state='disabled')
    employeeBirthdateEntry.place(x=145, y=210, width=240)

    employeeAgeWindow = Label(employeeWindow, text="Age:", font=('Times New Roman', 14), bg='lightblue')
    employeeAgeWindow.place(x=40, y=250)
    employeeAgeEntry = Entry(employeeWindow, font=('Times New Roman', 12), state='disabled')
    employeeAgeEntry.place(x=145, y=250, width=240)

    employeeStatusWindow = Label(employeeWindow, text="Status:", font=('Times New Roman', 14), bg='lightblue')
    employeeStatusWindow.place(x=40, y=290)
    employeeStatusEntry = Entry(employeeWindow, font=('Times New Roman', 12), state='disabled')
    employeeStatusEntry.place(x=145, y=290, width=240)

    employeeGenderWindow = Label(employeeWindow, text="Gender:", font=('Times New Roman', 14), bg='lightblue')
    employeeGenderWindow.place(x=40, y=330)
    employeeGenderEntry = Entry(employeeWindow, font=('Times New Roman', 12), state='disabled')
    employeeGenderEntry.place(x=145, y=330, width=240)

    saveButton = Button(employeeWindow, text="Save", font=('Times New Roman', 12, 'bold'), width=10, height=1, command=exit)
    saveButton.place(x=160, y=380)

    menubar = Menu(employeeWindow)
    filemenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Employee", menu=filemenu)
    filemenu.add_command(label="Profile")
    filemenu.add_command(label="Logout", command=logout)
    employeeWindow.config(menu=menubar)

    Database()
    fetch_data(employee_id)

    employeeWindow.mainloop()

def adminManagement():
    pass
    def get_next_employee_id():
        cursor.execute("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'hrdbsystem' AND TABLE_NAME = 'employees'")
        result = cursor.fetchone()
        next_id = result[0] if result else 1
        return f"{next_id:010d}"

    def save_data():
        Database()
    
        # Gather data from entry fields
        position = readonly_combobox.get()
        firstname = employeeNameEntry.get()
        lastname = employeeLastEntry.get()
        address = employeeAddressEntry.get()
        birthdate = f"{day_combobox.get()} {month_combobox.get()} {year_combobox.get()}"
        age = employeeAgeEntry.get()
        status = status_combobox.get()
        gender = gender_combobox.get()
        username = employeeUsernameEntry.get()
        password = employeePasswordEntry.get()
        confirm_password = employeeConfirmPassEntry.get()
    
        # Determine role based on position
        role = 0 if position == "Admin" else 1  # Assuming 0 for Admin, 1 for Employee
    
        # Validate inputs
        if not (position and firstname and lastname and address and birthdate != 'Day Month Year' and age and status != 'Select Status' and gender != 'Select Gender' and username and password and confirm_password):
            tkMessageBox.showerror("Input Error", "Please fill all fields")
            return
    
        if password != confirm_password:
            tkMessageBox.showerror("Password Error", "Passwords do not match")
            return
    
        try:
            # Check for duplicate entry
            cursor.execute("SELECT * FROM employees WHERE employee_id = %s AND firstname = %s AND lastname = %s", (employeeIDEntry.get(), firstname, lastname))
            existing_employee = cursor.fetchone()
            if existing_employee:
                tkMessageBox.showerror("Duplicate Entry", "Employee already exists.")
                return
    
            # Call stored procedure to insert data
            cursor.callproc('insert_employee_user', (
                position, firstname, lastname, address, birthdate, age, status, gender, username, password, role
            ))
    
            # Commit changes to the database
            conn.commit()
    
            # Show success message and clear fields
            tkMessageBox.showinfo("Success", "Data saved successfully")
            clear_fields()
    
            # Refresh displayed data (if needed)
            fetch_and_display_data()
    
        except Exception as e:
            tkMessageBox.showerror("Database Error", str(e))
    

    def delete_data():
        selected_item = tree.selection()
        if not selected_item:
            tkMessageBox.showerror("Selection Error", "Please select a record to delete.")
            return

        confirmation = tkMessageBox.askyesno("Confirmation", "Are you sure you want to delete the selected record?")
        if confirmation:
            try:
                for item in selected_item:
                    values = tree.item(item, 'values')
                    employee_id = values[0]
                    cursor.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
                    conn.commit()
                tkMessageBox.showinfo("Success", "Record(s) deleted successfully")
                clear_fields()
                fetch_and_display_data()

            except Exception as e:
                tkMessageBox.showerror("Database Error", str(e))
            

    def update_data():
        selected_item = tree.selection()
        if not selected_item:
            tkMessageBox.showerror("Selection Error", "Please select a record to update.")
            return

        position = readonly_combobox.get()
        firstname = employeeNameEntry.get()
        lastname = employeeLastEntry.get()
        address = employeeAddressEntry.get()
        birthdate = f"{day_combobox.get()} {month_combobox.get()} {year_combobox.get()}"
        age = employeeAgeEntry.get()
        status = status_combobox.get()
        gender = gender_combobox.get()
        username = employeeUsernameEntry.get()
        password = employeePasswordEntry.get()

        if position == "Select an option" or not firstname or not lastname or not address or birthdate == 'Day Month Year' or not age or status == 'Select Status' or gender == 'Select Gender' or not username or not password:
            tkMessageBox.showerror("Input Error", "Please fill all fields")
            return

        confirmation = tkMessageBox.askyesno("Confirmation", "Are you sure you want to update the selected record?")
        if confirmation:
            try:
                for item in selected_item:
                    values = tree.item(item, 'values')
                    employee_id = values[0]

                    # Update employee details
                    cursor.execute("""
                        UPDATE employees 
                        SET position=%s, firstname=%s, lastname=%s, address=%s, birthdate=%s, age=%s, stat=%s, gender=%s, username=%s, upass=%s
                        WHERE employee_id=%s
                    """, (position, firstname, lastname, address, birthdate, age, status, gender, username, password, employee_id))

                    # Update employee role using stored procedure
                    role = 0 if position == "Admin" else 1
                    cursor.callproc('update_employee_role', (employee_id, role))

                    conn.commit()

                tkMessageBox.showinfo("Success", "Record(s) updated successfully")
                clear_fields()
                fetch_and_display_data()

            except Exception as e:
                tkMessageBox.showerror("Database Error", str(e))

    def display_employee_id():
        employeeIDEntry.config(state=NORMAL)
        employeeIDEntry.delete(0, END)
        employeeIDEntry.insert(0, get_next_employee_id())
        employeeIDEntry.config(state=DISABLED)

    def clear_entry_fields():
        readonly_combobox.set("Select an option")
        display_employee_id()
        employeeNameEntry.delete(0, END)
        employeeLastEntry.delete(0, END)
        employeeAddressEntry.delete(0, END)
        day_combobox.set('Day')
        month_combobox.set('Month')
        year_combobox.set('Year')
        employeeAgeEntry.delete(0, END)
        status_combobox.set('Select Status')
        gender_combobox.set('Select Gender')
        employeeUsernameEntry.delete(0, END)
        employeePasswordEntry.delete(0, END)
        employeeConfirmPassEntry.delete(0, END)

    def fetch_and_display_data():
        Database()
        for record in tree.get_children():
            tree.delete(record)

        cursor.execute("SELECT employee_id, position, firstname, lastname, address, birthdate, age, stat, gender, username,upass FROM employees")
        rows = cursor.fetchall()

        for row in rows:
            tree.insert('', 'end', values=row)

    def clear_fields():
        readonly_combobox.set("Select an option")
        display_employee_id()
        employeeNameEntry.delete(0, END)
        employeeLastEntry.delete(0, END)
        employeeAddressEntry.delete(0, END)
        day_combobox.set('Day')
        month_combobox.set('Month')
        year_combobox.set('Year')
        employeeAgeEntry.delete(0, END)
        status_combobox.set('Select Status')
        gender_combobox.set('Select Gender')
        employeeUsernameEntry.delete(0, END)
        employeePasswordEntry.delete(0, END)
        employeeConfirmPassEntry.delete(0, END)

    def fetch_selected_data(event):
        selected_item = tree.selection()
        for item in selected_item:
            values = tree.item(item, 'values')
            if values:
                employee_id = values[0]  
                readonly_combobox.set(values[1])
                employeeIDEntry.config(state=NORMAL)
                employeeIDEntry.delete(0, END)
                employeeIDEntry.insert(0, employee_id)
                employeeIDEntry.config(state=DISABLED)
                employeeNameEntry.delete(0, END)
                employeeNameEntry.insert(0, values[2])
                employeeLastEntry.delete(0, END)
                employeeLastEntry.insert(0, values[3])
                employeeAddressEntry.delete(0, END)
                employeeAddressEntry.insert(0, values[4])
                if len(values) > 5:
                    day, month, year = values[5].split()
                    day_combobox.set(day)
                    month_combobox.set(month)
                    year_combobox.set(year)
                employeeAgeEntry.delete(0, END)
                employeeAgeEntry.insert(0, values[6])
                status_combobox.set(values[7])
                gender_combobox.set(values[8])
                employeeUsernameEntry.delete(0, END)
                employeeUsernameEntry.insert(0, values[9])
                employeePasswordEntry.delete(0, END)
                employeePasswordEntry.insert(0, values[10])
                employeeConfirmPassEntry.delete(0, END)
                employeeConfirmPassEntry.insert(0, values[10])
            else:
                tkMessageBox.showerror("Data Error", "Selected record contains empty values.")

    def search_data(event=None):
        search_text = searchEntry.get().lower()
        for record in tree.get_children():
            tree.delete(record)
        cursor.execute("SELECT employee_id, position, firstname, lastname, address, birthdate, age, stat, gender, username, upass FROM employees")
        rows = cursor.fetchall()
        for row in rows:
            if search_text in str(row).lower():
                tree.insert('', 'end', values=row)


    def on_combobox_key(event, combobox, values):
        value = combobox.get().lower()
        if value == '':
            combobox['values'] = values
        else:
            filtered_values = [str(item) for item in values if value in str(item).lower()]
            combobox['values'] = filtered_values
            #combobox.event_generate('<Down>')


    def clear_placeholder(event, combobox, placeholder):
        if combobox.get() == placeholder:
            combobox.set('')

    def reset_placeholder(event, combobox, placeholder):
        if combobox.get() == '':
            combobox.set(placeholder)

    def logout():
        confirm = messagebox.askyesno("Confirmation", "Are you sure you want to logout?")
        if confirm:
            admin.destroy()
            # Open the login window again
            loginWindow.deiconify()
            clear_login_fields()

    def clear_login_fields():
        loginUsernameEntry.delete(0, 'end')
        loginPasswordEntry.delete(0, 'end')

    def exportData():
        try:
            # Fetch data from employees table
            cursor.execute("SELECT employee_id, position, firstname, lastname, address, birthdate, age, stat, gender, username, upass FROM employees")
            employees_data = cursor.fetchall()
    
            # Fetch data from users table
            cursor.execute("SELECT employee_id, username, upass, role FROM users")
            users_data = cursor.fetchall()
    
            # Fetch data from position_history table
            cursor.execute("SELECT history_id, employee_id, old_position, new_position, update_time FROM position_history")
            position_history_data = cursor.fetchall()
    
            # Combine all data into a dictionary
            data = {
                'employees': employees_data,
                'users': users_data,
                'position_history': position_history_data
            }
    
            if not any(data.values()):
                tkMessageBox.showwarning("No Data", "No records found to export.")
                return
    
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if file_path:
                with open(file_path, 'w') as file:
                    json.dump(data, file, default=str, indent=4)
                tkMessageBox.showinfo("Export Successful", "Data exported successfully to JSON file.")
    
        except mysql.connector.Error as e:
            tkMessageBox.showerror("Export Error", f"Error: {e}")


    def importData():
        try:
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if file_path:
                with open(file_path, 'r') as file:
                    data = json.load(file)
    
                    # Import data into employees table
                    if 'employees' in data:
                        employees_data = data['employees']
                        for row in employees_data:
                            cursor.execute("""
                                INSERT INTO employees (employee_id, position, firstname, lastname, address, birthdate, age, stat, gender, username, upass) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, tuple(row))
                    
                    # Import data into users table
                    if 'users' in data:
                        users_data = data['users']
                        for row in users_data:
                            cursor.execute("""
                                INSERT INTO users (employee_id, username, upass, role) 
                                VALUES (%s, %s, %s, %s)
                            """, tuple(row))
                    
                    # Import data into position_history table
                    if 'position_history' in data:
                        position_history_data = data['position_history']
                        for row in position_history_data:
                            cursor.execute("""
                                INSERT INTO position_history (history_id, employee_id, old_position, new_position, update_time) 
                                VALUES (%s, %s, %s, %s, %s)
                            """, tuple(row))
                    
                    conn.commit()
                tkMessageBox.showinfo("Import Successful", "Data imported successfully from JSON file.")
                fetch_and_display_data()  # Refresh displayed data after import
    
        except Exception as e:
            tkMessageBox.showerror("Import Error", str(e))
    

    

    def payroll():
        admin.withdraw()
        payrollManagement()
        
    #==========adminFrame============
    admin = Toplevel()
    admin.title("Administration Management")
    admin.geometry("1200x700")
    admin.resizable(0, 0)
    
    #==========registerFrame=========
    registerFrame = Frame(admin, bd=2, relief='raised', bg='lightblue')
    registerFrame.place(x=30, y=10, width=600, height=680)
    registerFrameLabel = Label(registerFrame, text="Employee Management", font=('Times New Roman', 20, 'bold'), bg='lightblue')
    registerFrameLabel.place(x=140, y=10)
    
    employeePosition = Label(registerFrame, text="Position:", font=('Times New Roman', 14), bg='lightblue')
    employeePosition.place(x=60, y=70)
    
    readonly_combobox = ttk.Combobox(registerFrame, font=('Times New Roman', 12), values=["Employee", "Admin"], state="readonly")
    readonly_combobox.place(x=225, y=70)
    readonly_combobox.set("Select an option")

    
    employeeID = Label(registerFrame, text="ID Number:", font=('Times New Roman', 14), bg='lightblue')
    employeeID.place(x=60, y=110)
    employeeIDEntry = Entry(registerFrame, font=('Times New Roman', 14), bg='white', relief='sunken', bd=1, state='disabled')
    employeeIDEntry.place(x=225, y=110, width=290)
    display_employee_id()
    
    employeeName = Label(registerFrame, text="Firstname:", font=('Times New Roman', 14), bg='lightblue')
    employeeName.place(x=60, y=150)
    employeeNameEntry = Entry(registerFrame, font=('Times New Roman', 12))
    employeeNameEntry.place(x=225, y=150, width=290)
    
    employeeLast = Label(registerFrame, text="Lastname:", font=('Times New Roman', 14), bg='lightblue')
    employeeLast.place(x=60, y=190)
    employeeLastEntry = Entry(registerFrame, font=('Times New Roman', 12))
    employeeLastEntry.place(x=225, y=190, width=290)
    
    employeeAddress = Label(registerFrame, text="Address:", font=('Times New Roman', 14), bg='lightblue')
    employeeAddress.place(x=60, y=230)
    employeeAddressEntry = Entry(registerFrame, font=('Times New Roman', 12))
    employeeAddressEntry.place(x=225, y=230, width=290)
    
    employeeBirthdate = Label(registerFrame, text="Birthdate:", font=('Times New Roman', 14), bg='lightblue')
    employeeBirthdate.place(x=60, y=270)
    
    days = list(range(1, 32))
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    years = list(range(2024, 1899, -1))
    
    day_combobox = ttk.Combobox(registerFrame, values=days, font=('Times New Roman', 12))
    day_combobox.place(x=225, y=270, width=80)
    day_combobox.set('Day')
    day_combobox.bind('<FocusIn>', lambda event: clear_placeholder(event, day_combobox, 'Day'))
    day_combobox.bind('<FocusOut>', lambda event: reset_placeholder(event, day_combobox, 'Day'))
    day_combobox.bind('<KeyRelease>', lambda event: on_combobox_key(event, day_combobox, days))
    
    month_combobox = ttk.Combobox(registerFrame, values=months, font=('Times New Roman', 12))
    month_combobox.place(x=313, y=270, width=100)
    month_combobox.set('Month')
    month_combobox.bind('<FocusIn>', lambda event: clear_placeholder(event, month_combobox, 'Month'))
    month_combobox.bind('<FocusOut>', lambda event: reset_placeholder(event, month_combobox, 'Month'))
    month_combobox.bind('<KeyRelease>', lambda event: on_combobox_key(event, month_combobox, months))
    
    year_combobox = ttk.Combobox(registerFrame, values=years, font=('Times New Roman', 12))
    year_combobox.place(x=420, y=270, width=100)
    year_combobox.set('Year')
    year_combobox.bind('<FocusIn>', lambda event: clear_placeholder(event, year_combobox, 'Year'))
    year_combobox.bind('<FocusOut>', lambda event: reset_placeholder(event, year_combobox, 'Year'))
    year_combobox.bind('<KeyRelease>', lambda event: on_combobox_key(event, year_combobox, years))
    
    
    employeeAge = Label(registerFrame, text="Age:", font=('Times New Roman', 14), bg='lightblue')
    employeeAge.place(x=60, y=310)
    employeeAgeEntry = Entry(registerFrame, font=('Times New Roman', 12))
    employeeAgeEntry.place(x=225, y=310, width=202)
    
    employeeStatus = Label(registerFrame, text="Status:", font=('Times New Roman', 14), bg='lightblue')
    employeeStatus.place(x=60, y=350)
    
    status = ["Single", "Married"]
    
    status_combobox = ttk.Combobox(registerFrame, values=status, font=('Times New Roman', 12))
    status_combobox.place(x=225, y=350, width=200)
    status_combobox.set('Select Status')
    status_combobox.bind('<FocusIn>', lambda event: clear_placeholder(event, status_combobox, 'Select Status'))
    status_combobox.bind('<FocusOut>', lambda event: reset_placeholder(event, status_combobox, 'Select Status'))
    status_combobox.bind('<KeyRelease>', lambda event: on_combobox_key(event, status_combobox, status))
    
    employeeGender = Label(registerFrame, text="Gender:", font=('Times New Roman', 14), bg='lightblue')
    employeeGender.place(x=60, y=390)
    
    genders = ["Male", "Female"]
    
    gender_combobox = ttk.Combobox(registerFrame, values=genders, font=('Times New Roman', 12))
    gender_combobox.place(x=225, y=390, width=200)
    gender_combobox.set('Select Gender')
    gender_combobox.bind('<FocusIn>', lambda event: clear_placeholder(event, gender_combobox, 'Select Gender'))
    gender_combobox.bind('<FocusOut>', lambda event: reset_placeholder(event, gender_combobox, 'Select Gender'))
    gender_combobox.bind('<KeyRelease>', lambda event: on_combobox_key(event, gender_combobox, genders))
    
    employeeUsername = Label(registerFrame, text="Username:", font=('Times New Roman', 14), bg='lightblue')
    employeeUsername.place(x=60, y=430)
    employeeUsernameEntry = Entry(registerFrame, font=('Times New Roman', 12))
    employeeUsernameEntry.place(x=225, y=430, width=290)
    
    employeePassword = Label(registerFrame, text="Password:", font=('Times New Roman', 14), bg='lightblue')
    employeePassword.place(x=60, y=470)
    employeePasswordEntry = Entry(registerFrame, font=('Times New Roman', 12), show="*")
    employeePasswordEntry.place(x=225, y=470, width=290)
    
    employeeConfirmPass = Label(registerFrame, text="Confirm Password:", font=('Times New Roman', 14), bg='lightblue')
    employeeConfirmPass.place(x=60, y=510)
    employeeConfirmPassEntry = Entry(registerFrame, font=('Times New Roman', 12), show="*")
    employeeConfirmPassEntry.place(x=225, y=510, width=290)
    
    saveButton = Button(registerFrame, text="Save", font=('Times New Roman', 12, 'bold'), width=10, height=1, command=save_data)
    saveButton.place(x=60, y=600)
    deleteButton = Button(registerFrame, text="Delete", font=('Times New Roman', 12, 'bold'), width=10, height=1, command=delete_data)
    deleteButton.place(x=180, y=600)
    updateButton = Button(registerFrame, text="Update", font=('Times New Roman', 12, 'bold'), width=10, height=1, command=update_data)
    updateButton.place(x=300, y=600)
    clearButton = Button(registerFrame, text="Clear", font=('Times New Roman', 12, 'bold'), width=10, height=1, command=clear_entry_fields)
    clearButton.place(x=420, y=600)
    #==========employeeListFrame=====
    employeeListFrame = Frame(admin, bd=2, relief='raised')
    employeeListFrame.place(x=650, y=50, width=520, height=640)
    
    searchLabel = Label(admin, text="Search:", font=('Times New Roman', 14))
    searchLabel.place(x=650, y=20)
    searchEntry = Entry(admin, font=('Times New Roman', 12))
    searchEntry.place(x=730, y=20, width=400)
    searchEntry.bind("<Return>", search_data)
    
    
    scrollbarx = Scrollbar(employeeListFrame, orient=HORIZONTAL)
    scrollbary = Scrollbar(employeeListFrame, orient=VERTICAL)
    tree = ttk.Treeview(employeeListFrame, columns=("EmployeeID", "Position", "Firstname", "Lastname", "Address", "Birthdate", "Age", "Status", "Gender", "Username", "Password"),
    selectmode="extended", height=100, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
    scrollbary.config(command=tree.yview)
    scrollbary.pack(side=RIGHT, fill=Y)
    scrollbarx.config(command=tree.xview)
    scrollbarx.pack(side=BOTTOM, fill=X)
    tree.heading('EmployeeID', text="Employee ID", anchor=W)
    tree.heading('Position', text="Position", anchor=W)
    tree.heading('Firstname', text="Firstname", anchor=W)
    tree.heading('Lastname', text="Lastname", anchor=W)
    tree.heading('Address', text="Address", anchor=W)
    tree.heading('Birthdate', text="Birthdate", anchor=W)
    tree.heading('Age', text="Age", anchor=W)
    tree.heading('Status', text="Status", anchor=W)
    tree.heading('Gender', text="Gender", anchor=W)
    tree.heading('Username', text="Username", anchor=W)
    tree.heading('Password', text="Password", anchor=W)
    tree.column('#0', stretch=NO, minwidth=0, width=0)
    tree.column('#1', stretch=NO, minwidth=0, width=80)
    tree.column('#2', stretch=NO, minwidth=0, width=100)
    tree.column('#3', stretch=NO, minwidth=0, width=100)
    tree.column('#4', stretch=NO, minwidth=0, width=100)
    tree.column('#5', stretch=NO, minwidth=0, width=150)
    tree.column('#6', stretch=NO, minwidth=0, width=130)
    tree.column('#7', stretch=NO, minwidth=0, width=100)
    tree.column('#8', stretch=NO, minwidth=0, width=80)
    tree.column('#9', stretch=NO, minwidth=0, width=100)
    tree.column('#10', stretch=NO, minwidth=0, width=100)
    tree.column('#11', stretch=NO, minwidth=0, width=100)
    tree.bind("<<TreeviewSelect>>", fetch_selected_data)
    tree.pack()
    fetch_and_display_data()
    
    
    menubar = Menu(admin)
    filemenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Admin", menu=filemenu)
    menubar.add_cascade(label="Payroll", command=payroll)
    filemenu.add_command(label="Profile")
    filemenu.add_command(label="Export", command=exportData)
    filemenu.add_command(label="Import", command=importData)
    filemenu.add_command(label="Logout", command=logout)
    
    admin.config(menu=menubar)
    
    
    admin.mainloop()


def payrollManagement():
    def calculateData():
        rate = float(RPD.get())
        days = int(WORK_DAY.get())
        cash_adv = float(CPA.get())
        gross_pay = rate * days
        sss_contribution = gross_pay * 0.11  # Example SSS contribution rate
        phil_health_contribution = gross_pay * 0.03  # Example PhilHealth contribution rate
        total_deductions = sss_contribution + phil_health_contribution + cash_adv
        net_pay = gross_pay - total_deductions

        GP.set(str(gross_pay))
        SSS.set(str(sss_contribution))
        PHIL_HEALTH.set(str(phil_health_contribution))
        TD.set(str(total_deductions))
        NP.set(str(net_pay))

    def saveData():
        emp_no = EMP_NUM.get()
        emp_name = EMP_NAME.get()
        rate = float(RPD.get())
        days = int(WORK_DAY.get())
        cash_adv = float(CPA.get())
        gross_pay = float(GP.get())
        sss_contribution = float(SSS.get())
        phil_health_contribution = float(PHIL_HEALTH.get())
        total_deductions = float(TD.get())
        net_pay = float(NP.get())
        
        # Check if the employee already has a payroll record
        cursor.execute("SELECT COUNT(*) FROM payroll WHERE employee_id=%s", (emp_no,))
        record_exists = cursor.fetchone()[0]
        
        if record_exists:
            # Update the existing record
            cursor.execute("""
                UPDATE payroll
                SET rate_per_day=%s, work_days=%s, gross_pay=%s, sss_contribution=%s, phil_health=%s, cash_advance=%s, total_deductions=%s, net_pay=%s
                WHERE employee_id=%s
            """, (rate, days, gross_pay, sss_contribution, phil_health_contribution, cash_adv, total_deductions, net_pay, emp_no))
        else:
            # Insert a new record
            cursor.execute("""
                INSERT INTO payroll (employee_id, rate_per_day, work_days, gross_pay, sss_contribution, phil_health, cash_advance, total_deductions, net_pay)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (emp_no, rate, days, gross_pay, sss_contribution, phil_health_contribution, cash_adv, total_deductions, net_pay))
        
        conn.commit()
        tkMessageBox.showinfo("Data Saved", "Payroll data has been saved successfully.")

        EMP_NUM.set('')
        EMP_NAME.set('')
        RPD.set('')
        WORK_DAY.set('')
        CPA.set('')
        GP.set('')
        SSS.set('')
        PHIL_HEALTH.set('')
        TD.set('')
        NP.set('')

        display_data()

    def deleteData():
        selected_item = tree.selection()[0]
        item_id = tree.item(selected_item)['values'][0]
        cursor.execute("DELETE FROM payroll WHERE employee_id=%s", (item_id,))
        conn.commit()
        tree.delete(selected_item)
        display_data()

    def display_data():
        tree.delete(*tree.get_children())
        cursor.execute("""
        SELECT e.employee_id, CONCAT(e.firstname, ' ', e.lastname), p.rate_per_day, p.work_days, p.gross_pay, p.sss_contribution, p.phil_health, p.cash_advance, p.total_deductions, p.net_pay
        FROM employees e
        LEFT JOIN payroll p ON e.employee_id = p.employee_id
        """)
        rows = cursor.fetchall()
        for row in rows:
            tree.insert('', 'end', values=row)

    def on_tree_select(event):
        selected_item = tree.selection()[0]
        item = tree.item(selected_item)
        emp_id = item['values'][0]
        emp_name = item['values'][1]
        EMP_NUM.set(emp_id)
        EMP_NAME.set(emp_name)
    
    def exportData():
        # Ask user for file save location
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return  # User canceled the save dialog

        cursor.execute("""
        SELECT e.employee_id, CONCAT(e.firstname, ' ', e.lastname), p.rate_per_day, p.work_days, p.gross_pay, p.sss_contribution, p.phil_health, p.cash_advance, p.total_deductions, p.net_pay
        FROM employees e
        LEFT JOIN payroll p ON e.employee_id = p.employee_id
        """)
        rows = cursor.fetchall()

        # Prepare JSON data
        data = []
        for row in rows:
            data.append({
                'Employee ID': row[0],
                'Employee Name': row[1],
                'Rate/Day': row[2],
                'Work Days': row[3],
                'Gross Pay': row[4],
                'SSS Contribution': row[5],
                'Phil Health': row[6],
                'Cash Advance': row[7],
                'Total Deductions': row[8],
                'Net Pay': row[9]
            })

        # Write data to JSON file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        tkMessageBox.showinfo("Export Successful", f"Data exported to {file_path} successfully.")



    def admin():
        root.withdraw()
        adminManagement()

    def clear_login_fields():
        loginUsernameEntry.delete(0, 'end')
        loginPasswordEntry.delete(0, 'end')

    def logout():
        confirm = messagebox.askyesno("Confirmation", "Are you sure you want to logout?")
        if confirm:
            root.destroy()
            # Open the login window again
            loginWindow.deiconify()
            clear_login_fields()

    def importData():
        # Ask user to select JSON file for import
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return  # User canceled the dialog
    
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
    
            for item in data:
                emp_id = item['Employee ID']
                emp_name = item['Employee Name']
                rate_day = item['Rate/Day']
                work_days = item['Work Days']
                gross_pay = item['Gross Pay']
                sss_contribution = item['SSS Contribution']
                phil_health = item['Phil Health']
                cash_advance = item['Cash Advance']
                total_deductions = item['Total Deductions']
                net_pay = item['Net Pay']
    
                cursor.execute("""
                INSERT INTO payroll (employee_id, rate_per_day, work_days, gross_pay, sss_contribution, phil_health, cash_advance, total_deductions, net_pay)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (emp_id, rate_day, work_days, gross_pay, sss_contribution, phil_health, cash_advance, total_deductions, net_pay))
            
            conn.commit()
            tkMessageBox.showinfo("Import Successful", f"Data imported from {file_path} successfully.")
            display_data()
    
        except Exception as e:
            tkMessageBox.showerror("Import Error", f"Failed to import data from {file_path}: {str(e)}")
    
    

    root = Toplevel()
    root.title("Administrator")
    root.geometry("1050x750+200+10")
    root.resizable(0, 0)

    frame1 = Frame(root, borderwidth=2, relief=RIDGE)
    frame1.place(x=50, y=70, width=450, height=290)
    frame2 = Frame(root, borderwidth=2, relief=RIDGE)
    frame2.place(x=520, y=70, width=480, height=290)
    frame3 = Frame(root, borderwidth=2, relief=RIDGE)
    frame3.place(x=50, y=380, width=950, height=340)
    #VARIABLES
    EMP_NUM = StringVar()
    EMP_NAME = StringVar()
    RPD = StringVar()
    WORK_DAY = StringVar()
    GP =StringVar()
    SSS = StringVar()
    PHIL_HEALTH = StringVar()
    CPA = StringVar()
    TD = StringVar()
    NP = StringVar()
    #FRAME1
    Label(root, text='Payroll Management System', font='Arial 30 bold', fg='Black').grid(row=0, column=0, padx=(252, 0), pady=(10))

    Label(frame1, text="Employee's I.D:", font='arial 11 bold', fg='black').place(x=30, y=30)
    emp_No = Entry(frame1, font='arial 12', fg='black', width=20, textvariable=EMP_NUM, state='disabled')
    emp_No.place(x=200, y=30)

    Label(frame1, text="Name :", font='arial 11 bold', fg='black').place(x=30, y=70)
    emp_N = Entry(frame1, font='arial 12 ', fg='black', width=20, textvariable=EMP_NAME, state='disabled')
    emp_N.place(x=200, y=70)

    Label(frame1, text="Rate/Day :", font='arial 11 bold', fg='black').place(x=30, y=110)
    rpd = Entry(frame1, font='arial 12', fg='black', width=20, textvariable=RPD)         
    rpd.place(x=200, y=110)

    Label(frame1, text="No. of days worked :", font='arial 11 bold', fg='Black').place(x=30, y=150)
    no_work_d = Entry(frame1, font='arial 12', fg='black', width=20, textvariable=WORK_DAY)
    no_work_d.place(x=200, y=150)

    Label(frame1, text="Cash Advance :", font='arial 12 bold', fg='black').place(x=30, y=190)
    cpa = Entry(frame1, font='arial 12 bold', fg='black', width=20, textvariable=CPA)
    cpa.place(x=200, y=190)

    btn_cal = Button(frame1, text="Calculate", width=15, borderwidth=2, height=2, bg="#97ffff", cursor="hand2", command=calculateData)
    btn_cal.place(x=30, y=230)
    btn_save = Button(frame1, text="Save", width=15, borderwidth=2, height=2, fg="white", bg="blue", cursor="hand2", command=saveData)
    btn_save.place(x=160, y=230)
    btn_delete = Button(frame1, text="Delete", width=15, borderwidth=2, height=2, fg="white", bg="red", cursor="hand2", command=deleteData)
    btn_delete.place(x=290, y=230)

    #FRAME2
    Label(frame2, text="Gross Pay:", font='arial 12 bold', fg='Black').place(x=50, y=30)
    gp = Label(frame2, font='arial 12 bold underline', fg='black', textvariable=GP, bg='white', width=20, underline=True)
    gp.place(x=200, y=30)
    Label(frame2, text="SSS Contribution:", font='arial 12 bold', fg='Black').place(x=50, y=70)
    sssc = Label(frame2, font='arial 12 bold underline', fg='black', textvariable=SSS, bg='white', width=20, underline=True)
    sssc.place(x=200, y=70)
    Label(frame2, text="Phil Health:", font='arial 12 bold', fg='Black').place(x=50, y=110)
    ph = Label(frame2, font='arial 12 bold underline', fg='black', textvariable=PHIL_HEALTH, bg='white', width=20, underline=True)
    ph.place(x=200, y=110)
    Label(frame2, text="Cash Advance:", font='arial 12 bold', fg='Black').place(x=50, y=150)
    cpa = Label(frame2, font='arial 12 bold underline', fg='Red', textvariable=CPA, bg='white', width=20, underline=True)
    cpa.place(x=200, y=150)
    Label(frame2, text="Total Deduction:", font='arial 12 bold', fg='Black').place(x=50, y=190)
    td = Label(frame2, font='arial 12 bold underline', fg='black', textvariable=TD, bg='white', width=20, underline=True)
    td.place(x=200, y=190)
    Label(frame2, text="Net Pay:", font='arial 12 bold', fg='Black').place(x=50, y=230)
    np = Label(frame2, font='arial 12 bold underline', fg='black', textvariable=NP, bg='white', width=20, underline=True)
    np.place(x=200, y=230)



    #FRAME3
    log_message = Label(frame3,text='', font='arial 10 ',
          fg='pink', bg='#17161b')
    #data table===================================================================

    scrollbary = Scrollbar(frame3, orient=VERTICAL)
    scrollbarx = Scrollbar(frame3, orient=HORIZONTAL)
    tree = ttk.Treeview(frame3, columns=("Employee’s ID", "Employee’s Name", "Rate/Day", "No. of days worked",
                                        "Gross Pay",'SSS Con’t','Phil Health','C/A ','Total Deductions','Net Pay'),
                         selectmode="extended", height=700, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
    scrollbary.config(command=tree.yview)
    scrollbary.pack(side=RIGHT, fill=Y)
    scrollbarx.config(command=tree.xview)
    scrollbarx.pack(side=BOTTOM, fill=X)
    tree.heading('Employee’s ID', text="Employee’s ID", anchor=N)
    tree.heading('Employee’s Name', text="Employee’s Name", anchor=N)
    tree.heading('Rate/Day', text="Rate/Day", anchor=N)
    tree.heading('No. of days worked', text="No. of days worked", anchor=N)
    tree.heading('Gross Pay', text="Gross Pay", anchor=N)
    tree.heading('SSS Con’t', text="SSS Con’t", anchor=N)
    tree.heading('Phil Health', text="Phil Health", anchor=N)
    tree.heading('C/A ', text="C/A ", anchor=N)
    tree.heading('Total Deductions', text="Total Deductions", anchor=N)
    tree.heading('Net Pay', text="Net Pay", anchor=N)
    tree.column('#0', stretch=YES, minwidth=0, width=0, anchor=CENTER)
    tree.column('#1', stretch=YES, minwidth=0, width=60, anchor=CENTER)
    tree.column('#2', stretch=YES, minwidth=0, width=140, anchor=CENTER)
    tree.column('#3', stretch=YES, minwidth=0, width=140, anchor=CENTER)
    tree.column('#4', stretch=YES, minwidth=0, width=110, anchor=CENTER)
    tree.column('#5', stretch=YES, minwidth=0, width=130, anchor=CENTER)
    tree.column('#6', stretch=YES, minwidth=0, width=90, anchor=CENTER)
    tree.column('#7', stretch=YES, minwidth=0, width=70, anchor=CENTER)
    tree.column('#8', stretch=YES, minwidth=0, width=70, anchor=CENTER)
    tree.column('#9', stretch=YES, minwidth=0, width=70, anchor=CENTER)
    tree.column('#10', stretch=YES, minwidth=0, width=100, anchor=CENTER)
    tree.bind("<<TreeviewSelect>>", on_tree_select)
    tree.pack()

    Database()
    display_data()

    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Admin", menu=filemenu)
    menubar.add_cascade(label="Payroll")
    filemenu.add_command(label="Admin", command=admin)
    filemenu.add_command(label="Export", command=exportData)
    filemenu.add_command(label="Import", command=importData)
    filemenu.add_command(label="Logout", command=logout)
    
    root.config(menu=menubar)

    root.mainloop()

Database()

loginWindow = Tk()
loginWindow.title("Login")
loginWindow.geometry("550x380+200+10")
loginWindow.resizable(0, 0)

loginUsernameLabel = Label(loginWindow, text="Username:", font=('Times New Roman', 15), bd=10)
loginUsernameLabel.place(x=70, y=80)
loginUsernameEntry = Entry(loginWindow, font=('Times New Roman', 15), width=25)
loginUsernameEntry.place(x=190, y=85)

loginPasswordLabel = Label(loginWindow, text="Password:", font=('Times New Roman', 15), bd=10)
loginPasswordLabel.place(x=70, y=140)
loginPasswordEntry = Entry(loginWindow, font=('Times New Roman', 15), width=25, show="*")
loginPasswordEntry.place(x=190, y=145)

btn_login = Button(loginWindow, text="Login", font=('Times New Roman', 15), width=10, command=Login)
btn_login.place(x=300, y=230)
btn_exit = Button(loginWindow, text="Exit", font=('Times New Roman', 15), width=10, command=exit)
btn_exit.place(x=150, y=230)

loginWindow.mainloop()
