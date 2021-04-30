from flask import Flask, render_template, redirect, url_for, request
from flask_mysqldb import MySQL

app = Flask(__name__)

# Database confirgurations
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
# Add your root password below
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "hospital"

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employees')
def employees():
    cur = mysql.connection.cursor()
    employees = cur.execute("SELECT * from Employees")

    if employees > 0:
        employee_info = cur.fetchall()
        return render_template('employee.html', employee_info=employee_info)

    return ("<h2>No employee entry in the database</h2>")

@app.route('/patients')
def patients():
    cur = mysql.connection.cursor()
    patients = cur.execute("SELECT * from Patients")

    if patients > 0:
        patients_info = cur.fetchall()
        return render_template('patients.html', patients_info=patients_info)

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
        # employees = cur.execute("SELECT id from Employees").fetchall()
        #
        # if id in employees[0]:
        #     return ('<h2>Employee with this ID already exists. Try with another ID.</h2>')

        cur.execute("INSERT INTO employees (id, name, contact, designation, email, address, salary) VALUES (%s, %s, %d, %s, %s, %s, %s, %d)",(id, name, contact, designation, email, address, salary))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('success'))

    return render_template('employee_registration.html')

@app.route('/success')
def success():
    return render_template('employee_registered.html')


if __name__ == '__main__':
    app.run(debug=True)
