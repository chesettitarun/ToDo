from flask import Flask, render_template,request,flash,redirect,url_for,session
import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
app = Flask(__name__)
app.secret_key="123"

con=sqlite3.connect("database.db")
with open('schema.sql') as f:
    con.executescript(f.read())
cur = con.cursor()
con.close()

con2=sqlite3.connect("database.db")
with open('todo.sql') as h:
    con2.executescript(h.read())
cur2=con2.cursor()
con2.close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select password from customer where name=?",(name,))
        data=cur.fetchone()
        print(data)
        if data:
            if check_password_hash(data[0],password):
                session["name"]=name
                session["password"]=data[0]
                return redirect('/todo')
            else:
                flash("Invalid username or password","danger")
        else:
            flash("Username doesn't exist","danger")
    return redirect(url_for("index"))
               


@app.route('/todo',methods=["GET","POST"])
def tasks_list():
        con2=sqlite3.connect("database.db")
        con2.row_factory=sqlite3.Row
        cur2=con2.cursor()

        cur2.execute("select * from tasks where user=?",(session["name"],))
        tasks = cur2.fetchall()
        con2.commit()
        cur2.close()
        con2.close()
        return render_template('todo.html', tasks=tasks)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            name=request.form['name']
            password=request.form['password']
           
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            password=generate_password_hash(password, method='sha256')
            cur.execute("select name from customer where name=name")
            data =cur.fetchall()
            print(data)
            for row in data:
                if row[0]==name:
                    flash('User with this name already exists.',"danger")
                    return redirect(url_for("index"))
             
            cur.execute("insert into customer(name,password)values(?,?)",(name,password))
            con.commit()
            cur.close()
            con.close()
            flash("Account created  Successfully","success")
            return redirect(url_for("index"))
        except:
            flash("Error in Insert Operation","danger")

    return render_template('register.html')

@app.route('/task', methods=['POST'])
def add_task():
    con2=sqlite3.connect("database.db")
    con2.row_factory=sqlite3.Row
    cur2=con2.cursor()
    content = request.form['content']
    cur2.execute("insert into tasks(user,content,done)values(?,?,?)",(session["name"],content,False))
    session['content'] = content
    cur2.execute("select * from tasks where user=?",(session["name"],))
    tasks =cur2.fetchall()
    con2.commit()
    cur2.close()
    con2.close()
    return render_template('todo.html', tasks=tasks)


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    con2=sqlite3.connect("database.db")
    con2.row_factory=sqlite3.Row
    cur2=con2.cursor()
    # session.delete(, None)
    cur2.execute("delete from tasks where pid=?and user=?",(task_id,session["name"]))
    con2.commit()
    # cur2.execute("select * from tasks")
    # task = cur2.fetchall()
    #print (task)
    cur2.close()
    con2.close()
    return redirect('/todo')

    
    


@app.route('/done/<int:task_id>')
def resolve_task(task_id):
    con2=sqlite3.connect("database.db")
    con2.row_factory=sqlite3.Row
    cur2=con2.cursor()
    cur2.execute("select done from tasks where pid=? and user=?",(task_id,session["name"]))
    task = cur2.fetchone()
    if not task:
        return redirect(url_for("todo"))
    else:
        if not task[0]:
            cur2.execute("update tasks set done=? where pid=? and user=?",(True,task_id,session["name"]))
    con2.commit()
    cur2.close()
    con2.close()
    return redirect('/todo')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
