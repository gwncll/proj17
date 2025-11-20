import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="EduTrack")

#Grade Conversion

def convert_marks_to_grade(mark):
    if mark >= 85: 
        return "A", 4.00
    elif mark >= 80: 
        return "A-", 3.75
    elif mark >= 75: 
        return "B+", 3.50
    elif mark >= 65: 
        return "B", 3.00
    elif mark >= 55: 
        return "C+", 2.50
    elif mark >= 50: 
        return "C", 2.00
    elif mark >= 45: 
        return "D+", 1.50
    elif mark >= 40: 
        return "D", 1.00
    else: 
        return "F", 0.00

#CSV

FILE = "student_records.csv"

def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    else:
        return pd.DataFrame(columns=["Semester", "Course", "Credit", "Marks", "Grade", "Point"])
    
def save_data(df):
    df.to_csv(FILE, index=False)

df = load_data()

#Sidebar Navigation

menu = st.sidebar.radio(
    "Menu",
    ["Home", "Add Course", "View Records", "Edit Record", "Delete Record", "Display Summary"]
)

#1>Home

if menu == "Home":
    st.title("EduTrack")
    st.subheader("Welcome to **EduTrack : Your Smart Study Dashboard !**")
    
    st.write("""
    ### Features:
             
    - Auto GPA & CGPA calculation
    - Smart performance feedback
    - Interactive performance charts
    - Download report data
             
    """)
    st.write("Use the sidebar to navigate")

#2>Add course

elif menu == "Add Course":
    st.header("Add Course")

    existing_semesters = sorted(df["Semester"].unique())
    
    st.write("### Select or Create Semester")
    option = st.radio("Choose:", ["Select Existing Semester", "Create New Semester"])

    if option == "Select Existing Semester" and len(existing_semesters) > 0:
        sem = st.selectbox("Select Semester", existing_semesters)
    else:
        sem = st.text_input("Enter New Semester Name (Example: Sem 1, Sem 2, Year 1 Sem 2, Trimester 1)")

    course = st.text_input("Course Name")
    credit = st.number_input("Credit Hour", min_value=1, max_value=10, step=1)
    marks = st.number_input("Marks (0-100)", min_value=0, max_value=100)

    if st.button("Add to Records"):
        if sem.strip() == "":
            st.error("Semester name cannot be empty.")
        else:
            grade, point = convert_marks_to_grade(marks)

            new_row = pd.DataFrame({
                "Semester":[sem],
                "Course":[course],
                "Credit":[credit],
                "Marks":[marks],
                "Grade":[grade],
                "Point":[point]
            })

            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success(f"Saved! {course} added to {sem}.")

#3>View Records + CSV Download/Upload/Reset

elif menu == "View Records":
    st.header("All Records")
    st.dataframe(df)

    st.write("### 📁 CSV File Options")

    #Download CSV
    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False),
        file_name="student_records.csv",
        mime="text/csv"
    )

    #Upload CSV
    uploaded = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        save_data(df)
        st.success("CSV file loaded successfully!")

    #Reset CSV
    if st.button("Reset All Data"):
        df = pd.DataFrame(columns=["Semester", "Course", "Credit", "Marks", "Grade", "Point"])
        save_data(df)
        st.warning("All data has been cleared!")

#4>Edit a record

elif menu == "Edit Record":
    st.header("Edit Record")

    if len(df) == 0:
        st.warning("No records to edit.")
    else:
        index = st.number_input("Enter row index to edit", min_value=0, max_value=len(df)-1)
        row = df.iloc[index]

        sem = st.text_input("Semester", value=row["Semester"])
        course = st.text_input("Course", value=row["Course"])
        credit = st.number_input("Credit Hour", min_value=1, max_value=6, value=int(row["Credit"]))
        marks = st.number_input("Marks", min_value=0, max_value=100, value=int(row["Marks"]))

        if st.button("Update"):
            grade, point = convert_marks_to_grade(marks)
            df.loc[index] = [sem, course, credit, marks, grade, point]
            save_data(df)
            st.success("Record updated!")

#5>Delete a record

elif menu == "Delete Record":
    st.header("Delete Record")

    if len(df) == 0:
        st.warning("No records available.")
    else:
        index = st.number_input("Enter record index to delete", min_value=0, max_value=len(df)-1)

        if st.button("Delete"):
            df = df.drop(index).reset_index(drop=True)
            save_data(df)
            st.success("Record deleted!")

#6>Display summary, feedback, charts

