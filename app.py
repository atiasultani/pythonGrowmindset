import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set up the app configuration
st.set_page_config(page_title="Data Sweeper", page_icon="", layout="wide")
st.title("Data Sweeper")
st.write("Transform CSV and Excel Files to built-in duplicate data clean and visualization")

# Cache function to load the data efficiently using st.cache_data
@st.cache_data
def load_data(file, file_ext):
    if file_ext == ".csv":
        return pd.read_csv(file)
    elif file_ext == ".xlsx":
        return pd.read_excel(file)
    else:
        return None

# File uploader widget
uploaded_files = st.file_uploader("Upload Your Files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Load the uploaded file using cached function
        df = load_data(file, file_ext)
        
        if df is None:
            st.write(f"Unsupported file type: {file_ext}")
            continue

        # Display file information
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")

        # Display initial preview (first time only)
        st.write("Preview of the data:")
        num_rows = st.slider("Select number of rows to display", min_value=10, max_value=len(df), value=10)
        st.dataframe(df.head(num_rows))  # Display only the first `num_rows` rows

        # Initialize a flag to track if preview was already shown
        preview_shown = False

        # Data Cleaning (remove duplicates and fill missing values)
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates removed!")
                    preview_shown = False  # Reset the flag so that preview is shown after removal
                
            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    # Fill missing numeric values with 0 (instead of the mean)
                    df[numeric_cols] = df[numeric_cols].fillna(0)
                    st.write("Missing values have been filled with 0!")

                    # Show updated data preview after filling missing values
                    preview_shown = False  # Reset the flag so that preview is shown after filling missing values

            # Only show the updated data preview once after cleaning
            if not preview_shown:
                st.write("Updated Data Preview:")
                st.dataframe(df.head(num_rows))  # Show updated preview after filling missing values and removing duplicates
                preview_shown = True

        # Choose specific columns to keep or convert
        st.subheader("Select Columns to Keep/Convert")
        columns = st.multiselect(f"Choose Columns from {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Show updated data preview after selecting columns (if preview not shown)
        if not preview_shown:
            st.write("Updated Data Preview after Column Selection:")
            st.dataframe(df.head(num_rows))

        # Data Visualization (Bar chart)
        st.subheader("Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

        # File Conversion Options (CSV to Excel or Excel to CSV)
        st.subheader("File Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            # Provide download button
            st.download_button(
                label="Download file",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )
