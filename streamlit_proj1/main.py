import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import json
import os
import os.path
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def load_image(image_file):
    img = Image.open(image_file)
    return img

#page layout
page_choice = st.sidebar.selectbox("Content", options=['Home', 'Upload Pet Expense'])
header_section = st.container()
download_template_section = st.container()
form_section = st.container()
expenses_section = st.container()

def main():
    template_file = pd.read_csv('data/template.csv').to_csv().encode('utf-8')
    if (page_choice == 'Home'):
        home_header_section = st.container()
        home_graph_section = st.container()
        home_breakdown_section = st.container()

        with home_header_section:
            st.title('Welcome to your pet expenses tracker!')
            st.write("""I want to be a pet lady when I'm older. One of my dreams is to take care of as many pets as I possibly can (and yes, I was
            heavily influenced by the movie 'Hotel for Dogs'). However, this can get super expensive
            and can be hard to track, especially if you have many pets with specific needs such as medications.
            To stay organized, I created my own simple pet expenses tracker to analyze my annual pets' expenses. """)
            st.write("""You can add your own pet data by navigating to the 'Upload Pet Expense' page. Then, you can come back to the home page to see
            your expenses analyses and breakdown.""")

        with home_graph_section:
            home_data = pd.read_csv('data/new_data.csv')
            home_data['Month'] = pd.DatetimeIndex(home_data['Date']).month

            graph_data = pd.DataFrame()
            graph_data['Month'] = [1,2,3,4,5,6,7,8,9,10,11,12]
            for pet in home_data['Pet'].unique():
                pet_data = home_data[home_data['Pet'] == pet]
                pet_data = pet_data.groupby('Month')['Amount'].sum()
                graph_data[pet] = pet_data
            graph_data['All'] = home_data.groupby('Month')['Amount'].sum()

            graph_data = graph_data.fillna(0)
            graph_data = graph_data.set_index('Month')
            st.header("""Your 2022 Pet Expenses """)
            st.line_chart(data=graph_data, use_container_width=True)

        with home_breakdown_section:
            st.header("""2022 Monthly Pet Expenses Breakdown""")
            month = st.selectbox('Pick a month', home_data['Month'].unique())

            for pet in home_data['Pet'].unique():
                pet_data = home_data[home_data['Pet'] == pet]
                pet_data = pet_data[pet_data['Month'] == month]
                with open('data/total_pets.json', 'r+') as f:
                    data = json.load(f)

                col1, col2 = st.columns([1,3], gap='small')
                with col1:
                    st.header(pet)
                    #check if image exists
                    file_exists = os.path.exists('data/{}.jpg'.format(pet))
                    if file_exists:
                        img = load_image('data/{}.jpg'.format(pet))
                    else:
                        img = load_image('data/default.jpg')
                    st.image(img,  use_column_width=True)
                    st.write("Gender: {}".format(data.get(pet)['gender']))
                    st.write("Birthday: {}".format(data.get(pet)['birthday']))

                with col2:
                    pet_data['Month'] = pd.DatetimeIndex(pet_data['Date']).month
                    pie_data = pet_data[pet_data['Pet'] == pet].groupby('Category')['Amount'].sum()
                    fig = go.Figure(
                        go.Pie(
                        labels = pet_data['Category'].unique(),
                        values = pie_data,
                        hoverinfo = "label+percent",
                        textinfo = "value"
                    ))
                    st.plotly_chart(fig)

    elif (page_choice == 'Upload Pet Expense'):
        with header_section:
            st.title('Upload your pet expenses')

        with download_template_section:
            st.write("""You can download this template file to input your pet's expenses in. """)
            st.download_button("Download Template File", data= template_file, file_name = "template.csv")

        with form_section:
            with st.form(key="new_pet_form", clear_on_submit=True):
                pet_name = st.text_input(label='Pet Name', value='')
                pet_gender = st.selectbox(label='Pet Gender', options=['Male', 'Female'])
                pet_birthday = st.date_input(label="Pet Birthday")
                pet_picture = st.file_uploader(label='Pet Picture', type = ['jpg', 'jpeg'])
                pet_expenses = st.file_uploader(label='Pet Expenses',type='csv', accept_multiple_files = False)
                submit_button = st.form_submit_button(label='Submit')

            if submit_button:
                if pet_name != '':
                    #save pet photo
                    if pet_picture:
                        img = load_image(pet_picture)
                        img.save('data/{}.jpg'.format(pet_name), format='jpeg')

                    #add data to data.csv
                    if pet_expenses:
                        current_data = pd.read_csv('data/new_data.csv')
                        new_data = pd.read_csv(pet_expenses)
                        final_data = pd.concat([current_data, new_data])
                        st.write("""Here's a preview of your new data""")
                        st.write(final_data)
                        final_data.to_csv('data/new_data.csv', index=False)

                        with open('data/total_pets.json', 'r+') as f:
                            data = json.load(f)
                            data[pet_name] = {'gender': pet_gender, 'birthday':str(pet_birthday)}
                        with open("data/total_pets.json", 'w+') as f:
                            json.dump(data, f)
                        st.success("Your pet {} has been added.".format(pet_name))
                    else:
                        st.error("""You must submit your pet's expenses""")

                else:
                    st.error("""You must include pet's name""")


if __name__ == '__main__':
    main()
