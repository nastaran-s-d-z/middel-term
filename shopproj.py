import re
import tkinter as tk
import sqlite3
import re
from itertools import product
from logging import disable
from pstats import Stats
import json
from tkinter import mainloop

from pyexpat.errors import messages

#--------------- connect to database -----------
cnt=sqlite3.connect('myshop.db')
#
# sql='''CREATE TABLE products(
#     id  INTEGER PRIMARY KEY,
#     name VARCHAR(40) NOT NULL,
#     price INTEGER NOT NULL,
#     quantity INTEGER NOT NULL
# )'''
# cnt.execute(sql)

# sql=''' INSERT INTO products (name,price,quantity)
#     VALUES("Del Laptop model C0021",21000,160)
#    '''
# cnt.execute(sql)
# cnt.commit()

# sql='''CREATE TABLE cart(
#      id  INTEGER PRIMARY KEY,
#    pid INTEGER NOT NULL,
#      uid INTEGER NOT NULL,
#     number INTEGER NOT NULL
#  )'''
# cnt.execute(sql)


# with open("Settings.json","w") as f:
#   json.dump({"usergaradebase":[2000],"usersettings":{"0":{"shop":0,"my cart":0},"5":{"shop":1,"my cart":0},"10":{"shop":1,"my cart":1}}},f)
#----------------functions-------------------
def readjson():
    try:
        with open("Settings.json", "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def getusers1():
    Settings = readjson()
    ID = getID(txtUser.get())
    sql = f'''SELECT grade FROM users WHERE id={ID}'''
    result = ((cnt.execute(sql)).fetchall())[0][0]
    for k, v in sorted(Settings["usersettings"].items(), key=lambda x: int(x[0]), reverse=True):
        if result >= int(k):
            return v["shop"], v["my cart"]

    return 0, 0


def checkLogin(user,pas):
    sql=f'''SELECT * FROM users WHERE username="{user}" AND password="{pas}" '''
    result=cnt.execute(sql)
    rows=result.fetchall()
    if len(rows)<1:
        return False
    else:
        return True
def login():
        global session
        user, pas = txtUser.get(), txtPass.get()
        try:
            if checkLogin(user, pas):
                session = user
                lblMsg.configure(text='Welcome to your account!', fg='green')
                for widget in (txtUser, txtPass, btnLogin, btnSignup):
                    widget.configure(state='disabled')
                if user != "admin":
                    a, b = getusers1()
                    if a == 1:
                        tk.Button(win, text='Shop Panel', command=shopPanel).pack()
                    if b == 1:
                        tk.Button(win, text="My Cart", command=mycart).pack()
                if user == "admin":
                    tk.Button(win, text="Users Setting", command=Userssettings).pack(pady=5)
                    tk.Button(win, text="Products Setting", command=Productssettings).pack(pady=5)
                    tk.Button(win, text="Add Product", command=insertnewproducts).pack(pady=5)
                    grade_counting_box(win)
            else:
                lblMsg.configure(text='Wrong username or password!', fg='red')
        except Exception as e:
            lblMsg.configure(text='An error occurred: {}'.format(str(e)), fg='red')
def grade_counting_box(win):
        global gradebox
        tk.Label(win, text="Set user grade counting base (Leave empty if you don't want to change.):").pack()
        SGCB = tk.Entry(win)
        SGCB.pack()
        tk.Button(win, text="Set", command=lambda: update_user_grade_base(SGCB, win)).pack()
        gradebox = tk.Label(win, text=f"{readjson()}")
        gradebox.pack()

def signup():
    def signupValidate(user,pas,cpas,addr):
        if user=='' or pas=='' or cpas=='' or addr=='':
            return False,'empty fileds error!'
        if pas!=cpas:
            return False,'password and confiration mismatch!'
        if len(pas)<8:
            return False,'password length at least 8 chars!'

        sql=f'''SELECT * FROM users WHERE username="{user}" '''
        result=cnt.execute(sql)
        rows=result.fetchall()
        if len(rows)>0:
            return False,'username already exist!'
        reg=r"?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$"
        if not(re.match(reg,pas)):
            return False,'not ok'
        return True,''


        return True,''
    def save2users(user,pas,addr):

        try:
            sql=f'''INSERT INTO users (username,password,address,grade)
                    VALUES ("{user}","{pas}","{addr}",0)'''
            cnt.execute(sql)
            cnt.commit()
            return True
        except:
            return False
from tkinter import messagebox
def mycart():
    def ok():
        winMycart.destroy()
    DCT = {}

    user_input = txtUser.get()
    ID = getID(user_input)

    if ID is None:
        messagebox.showerror("User Not Found", "No user found with the provided ID.")
        return

    sql = f'''SELECT c.pid, c.number, p.name FROM cart c 
              JOIN products p ON c.pid = p.id 
              WHERE c.uid = {ID}'''
    lst = cnt.execute(sql).fetchall()
    for item in lst:
        pid = str(item[0])
        number = item[1]
        product_name = item[2]
        if pid in DCT:
            DCT[pid]['quantity'] += number
        else:
            DCT[pid] = {'name': product_name, 'quantity': number}

    winMycart = tk.Toplevel(win)
    winMycart.title("My Cart:")
    winMycart.geometry("500x500")
    listbox = tk.Listbox(winMycart, width=50, height=15)
    listbox.pack(pady=10)

    for data in DCT.values():
        listbox.insert(tk.END, f"{data['name']}{data['quantity']}")
    tk.Button(winMycart, text="Ok", command=ok).pack(pady=10)
    winMycart.mainloop()


def show_error_message(message, win):
    error_win = tk.Toplevel(win)
    error_win.title("Error")
    error_win.geometry("200x150")
    tk.Label(error_win, text=message).pack(pady=20)


    def close_error_win():
        error_win.destroy()

    btnOk = tk.Button(error_win, text="Ok", command=close_error_win)
    btnOk.pack(pady=10)

    error_win.mainloop()

def update_user_grade_base(SGCB, win):
    sgcb_value = SGCB.get()
    if sgcb_value == "":
        show_error_message("Empty Field!", win)
        return

    try:
        sgcb = int(sgcb_value)
        if sgcb <= 0:
            raise ValueError("Grade must be greater than 0.")
        else:
            dct = readjson()
            dct["usergaradebase"] = [sgcb]
            with open("Settings.json", "w") as f:
                json.dump(dct, f)
            gradebox.configure(text=f"{readjson()}")


    except ValueError as e:
        show_error_message(f"Invalid Input: {e}", win)

    def getID(user):
        sql = f'''SELECT id FROM users WHERE username="{user}"'''
        result = cnt.execute(sql)
        rows = result.fetchall()
        return rows[0][0] if rows else None

    def submit():
        user=txtUser2.get()
        pas=txtPass2.get()
        cpas=txtcPass2.get()
        addr=txtaddr.get()
        result,errormsg=signup(user,pas,cpas,addr)
        if not result:
            lblMsg2.configure(text=errormsg,fg="red")
            return
        result (user,pas,addr)
        if not result:
            lblMsg2.configure(text='error while connecting database!!',fg='red')
            return
        lblMsg2.configure(text='Submit done successfully!',fg='green')
        txtUser2.delete(0,'end')
        txtPass2.delete(0,'end')
        txtcPass2.delete(0,'end')
        txtaddr.delete(0,'end')
    winSignup=tk.Toplevel(win)
    winSignup.title('Signup Panel')
    winSignup.geometry('300x300')

    lblUser2 = tk.Label(winSignup, text='Username: ')
    lblUser2.pack()
    txtUser2 = tk.Entry(winSignup)
    txtUser2.pack()

    lblPass2 = tk.Label(winSignup, text='Password: ')
    lblPass2.pack()
    txtPass2 = tk.Entry(winSignup, show='*')
    txtPass2.pack()

    lblcPass2 = tk.Label(winSignup, text='Password confirmation: ')
    lblcPass2.pack()
    txtcPass2 = tk.Entry(winSignup, show='*')
    txtcPass2.pack()

    lbladdr = tk.Label(winSignup, text='Address: ')
    lbladdr.pack()
    txtaddr = tk.Entry(winSignup)
    txtaddr.pack()

    lblMsg2 = tk.Label(winSignup, text='')
    lblMsg2.pack()

    btnSubmit = tk.Button(winSignup, text='Submit', command=submit)
    btnSubmit.pack()

    winSignup.mainloop()
def getProdocts():
    sql='''SELECT * FROM products'''
    result=cnt.execute(sql)
    products=result.fetchall()
    return products
def getID(user):
    sql=f''' SELECT id FROM users WHERE username='{user}' '''
    result=cnt.execute(sql)
    return result.fetchall()[0][0]
def updateQNT(pid,number):
    sql=f''' UPDATE products SET quantity=quantity-{int(number)} WHERE id={int(pid)}'''
    cnt.execute(sql)
    cnt.commit()


def shopPanel():
    def shopValidate(pid,pnumber):
        if not(pid.isdigit()) or not (pnumber.isdigit()):
            return False,'Invalid input'
        #     ---
        sql=f'''SELECT * FROM products WHERE id={int(pid)}'''
        result=cnt.execute(sql)
        products=result.fetchall()
        if len (products)<1:
            return False,'wrong product id'
        # ----
        sql=f''' SELECT *FROM products WHERE id={int(pid)} and quantity>={int(pnumber)}'''

        result = cnt.execute(sql)
        products = result.fetchall()
        if len(products) < 1:
            return False, 'not enough products'
        return True,''


    def save2cart():
        global  session
        pid=txtId.get()
        pnumber=txtNum.get()
        result,msg=shopValidate(pid,pnumber)
        if not result:
            lblMsg3.configure(text=msg,fg='red')
            return
        updateQNT(pid,pnumber)
        uid=getID(session)
        sql=f"INSERT INTO cart (pid,uid,number) VALUES ({int(pid)},{uid},{int(pnumber)})"

        try:
            cnt.execute(sql)
            cnt.commit()
            lblMsg3.configure(text='save to your cart',fg='green')
            txtId.delete(0,'end')
            txtNum.delete(0,'end')
            lstbox.delete(0,'end')
            products = getProdocts()
            showProducts(products)
        except:
            lblMsg3.configure(text='error while connecting database',fg='red')


    def showProducts(products):
        for product in products:
            text=f'id={product[0]}  name={product[1]}  price{product[2]}  qnt={product[3]}'
            lstbox.insert('end',text)

    winshop=tk.Toplevel(win)
    winshop.title("shop panel")
    winshop.geometry("600x400")
    lstbox=tk.Listbox(winshop,width=80)
    lstbox.pack()
    lblId=tk.Label(winshop,text='Id:')
    lblId.pack()
    txtId=tk.Entry(winshop)
    txtId.pack()

    lblNum= tk.Label(winshop, text='number:')
    lblNum.pack()
    txtNum= tk.Entry(winshop)
    txtNum.pack()
    lblMsg3=tk.Label(winshop,text='')
    lblMsg3.pack()
    btnBuy=tk.Button(winshop,text="save to cart",command=save2cart)
    btnBuy.pack(pady=8)
    products=getProdocts()
    showProducts(products)
    print(products)
    winshop.mainloop()
def getmycart(uid):
      sql=f'''SELECT products.name,products.price,cart.number
                FROM cart INNER JOIN products
                ON  cart.pid=products.id
                WHERE cart.uid={uid}
'''
      result=cnt.execute(sql)
      return result.fetchall()


def Userssettings():
    winAd = tk.Toplevel(win)
    winAd.title("Update User Info Panel")
    winAd.geometry("200x200")

    tk.Label(winAd, text="User ID:").pack()
    txtuserSet1 = tk.Entry(winAd)
    txtuserSet1.pack()

    tk.Label(winAd, text="New Username (leave empty if no change):").pack()
    txtuserSet2 = tk.Entry(winAd)
    txtuserSet2.pack()

    tk.Label(winAd, text="New Password (leave empty if no change):").pack()
    txtuserSet3 = tk.Entry(winAd, show='*')
    txtuserSet3.pack()

    tk.Label(winAd, text="New Address (leave empty if no change):").pack()
    txtuserSet4 = tk.Entry(winAd)
    txtuserSet4.pack()

    tk.Label(winAd, text="New Grade (leave empty if no change):").pack()
    txtuserSet5 = tk.Entry(winAd)
    txtuserSet5.pack()

    lblMssg = tk.Label(winAd, text="")
    lblMssg.pack()

    def userinfoprocessing():
        global textuserSet1, original_values
        textuserSet1 = txtuserSet1.get()
        if not textuserSet1:
            lblMssg.configure(text="Please enter a User ID!", fg="red")
            return

        try:
            sql = f'SELECT username, password, address, grade FROM users WHERE id={int(textuserSet1)}'
            result = cnt.execute(sql)
            lst = result.fetchall()
            if not lst:
                lblMssg.configure(text="ID not found!", fg="red")
                return

            original_values = dict(zip(["username", "password", "address", "grade"], lst[0]))
            lblMssg.configure(text=f"User's Username is {original_values['username']}.", fg="green")
            new_username = txtuserSet2.get()
            new_password = txtuserSet3.get()
            new_address = txtuserSet4.get()

            try:
                new_grade = int(txtuserSet5.get()) if txtuserSet5.get() else None
            except ValueError:
                new_grade = None

            if new_username and new_username != original_values["username"]:
                existing_user_id = getID(new_username)
                if existing_user_id:
                    lblMssg.configure(text=" Please choose another one.", fg="red")
                    return

            if (new_username == original_values["username"] or new_username == "") and \
                    (new_password == original_values["password"] or new_password == "") and \
                    (new_address == original_values["address"] or new_address == "") and \
                    (new_grade == original_values["grade"] or new_grade is None):
                winWrong = tk.Toplevel(winAd)
                winWrong.geometry("300x300")
                winWrong.title("Something went wrong!")
                tk.Label(winWrong, text="No Alteration! Please change at least one property!").pack()
                tk.Button(winWrong, text="OK", command=winWrong.destroy).pack()
            elif (new_username == original_values["username"]) or \
                    (new_password == original_values["password"]) or \
                    (new_address == original_values["address"]) or \
                    (new_grade == original_values["grade"]):
                winWrong = tk.Toplevel(winAd)
                winWrong.geometry("300x300")
                winWrong.title("Something went wrong!")
                tk.Label(winWrong, text="Leave empty if you don't want to change!").pack()
                tk.Button(winWrong, text="OK", command=winWrong.destroy).pack()

            else:
                global winConfirmupdate
                winConfirmupdate = tk.Toplevel(winAd)
                winConfirmupdate.geometry("200x300")
                winConfirmupdate.title("Confirm Panel")
                tk.Label(winConfirmupdate, text=f"User's Username is ({original_values["username"]}.)\nAre you sure \nthis User's Info?").pack()
                tk.Button(winConfirmupdate, text="Yes", command=userinfoupdate).pack()
                tk.Button(winConfirmupdate, text="No", command=winConfirmupdate.destroy).pack()

        except Exception as e:
            lblMssg.configure(text=f"Error fetching user info: {e}", fg="red")

    def userinfoupdate():
        try:
            updates = {
                "username": txtuserSet2.get(),
                "password": txtuserSet3.get(),
                "address": txtuserSet4.get(),
            }
            grade = int(txtuserSet5.get())
            for column, new_value in updates.items():
                if new_value and new_value != original_values[column]:
                    sql = f'UPDATE users SET {column}="{new_value}" WHERE id={int(textuserSet1)}'
                    cnt.execute(sql)

            sql = f'UPDATE users SET grade={grade} WHERE id={int(textuserSet1)}'
            cnt.execute(sql)
            cnt.commit()

            winConfirmupdate.destroy()

        except Exception as e:
            lblMssg.configure(text=f"Error updating user info: {e}", fg="red")

    def deleteuseraccount():
        textuserSet1 = txtuserSet1.get()
        sql=f'''SELECT username FROM users WHERE id={int(textuserSet1)}'''
        US=((cnt.execute(sql)).fetchall())[0][0]

        def confirm_delete():
            try:
                sql = f'''DELETE FROM users WHERE id={int(textuserSet1)}'''
                cnt.execute(sql)
                cnt.commit()
                winCondelete.destroy()
                lblMssg.configure(text="User deleted successfully!", fg="green")
            except Exception as e:
                lblMssg.configure(text=f"Error deleting user: {e}", fg="red")

        def cancel_delete():
            winCondelete.destroy()
        global winCondelete
        winCondelete = tk.Toplevel(winAd)
        winCondelete.title("Delete Process Confirm")
        winCondelete.geometry("300x300")
        tk.Label(winCondelete, text=f"User's Id is {US}.\nAre you sure about deleting this User's Account?").pack()
        tk.Button(winCondelete, text="Yes", command=confirm_delete).pack()
        tk.Button(winCondelete, text="No", command=cancel_delete).pack()
        winCondelete.mainloop()

    tk.Button(winAd, text="Submit", command=userinfoprocessing).pack()
    tk.Button(winAd, text="Delete User's Account", command=deleteuseraccount).pack()

    winAd.mainloop()
def Productssettings():
    winAd = tk.Toplevel(win)
    winAd.title("Update Product Info Panel")
    winAd.geometry("300x300")
    tk.Label(winAd, text="Product ID:").pack()
    txtProductSet1 = tk.Entry(winAd)
    txtProductSet1.pack()

    tk.Label(winAd, text="New Price (leave empty if no change):").pack()
    txtProductSet2 = tk.Entry(winAd)
    txtProductSet2.pack()

    tk.Label(winAd, text="New Quantity (leave empty if no change):").pack()
    txtProductSet3 = tk.Entry(winAd)
    txtProductSet3.pack()

    lblMssg = tk.Label(winAd, text="")
    lblMssg.pack()

    def validate_and_convert_input():
        try:
            new_price = txtProductSet2.get()
            if new_price:
                new_price = float(new_price)
            else:
                new_price = None

            new_quantity = txtProductSet3.get()
            if new_quantity:
                new_quantity = int(new_quantity)
            else:
                new_quantity = None

            return new_price, new_quantity
        except ValueError:
            lblMssg.configure(text="Invalid input! Please enter valid numbers for Price and Quantity.", fg="red")
            return None, None


    def productInfoProcessing():
        product_id = txtProductSet1.get()

        if not product_id:
            lblMssg.configure(text="Please enter a Product ID!", fg="red")
            return

        try:
            sql = "SELECT name, price, quantity FROM products WHERE id = ?"
            result = cnt.execute(sql, (product_id,))
            lst = result.fetchall()

            if not lst:
                lblMssg.configure(text="Product ID not found!", fg="red")
                return

            original_values = dict(zip(["name", "price", "quantity"], lst[0]))
            lblMssg.configure(text=f"Product Name is {original_values['name']}.", fg="green")

            new_price, new_quantity = validate_and_convert_input()

            if new_price is None and new_quantity is None:
                return
            changes_made = False
            if new_price is not None and new_price != original_values["price"]:
                changes_made = True
            if new_quantity is not None and new_quantity != original_values["quantity"]:
                changes_made = True

            if not changes_made:
                messagebox.showinfo("No Changes", "Please change at least one field.")
            else:
                confirm_update = messagebox.askyesno("Confirm Update",
                                                     f"Product's Name is ({original_values['name']}).\nAre you sure about updating this product's info?")
                if confirm_update:
                    productInfoUpdate(new_price, new_quantity, product_id, original_values)

        except Exception as e:
            lblMssg.configure(text=f"Error fetching product info: {e}", fg="red")

    def productInfoUpdate(new_price, new_quantity, product_id, original_values):
        try:
            updates = {}
            if new_price is not None:
                updates["price"] = new_price
            if new_quantity is not None:
                updates["quantity"] = new_quantity

            for column, new_value in updates.items():
                if new_value != original_values[column]:
                    sql = f"UPDATE products SET {column} = ? WHERE id = ?"
                    cnt.execute(sql, (new_value, product_id))

            cnt.commit()
            lblMssg.configure(text="Product  updated successfully!", fg="green")
        except Exception as e:
            lblMssg.configure(text=f"Error updating product info: {e}", fg="red")
    def deleteProduct():
        product_id = txtProductSet1.get()
        sql = f"SELECT name FROM products WHERE id = ?"
        result = cnt.execute(sql, (product_id,))
        lst = result.fetchall()

        if not lst:
            lblMssg.configure(text="Product ID not found!", fg="red")
        else:
            product_name = lst[0][0]
            confirm_delete = messagebox.askyesno("Confirm Delete",
                                                 f"Product's Name is {product_name}.\nAre you sure about deleting this product?")
            if confirm_delete:
                try:
                    sql = f"DELETE FROM products WHERE id = ?"
                    cnt.execute(sql, (product_id,))
                    cnt.commit()
                    lblMssg.configure(text="Product deleted successfully!", fg="green")
                except Exception as e:
                    lblMssg.configure(text=f"Error deleting product: {e}", fg="red")
    tk.Button(winAd, text="Submit", command=productInfoProcessing).pack()
    tk.Button(winAd, text="Delete Product", command=deleteProduct).pack()


    winAd.mainloop()

def totalpayment(new_cart_items):
    global session


    try:
        grade_threshold = (readjson())["usergaradebase"][0]
    except KeyError:
        show_error_message("Error reading grade .", win)
        return

    ID = getID(session)
    if not ID:
        show_error_message("User ID not found.", win)
        return
    product_ids_new = [item[0] for item in new_cart_items]
    sql_prices_new = '''SELECT id, price FROM products WHERE id IN ({})'''.format(
        ','.join(['?'] * len(product_ids_new)))
    result_prices_new = cnt.execute(sql_prices_new, tuple(product_ids_new))
    product_prices_new = dict(result_prices_new.fetchall())
    total_new_purchase = sum(product_prices_new.get(item[0], 0) * item[1] for item in new_cart_items)
    sql_grade = '''SELECT grade FROM users WHERE username = ?'''
    result_grade = cnt.execute(sql_grade, (session,))
    grade_data = result_grade.fetchone()
    if not grade_data:
        show_error_message("not exist.", win)
        return

    grade = grade_data[0]
    new_grade = grade + int(total_new_purchase / grade_threshold)

    if new_grade > 20:
        new_grade = 20

    if new_grade != grade:
        sql_update_grade = '''UPDATE users SET grade = ? WHERE username = ?'''
        cnt.execute(sql_update_grade, (new_grade, session))
        cnt.commit()


    cnt.commit()


from tkinter import messagebox
def insertnewproducts():
    def savetoproducts():
        product_name = E1.get()
        product_price = E2.get()
        product_quantity = E3.get()
        if not product_name or not product_price or not product_quantity:
            lbl4.configure(text="cheek in fild!", fg="red")
            return
        sql = '''SELECT id FROM products WHERE name = ?'''
        RES = cnt.execute(sql, (product_name,))
        if len(RES.fetchall()) > 0:
            lbl4.configure(text="This product already exists!", fg="red")
            return
        try:
            product_price = float(product_price)
            product_quantity = int(product_quantity)
        except ValueError:
            lbl4.configure(text="Price and Quantity must be valid numbers!", fg="red")
            return
        try:
            sql = '''INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)'''
            cnt.execute(sql, (product_name, product_price, product_quantity))
            cnt.commit()
            lbl4.configure(text=" successfully!", fg="green")
            E1.delete(0, tk.END)
            E2.delete(0, tk.END)
            E3.delete(0, tk.END)

        except Exception as e:
            lbl4.configure(text=f"Error: {e}", fg="red")

    winInsertnewP = tk.Toplevel(win)
    winInsertnewP.geometry("500x500")
    winInsertnewP.title("Add New Product")

    lbl1 = tk.Label(winInsertnewP, text="Product Name:")
    lbl1.pack()
    E1 = tk.Entry(winInsertnewP)
    E1.pack()

    lbl2 = tk.Label(winInsertnewP, text="Product Price:")
    lbl2.pack()
    E2 = tk.Entry(winInsertnewP)
    E2.pack()

    lbl3 = tk.Label(winInsertnewP, text="Product Quantity:")
    lbl3.pack()
    E3 = tk.Entry(winInsertnewP)
    E3.pack()

    lbl4 = tk.Label(winInsertnewP, text="", fg="red")
    lbl4.pack()

    tk.Button(winInsertnewP, text="Add Product", command=savetoproducts).pack()

    winInsertnewP.mainloop()






def cartpanel():
    def showcart(mycart):
     for product in mycart:
        text=f''' name={product[0]}   price={product[1]}  number={mycart[2]} total={product[1]*product[2]}'''
        lstbox2.insert('end',text)
    global  session
    winCart=tk.Toplevel(win)
    winCart.title('cart panel')
    winCart.geometry('500x300')
    lstbox2=tk.Listbox(winCart,width=80)
    lstbox2.pack()
    uid=getID(session)
    mycart=getmycart(uid)
    showcart(mycart)
    winCart.mainloop()
#-------------------main---------------------
session=False

win=tk.Tk()
win.title('Main Panel')
win.geometry('400x400')

lblUser=tk.Label(win,text='Username: ')
lblUser.pack()
txtUser=tk.Entry(win)
txtUser.pack()

lblPass=tk.Label(win,text='Password: ')
lblPass.pack()
txtPass=tk.Entry(win,show='-')
txtPass.pack()

lblMsg=tk.Label(win,text='')
lblMsg.pack()

btnLogin=tk.Button(win,text='Login',command=login)
btnLogin.pack()

btnSignup=tk.Button(win,text='Signup',command=signup)
btnSignup.pack()
btnshop=tk.Button(win,text='shop panel',state='disabled',command=shopPanel)
btnshop.pack()
btncar=tk.Button(win,text='MY CART',state='disabled',command=cartpanel)
btncar.pack()
mainloop()