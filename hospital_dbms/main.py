from flask import Flask, render_template, redirect, url_for, request, session
from flask_mysqldb import MySQL

app = Flask(__name__)


# Database confirgurations
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "hospital_admin"
# create username = hospital_admin
# password = "cse2018"
# Add your root password below
app.config['MYSQL_PASSWORD'] = "cse2018"
app.config['MYSQL_DB'] = "hospital"

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html', msg='HOME')

# Admin Portal Functionality
@app.route('/admin-index')
def admin_index():
    return render_template('admin_index.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'login_id' in request.form and 'password' in request.form:
        username = request.form['login_id']
        password = request.form['password']
        access_level = 'Admin'
        print(username, password)
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE login_id = %s AND password = %s AND access_level= %s', (username, password, access_level))
        account = cur.fetchone()
        if account:
            print(session)
            session['loggedin'] = True
            print(account)
            print(session)
            msg = 'Logged in'
            print("SUCCESS!")
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect LoginID or Password!'
            print("FAIL")
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('index'))

@app.route('/admin/view-data', methods = ['GET', 'POST'])
def view_data():
    cur = mysql.connection.cursor()
    tables = cur.execute("show full tables where Table_Type = 'BASE TABLE'")
    tables = cur.fetchall()

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        table = request.form['table']
        print(table)
        labels = cur.execute("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = \'{}\'".format(table))
        labels = cur.fetchall()
        data = cur.execute("SELECT * FROM {}".format(table))
        data = cur.fetchall()
        print(labels)
        return render_template('view-data.html', tables=tables, table=table, labels=labels, data=data)
    print(tables)
    return render_template('view-data.html', tables = tables)

# Staff Portal Functionality
@app.route('/staff-index')
def staff_index():
    return render_template('staff_index.html')

@app.route('/employees')
def employees():
    cur = mysql.connection.cursor()
    employees = cur.execute("SELECT * from Employees")

    if employees > 0:
        employee_info = cur.fetchall()
        return render_template('employee.html', employee_info=employee_info)

    return ("<h2>No employee entry in the database</h2>")

@app.route('/register', methods=['GET', 'POST'])
def employee_reg():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        contact = request.form['contact']
        designation = request.form['designation']
        email = request.form['email']
        address = request.form['address']
        salary = request.form['salary']
        cur = mysql.connection.cursor()
        ids = cur.execute("SELECT id FROM employees")
        ids = cur.fetchall()

        # checking for duplicate entry
        eid = (id,)
        if eid in ids:
            return render_template("already_exists.html", id = id)
        else:
            if designation == "Doctor":
                cur.execute("call hire_doctor(\'%s\',\'%s\', \'%s\', NULL,\'%s\', \'%s\', %.2f)" % (id, name, contact, email, address, float(salary)))
            elif designation == "Nurse":
                cur.execute("call hire_nurse(\'%s\',\'%s\', \'%s\', \'%s\', \'%s\', %.2f)" % (id, name, contact, email, address, float(salary)))
            else:
                curr.execute("call hire_management(\'%s\',\'%s\', \'%s\', \'%s\', \'%s\', %.2f)" % (id, name, contact, email, address, float(salary)))


        mysql.connection.commit()
        cur.close()
        return redirect(url_for('success'))

    return render_template('employee_registration.html')


@app.route('/delete', methods=['GET', 'POST'])
def employee_deletion():
    if request.method == 'POST':
        info = request.form['info']
        eid = info.split(' ')[0]
        designation = info.split(' ')[-1]
        print(eid)
        cur = mysql.connection.cursor()
        eids = cur.execute("SELECT id FROM employees")
        eids = cur.fetchall()
        # checking for invalid deletion
        eid = (eid,)
        if eid not in eids:
            return ('<h2>Employee with this ID doesnot exists. Please enter valid ID.</h2>')
        else:
            if designation == "(Doctor,)":
                cur.execute("DELETE FROM appointments WHERE doctor_ID = \'{}\'".format(eid[0]))
                cur.execute("UPDATE patients SET doctors = NULL WHERE doctors = \'{}\'".format(eid[0]))
                cur.execute("DELETE FROM doctors WHERE id = \'{}\'".format(eid[0]))
            # elif designation == "(Nurse,)":
            #     cur.execute("DELETE FROM nurses WHERE id = \'{}\'".format(eid[0]))
            # else:
            #     cur.execute("DELETE FROM management_staff WHERE id = \'{}\'".format(eid[0]))

            cur.execute("DELETE FROM management_staff WHERE id = \'{}\'".format(eid[0]))
            cur.execute("DELETE FROM nurses WHERE id = \'{}\'".format(eid[0]))
            cur.execute("DELETE FROM employees WHERE id = \'{}\'".format(eid[0]))
            mysql.connection.commit()
            cur.close()
            return render_template('deleted_successfully.html', info = info)

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, designation FROM employees")
    employees_info = cur.fetchall()
    return render_template('employee_deletion.html', employees_info=employees_info)


