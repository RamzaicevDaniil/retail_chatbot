import sqlite3
conn = sqlite3.connect('example.db')

c = conn.cursor()

#USERS
#Create table user
# c.execute('''CREATE TABLE user
# (email, password)''')
c.execute('''CREATE TABLE user (user_email, user_password, user_first_name, user_last_name, user_birth_date, user_phone_number)''')
#Insert a row a data
users = [
('example@rasa.com', '123', 'Sus', 'Aboba', '1999-12-12', '987239857'),
('example1@rasa.com', '345', 'Sus', 'Amogus', '1998-12-12', '987239853247'),
('example123@rasa.com', '345', 'Amomogus', 'Amogus', '1997-12-12', '9872325359857'),
]

c.executemany('INSERT INTO user (user_email, user_password, user_first_name, user_last_name, user_birth_date, user_phone_number) VALUES (?, ?, ?, ?, ?, ?)', users)

# EXISTING ORDERS
# Create table
c.execute('''CREATE TABLE orders
(order_date, order_number, order_email, color, size, status)''')



# data to be added
purchases = [('2006-01-05',123456,'example@rasa.com','blue', 9, 'shipped'),
('2021-01-05',123457,'me@rasa.com','black', 10, 'order pending'),
('2021-01-05',123458,'me@gmail.com','gray', 11, 'delivered'),
]

# add data
c.executemany('INSERT INTO orders VALUES (?,?,?,?,?,?)', purchases)

# AVAILABLE INVENTORY
# Create table
c.execute('''CREATE TABLE inventory
(size, color)''')

# data to be added
inventory = [(7, 'blue'),
(8, 'blue'),
(9, 'blue'),
(10, 'blue'),
(11, 'blue'),
(12, 'blue'),
(7, 'black'),
(8, 'black'),
(9, 'black'),
(10, 'black'),
(123, 'black')
]

# add data
c.executemany('INSERT INTO inventory VALUES (?,?)', inventory)


# Save (commit) the changes
conn.commit()

# end connection
conn.close()