elif menu == "Display Summary":
    st.header("GPA, CGPA Summary & Performance Feedback")

    if len(df) == 0:
        st.warning("No data available.")
    else:
        semesters = sorted(df["Semester"].unique())
        summary = {}

        for sem in semesters:
            temp = df[df["Semester"] == sem]
            gpa = (temp["Credit"] * temp["Point"]).sum() / temp["Credit"].sum()
            summary[sem] = round(gpa, 2)

        #Calculate CGPA
        total_points = (df["Credit"] * df["Point"]).sum()
        total_credits = df["Credit"].sum()
        cgpa = total_points / total_credits

        st.subheader(f"Overall CGPA: **{cgpa:.2f}**")

        #Performance Feedback (Motivational Message)

        st.subheader("Performance Feedback")

        latest_sem = semesters[-1]
        latest_gpa = summary[latest_sem]

        prev_gpa = summary[semesters[-2]] if len(semesters) > 1 else None

        #GPA feedback
        if latest_gpa >= 3.50:
            st.success("🔥 Excellent! You're performing at Dean's List level!")
        elif latest_gpa >= 3.30:
            st.info("💪 Great job! Keep up the strong performance.")
        elif latest_gpa >= 3.00:
            st.write("👍 Solid performance! A bit more effort can boost your GPA even higher.")
        elif latest_gpa >= 2.00:
            st.write("❗You're capable of much more. Keep working on it!")
        else:
            st.warning("‼️Try reviewing your study habits. You can improve!")

        #Improvement feedback
        if prev_gpa is not None:
            diff = latest_gpa - prev_gpa
            if diff > 0:
                st.success(f"GPA improved by {diff:.2f}! Great progress!")
            elif diff < 0:
                st.warning(f"GPA dropped by {abs(diff):.2f}. Every fall is an opportunity to rise stronger!")
            else:
                st.info("GPA remained the same as the previous semester. ")

        st.markdown("---")

        #matplotlib bar chart

        st.subheader("GPA Analysis")
        fig, ax = plt.subplots()
        bars = ax.bar(summary.keys(), summary.values())
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{height:.2f}",
                ha="center",va="bottom",fontsize=10
            )


        ax.set_xlabel("Semester")
        ax.set_ylabel("GPA")
        ax.set_title("GPA by Semester")
        st.pyplot(fig)

        #matplotlib line chart

        st.subheader("GPA Progress")
        fig2, ax2 = plt.subplots()
        ax2.plot(list(summary.keys()), list(summary.values()), marker="o")
        ax2.set_xlabel("Semester")
        ax2.set_ylabel("GPA")
        ax2.set_title("GPA Trend Across Semesters")
        st.pyplot(fig2)

#change colour (design)       
st.markdown("""
    <style>
    .stApp {
        background-color: #D9C4B0;
    }
   
    section[data-testid="stSidebar"] {
        background-color: #CFAB8D;
    }
            
    html, body, [class*="css"] {
        color: black !important;
    }
    p, span, label, h1, h2, h3, h4, h5, h6, div {
        color: black !important;
    }
            
    .stTextInput input {
        background-color: #ECEEDF;   
        color: black;
    }
            
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ECEEDF;  
        color: black;
    }
    
    .stNumberInput input {
        background-color: #BBDCE5; 
        color: black;
    }
            
    /* Change CSV Buttons (Download / Reset) */
    .stDownloadButton button, .stButton button {
        background-color: #CFAB8D !important;     /* light brown */
        color: black !important;
    }

    /* Hover effect */
    .stDownloadButton button:hover, .stButton button:hover {
        background-color: #B89274 !important;
    }

    /* Change File Uploader Box */
    [data-testid="stFileUploaderDropzone"] {
        background-color: #E6D5C3 !important;   /* light beige */
        border: 2px dashed #8B5E3C !important;  /* brown border */
       
    }

    /* Change inside text */
    [data-testid="stFileUploaderDropzone"] * {
        color: black !important;
    }

    /* Change "Browse files" button */
    [data-testid="stFileUploaderBrowseButton"] {
        background-color: #CFAB8D !important;
        color: black !important;
    }

    [data-testid="stFileUploaderBrowseButton"]:hover {
        background-color: #B89274 !important;
    }
            
    /* Change the +/- buttons of st.number_input */
    [data-testid="stNumberInput"] button {
        background-color: #CFAB8D !important;   /* light brown */
        color: black !important;
    }

    /* Hover effect */
    [data-testid="stNumberInput"] button:hover {
        background-color: #B89274 !important;
    }

    /* Change the number input text field */
    [data-testid="stNumberInput"] input {
        background-color: #E2F0FF !important;   /* your light blue */
        color: black !important;
    }

    </style>
""", unsafe_allow_html=True)