import streamlit as st
import mysql.connector
from PIL import Image
import io
import easyocr
import numpy as np

# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="bizcard"
)
cursor = conn.cursor()

# Function to create table if not exists
def create_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS business_cards
                      (id INT AUTO_INCREMENT PRIMARY KEY,
                       image LONGBLOB,
                       company_name VARCHAR(255),
                       card_holder_name VARCHAR(255),
                       designation VARCHAR(255),
                       mobile_number VARCHAR(20),
                       email_address VARCHAR(255),
                       website_url VARCHAR(255),
                       area VARCHAR(255),
                       city VARCHAR(255),
                       state VARCHAR(255),
                       pin_code VARCHAR(20))''')

# Function to insert data into database
def insert_data(image, company_name, card_holder_name, designation, mobile_number, email_address, website_url, area, city, state, pin_code):
    sql = '''INSERT INTO business_cards (image, company_name, card_holder_name, designation, mobile_number, email_address, website_url, area, city, state, pin_code)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    val = (image, company_name, card_holder_name, designation, mobile_number, email_address, website_url, area, city, state, pin_code)
    cursor.execute(sql, val)
    conn.commit()

# Function to display data from database
def display_data():
    cursor.execute("SELECT * FROM business_cards")
    data = cursor.fetchall()
    for entry in data:
        st.write(f"ID: {entry[0]}")
        st.write(f"Company Name: {entry[2]}")
        st.write(f"Card Holder Name: {entry[3]}")
        st.write(f"Designation: {entry[4]}")
        st.write(f"Mobile Number: {entry[5]}")
        st.write(f"Email Address: {entry[6]}")
        st.write(f"Website URL: {entry[7]}")
        st.write(f"Area: {entry[8]}")
        st.write(f"City: {entry[9]}")
        st.write(f"State: {entry[10]}")
        st.write(f"Pin Code: {entry[11]}")
        st.write("---")

# Function to delete data from database
def delete_data(id):
    sql = "DELETE FROM business_cards WHERE id = %s"
    val = (id,)
    cursor.execute(sql, val)
    conn.commit()

# Function to convert PIL image to numpy array
def pil_to_np_array(image):
    return np.array(image)

# Main function
def main():
    st.title("Business Card Information Extractor")
    st.sidebar.title("Options")

    # Upload image
    uploaded_image = st.sidebar.file_uploader("Upload Business Card Image", type=["jpg", "png", "jpeg"])

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Convert image to numpy array
        image_np = pil_to_np_array(image)

        # Perform OCR
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image_np)

        # Extract information
        company_name = ""
        card_holder_name = ""
        designation = ""
        mobile_number = ""
        email_address = ""
        website_url = ""
        area = ""
        city = ""
        state = ""
        pin_code = ""

        for detection in result:
            text = detection[1]
            if "company" in text.lower():
                company_name = text
            elif "name" in text.lower():
                card_holder_name = text
            elif "designation" in text.lower():
                designation = text
            elif "mobile" in text.lower():
                mobile_number = text
            elif "@" in text:
                email_address = text
            # Similar logic for other fields...

        # Display extracted information
        st.subheader("Extracted Information")
        st.write(f"Company Name: {company_name}")
        st.write(f"Card Holder Name: {card_holder_name}")
        st.write(f"Designation: {designation}")
        st.write(f"Mobile Number: {mobile_number}")
        st.write(f"Email Address: {email_address}")
        # Similar display for other fields...

        # Save to database
        if st.button("Save to Database"):
            image_byte_array = io.BytesIO()
            image.save(image_byte_array, format='PNG')
            image_byte_array = image_byte_array.getvalue()
            insert_data(image_byte_array, company_name, card_holder_name, designation, mobile_number, email_address, website_url, area, city, state, pin_code)

    # Display database entries
    display_data()

    # Delete data
    if st.button("Delete Entry"):
        id = st.text_input("Enter ID of entry to delete:")
        if id != "":
            delete_data(int(id))
            st.success("Entry deleted successfully!")

if __name__ == "__main__":
    create_table()
    main()