@app.route('/success', methods=['GET', 'POST'])
def success():
    return render_template("employee_registered.html")

# Patient Portal Functionality
@app.route('/patients')
def patients():
    cur = mysql.connection.cursor()
    patients = cur.execute("SELECT * from Patients where discharged = '0'")

    if patients > 0:
        patients_info = cur.fetchall()
        return render_template('patients.html', patients_info=patients_info)

    return ("<h2>No patient entry in the database</h2>")

@app.route('/patient_reg_main')
def patient_reg_main():
    return render_template('patient_main_reg.html')

@app.route('/already_reg', methods = ['GET', 'POST'])
def already_registered():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        pids = cur.execute("SELECT patient_ID FROM patients")
        pids = cur.fetchall()
        id = request.form['id']
        p_id = (id, )
        if p_id not in pids:
            return ('<h2>patient with this ID doesnot exists. Please enter valid patient ID.</h2>')
        else:
            cur.execute("UPDATE patients set discharged = '0', doctors = NULL, room = NULL, medicine = NULL where patient_ID = \'%s\'"%(id))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('patient_success'))
    return render_template('already_registered.html')

@app.route('/patient_reg', methods = ['GET', 'POST'])
def patient_registration():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        pids = cur.execute("SELECT patient_ID FROM patients")
        pids = cur.fetchall()
        id = request.form['id']
        p_id = (id, )
        name = request.form['name']
        contact = request.form['contact']
        dob =  request.form['dob']
        address = request.form['address']
        if p_id in pids:
            return render_template("patient_already_exists.html", id = id)
        else:
            cur.execute("call new_patient(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')" % (id, name, dob, contact, address))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('patient_success'))

    return render_template("patient_registration.html")


@app.route('/book_appointment', methods = ['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        p_ID = request.form['p_ID']
        d_ID = request.form['d_ID']
        time_slot = request.form['time_slot']
        cur = mysql.connection.cursor()
        pids = cur.execute("SELECT patient_ID FROM patients WHERE discharged = '0'")
        pids = cur.fetchall()
        dids = cur.execute("SELECT id FROM doctors")
        dids = cur.fetchall()
        apids = cur.execute("SELECT patient_ID FROM appointments")
        apids = cur.fetchall()
        pID = (p_ID, )
        dID = (d_ID, )
        status = 2;
        if pID not in pids or dID not in dids:
            status = 0
            return render_template('appointment_result.html', status = status, p_ID = p_ID)
        elif pID in apids:
            status = 1
            return render_template('appointment_result.html', status = status, p_ID = p_ID)
        else:
            cur.execute("INSERT INTO appointments VALUES ('%s', '%s', '%s')"% (p_ID, d_ID, time_slot))
            mysql.connection.commit()
            cur.close()
            return render_template('appointment_result.html', status = status, p_ID = p_ID)

    return render_template('book_appointment.html')


@app.route('/appointments')
def appointments():
    cur = mysql.connection.cursor()
    appointments = cur.execute("SELECT * FROM appointment_details")
    if appointments > 0:
        appointment_info = cur.fetchall()
        return render_template('appointments.html', appointment_info = appointment_info)

    return ("<h2>No appointment entry in the database</h2>")


@app.route('/patient_success', methods = ['GET', 'POST'])
def patient_success():
    return render_template("patient_registered.html")

@app.route('/patient-index')
def patient_index():
    return render_template('patient_index.html')




if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
