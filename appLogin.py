from flask import Flask, flash, redirect, url_for
from flask import render_template
from flask import request
from flask import make_response
from flask import session
from flask_mysqldb import MySQL
from datetime import date
import forms
import requests

app = Flask(__name__)#nuevo objeto,

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskschema'

mysql = MySQL(app)
app.secret_key='mysecretkey'
casa=0
def sql_Query(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    Answer = cur.fetchall()
    cur.close()
    return Answer

def guardar(valor):
    
    if type(valor)=='int':
        casa=valor


@app.route('/', methods = ['GET','POST'])#wrap o un decorador
def main():
    if 'name' in session:
         return render_template('index.html')
    else:
         return render_template('ingresar.html')

@app.route('/inicio', methods = ['GET','POST'])#wrap o un decorador
def inicio():
    if 'name' in session:

        
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM type_tech')

        data = cur.fetchall()
        cur.close()

        print(date)
        
        return render_template('index.html', categorias=data )
         
    else:
        return render_template('ingresar.html')


@app.route('/registrar', methods = ['GET','POST'])#wrap o un decorador
def registrar():
    if (request.method=="GET"):
        if 'name' in session:
            return render_template('inicio.html')
        else:
            return render_template('ingresar.html')
    else:
        name = request.form['nmNombreRegistro']
        email = request.form['nmCorreoRegistro']
        password = request.form['nmPasswordRegistro']

        sQuery = "INSERT into user(email, password, name) VALUES ( %s, %s, %s)"

        #crea cursor para ejecucion
        cur = mysql.connection.cursor()

        cur.execute(sQuery,(email,password,name))

        mysql.connection.commit()

        session['name']=name
        session['email']=email

        return redirect(url_for('inicio'))

@app.route('/ingresar', methods = ['GET','POST'])#wrap o un decorador
def ingresar():
    if (request.method=="GET"):
        if 'name' in session:
            return render_template('inicio.html')
        else:
            return render_template('ingresar.html')
    else:
        email = request.form['nmCorreoLogin']
        password = request.form['nmPasswordLogin']
        
        cur = mysql.connection.cursor()
        sQuery = "SELECT email, password, name FROM user WHERE email=%s"

        #crea cursor para ejecucion
        cur.execute(sQuery,[email])

        user = cur.fetchone()

        cur.close()

        if(user !=None ) :

            session['name'] = user[2]
            session['correo'] = user[0]
            
            return redirect(url_for('inicio'))
        else:
            return redirect(url_for('ingresar'))


@app.route('/type_tech/<name>', methods = ['GET','POST'])#wrap o un decorador
def categoria(name):

    if len(name.split('-'))==1:
        idPorParametro='sin servicio'
    else:
        idPorParametro=name.split('-')[1]

    r = requests.get('http://apilayer.net/api/live?access_key=03b658795166b9f77f7d648c6b78d32b&currencies=COP&source=USD&format=1')
    json=r.json()
    CAMBIO=3800 #json['quotes']['USDCOP']
    float(CAMBIO)
    cur = mysql.connection.cursor()
    Pregunta= "SELECT * FROM tech INNER JOIN type_tech ON tech.id_type_tech=type_tech.id_type_tech WHERE type_tech.name='{}'".format(name.split('-')[0])     
    cur.execute(Pregunta)
    dato = cur.fetchall()
    cur.close()
   
    if idPorParametro !='sin servicio':

        row=[]
        row2=[]
        vector=[]
        matriz=[]
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_tech FROM tech_cart WHERE id_shopping_cart=%s",[idPorParametro])

        while True:
            
            row=cur.fetchone()
            if row:
                vector.append(row[0])
            else:
                break
        
        for i in range(len(vector)):
            ur = mysql.connection.cursor()
            cur.execute("SELECT * FROM tech WHERE id_tech=%s",[vector[i]])
            row2=cur.fetchone()
            matriz.append(row2)
    else:

        matriz=[(0,'Lista Vacia',0,0,'')]
    
   
    return render_template('categoria.html', productos=dato, cambio=CAMBIO, comidas=matriz)


@app.route('/comprar/<id>/<email>', methods = ['GET','POST'])#wrap o un decorador
def comprar(id,email):
    termina=0

    '''cur = mysql.connection.cursor()
    #crea cursor para ejecucion
    cur.execute("SELECT id_user FROM user WHERE email=%s",[email])
    user = cur.fetchone()
    cur.close()'''
    user=sql_Query("SELECT id_user FROM user WHERE email='{}'".format(email))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id_shopping_cart FROM shopping_cart WHERE id_user=%s and send=%s",[user[0],termina])
    IdCarrito = cur.fetchone()
    cur.close()
    
    if IdCarrito==None:
    
        cur = mysql.connection.cursor()
        cur.execute("INSERT into shopping_cart(id_user, dateup, send) VALUES ( %s, %s, %s)",[user[0],date.today,termina])
        mysql.connection.commit()

        cur = mysql.connection.cursor()
        cur.execute("SELECT id_shopping_cart FROM shopping_cart WHERE id_user=%s",[user[0]])
        IdCarrito = cur.fetchone()
        cur.close()  
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT into tech_cart(id_shopping_cart, id_tech) VALUES ( %s, %s)",[IdCarrito[0],id])
    mysql.connection.commit()
    cur.close()

    cur = mysql.connection.cursor()
    Pregunta= "SELECT type_tech.name FROM type_tech INNER JOIN tech ON type_tech.id_type_tech=tech.id_type_tech WHERE tech.id_tech='" + id +"'"
    cur.execute(Pregunta)
    dato = cur.fetchone()
    cur.close()
    
    return  redirect("/type_tech/{}-{}".format(dato[0],IdCarrito[0])) 

@app.route('/salir', methods = ['GET','POST'])#wrap o un decorador
def salir():

    session.clear()

    return redirect(url_for('ingresar'))


if __name__ == '__main__':
    app.run(debug=True)

       

