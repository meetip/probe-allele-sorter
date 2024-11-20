import py_compile
import pandas as pd

#import shap #temorary
import streamlit as st
import xlsxwriter


st.set_page_config("Probe Checking App",":dna:")#,layout="wide",initial_sidebar_state="expanded")

st.title('Quick Probe Checking App:dna:')
st.header('=================================')
 

# Uploading data and converting it to numbers only 
data= st.sidebar.file_uploader("Upload Probe result to compare",type=['xlsx'],key='1')
if data is not None:
    try:
        df_raw = pd.read_excel(data)
    except:
        pass
else:
    st.sidebar.write('*Kindly upload valid result data')
    
if data is not None:
    df= pd.read_excel(data)
    # Create the probe dictionary
    probe = {}
    for i in range(13, 17):
        probe[df.iloc[i, 0]] = df.iloc[i, 1]

    # Save rows from index 24 onward to a CSV file
    df_csv = df.iloc[23:, :]  # corrected to start from row 24 (index 23)
    df_csv.columns = ['Probe 1', 'Probe 2', 'Probe 3', 'Probe 4']
    df_csv.to_csv("output.csv", index=False)
 
    # Create an empty list to store the data
    data_list = []

    # Iterate through each column in the DataFrame
    for col in df_csv.columns:
        # Iterate through each item in the column
        for item in df_csv[col]:
            # Append a tuple of the item and the column name to the list
            data_list.append((item, col))

    # Create a new DataFrame from the list of tuples
    new_df = pd.DataFrame(data_list, columns=['Item', 'Column'])
    # Drop rows with NaN values in any column.
    new_df.dropna(inplace=True)

    # Group by 'Item' and count occurrences in each column
    item_counts = new_df.groupby('Item')['Column'].value_counts().unstack(fill_value=0)
    # Calculate the sum of 'probe1' to 'probe4'
    item_counts['sum'] = item_counts['Probe 1'] + item_counts['Probe 2'] + item_counts['Probe 3'] + item_counts['Probe 4']
    item_counts = item_counts.sort_values('sum', ascending=False)
    
    with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
        probe_df = pd.DataFrame(list(probe.items()), columns=['Probe', 'Value'])
        probe_df.to_excel(writer, sheet_name='Probe', index=False)
        item_counts.to_excel(writer, sheet_name='Item Counts')

    # Use st.download_button to provide a download link for the Excel file
    with open("output.xlsx", "rb") as file:
        st.download_button(
            label="Download result",
            data=file,
            file_name="result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.write('=================================')
    for k,v in probe.items():
        st.write(k," : ",v)
    st.write('=================================')
    st.write(item_counts)



