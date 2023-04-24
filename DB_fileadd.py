# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 18:40:18 2023

@author: kpava
"""

import psycopg2
import csv


#Cloud Database connection
DB_HOST = "floppy.db.elephantsql.com"
DB_NAME = "tjkicypl"
DB_USER = "tjkicypl"
DB_PASS = "dZ6SKvQZZZKOGm5zyfhCwa_R4jbDTZ3O"

# Connecting postgresql database to the python
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)

print("CONNECTED SUCCESSFULLY")

# Open the CSV file and read the data
with open(r'C:\Users\kpava\Downloads\plp_3_platforms_2023_04_18_AmazonPLP_Output_batch_1.csv', 'r',encoding='iso-8859-1') as file:
    reader = csv.reader(file)
    next(reader) # Skip the header row
    rows = [row for row in reader]

# Create a cursor object to execute SQL queries
cur = conn.cursor()

# Define the SQL query to insert the data into the table
query = '''INSERT INTO productdetails (productname , productdescrb , imgurl , productprice , category,addedby)  VALUES (%s , %s , %s, %s , %s,%s)'''

# Execute the SQL query for each row of data
for row in rows:
    cur.execute(query, row)

# Commit the changes to the database
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
