import re
from flask import Flask, render_template, make_response, request, redirect, flash,session
from sqlalchemy import values
from moattvpkg import app, db
import datetime

    

@app.route('/')
def moattv():
    return render_template('moattvhome.html')

@app.route('/moattvsignup')
def moatsignup():
    return render_template('customersignup.html')

@app.route('/moattvlogin')
def moattvlogin():
    return render_template('customerlogin.html')

@app.route('/moatsubmitted', methods=['POST'])
def moatsubmitted():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('pswd1')
    password2 = request.form.get('pswd2')
    
    rsp = db.session.execute(f"SELECT email FROM customers WHERE email='{email}';")
    checkemail= rsp.fetchmany()
    checkemail = str(checkemail)

    
    if password.startswith("'") or password.endswith("'") or password.startswith('"') or password.endswith('"'):
        flash('Oops, The email provided is invalid.',category='email2')
        return redirect('/moattvsignup')
        

    elif email == checkemail[3:-4]:
        flash('Oops, signup unsuccessful, please try again.',category='email')
        return redirect('/moattvsignup')

    elif re.search('^\D([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+',email) and re.search('^\D[A-Z|a-z]{2,25}',firstname) and re.search('^\D[A-Z|a-z]{2,25}',lastname) and re.search('[A-Z|a-z|0-9]{5,25}',password) and password == password2:
        db.session.execute(f"INSERT INTO customers SET firstname='{firstname}', lastname='{lastname}',email='{email}',phone='{phone}',password='{password}'")
        db.session.commit()
        flash('You have signed up successfully',category='success')
        return redirect('/moattvlogin')
    else:
        flash('Sign up was unsuccessful, please fill in the your details correctly',category='incorrect')
        return redirect('/moattvsignup')

@app.route('/moattvcustomerprofile')
def moattvcustomerprofile():
    return render_template('customerprofile.html')

@app.route("/moatsubmittedlogin", methods = ['POST'])
def moatsubmittedlogin():
    email = request.form.get('email')
    password = request.form.get('pswd1')

    if email == '' or password == '' or re.search("^(\d|')(')$",email) or re.search("^(')(')$", password) or password.startswith("'") or password.endswith("'") or password.startswith('"') or password.endswith('"'):
        flash('Invalid Credentials', category='error')
        return redirect('/moattvlogin')
    else:
        rsp = db.session.execute(f"SELECT firstname FROM customers WHERE email='{email}' and password='{password}'")
        x=rsp.fetchmany()

    if len(x) == 0:
        flash('Invalid Credentials', category='error')
        return redirect('/moattvlogin')
    else:
        x=str(x)
        session['user'] = x[3:-4]
        session['email'] = email
        return redirect('/moattvcustomerprofile')
    


@app.route('/report')
def moatadminreport():
    data = db.session.execute('SELECT customers.firstname as Firstname, customers.lastname as Lastname, customers.email as email, customers.phone as Phone, customercases.complaint as Comment, customercases.case_type as Subject, dept.dept_name as department,customercases.date FROM customers INNER JOIN customercases ON customers.customerid = customercases.customerid INNER JOIN dept ON customercases.deptid = dept.dept_id;')


    admin = data.fetchmany(10)
    admins = admin

    return render_template('moattvadmin.html', admins=admins)
   
   

@app.route('/moattvprofile')
def moatcustomer():
    return render_template('customerprofile.html')

@app.route('/moatsubmittedcomplaint',methods=['POST'])
def moatsubmittedcomplaint():
    myform = request.form.to_dict(flat=False)
    case = myform.get('case')
    department = myform.get('department')
    comments = myform.get('comments')
    email = session['email']

    
    rsp = db.session.execute(f"SELECT customerid FROM customers WHERE email='{email}'")
    myid=rsp.fetchmany()
    myid = str(myid)
    myid=myid[2:-3]

    rsp = db.session.execute(f"SELECT dept_id FROM dept WHERE dept_name='{department[0]}'")
    dep=rsp.fetchmany()
    dep = str(dep)
    dep=dep[2:-3]

    if dep == '' or comments[0] == '' or case[0] == '':
        flash('Please ensure all fields are filled out before you submit your message', category='error')
        return redirect('/moattvcustomerprofile')
    else:    
        db.session.execute(f"INSERT INTO customercases SET customerid='{myid}', deptid='{dep}', complaint='{comments[0]}',case_type='{case[0].upper()}'")
        db.session.commit()
        flash('Your message has been sent successfully, thank you for your feedback')
        return redirect('/moattvcustomerprofile')
    

@app.route("/moattvlogout")
def maottvlogout():
    session.pop("email",None)
    session.pop('user', None)
    return redirect('/')