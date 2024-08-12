import streamlit as st
from capstone_ocr import process_document, count_grades, assign_core_maths_score, assign_elective_maths_score, assign_physics_score, calculate_aggregate, assign_score
from PIL import Image
import json

st.set_page_config(page_title="Admissions Reviewer", layout="wide")

st.header("Admissions Reviewer")

# Sidebar for input and options
with st.sidebar:
    st.subheader("Upload Results")
    img = st.file_uploader("Upload Results", type=["png", "jpg"])

    st.subheader("Select Major")
    major = st.selectbox("Select Student's Major", ["Engineering", "Arts & Science"])

if img is not None:
    text = process_document(img)
    
    # Parse results from the text
    parsed_data = json.loads(text)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Student Information")
        st.write(f"**Candidate Name:** {parsed_data['candidate_name']}")
        
        st.subheader("Grades")
        grades = count_grades(parsed_data['results'])
        grades_table = ""
        for grade, count in grades.items():
            grades_table += f"{grade}: {count}\n"
        st.text(grades_table)

    with col2:
        st.subheader("Scores")
        
        aggregate_score = calculate_aggregate(parsed_data['results'])
        st.write(f"**Aggregate Score:** {aggregate_score}")
        
        score = assign_score(aggregate_score)
        st.write(f"**Ashesi Exam Score:** {score}")
        
        core_maths_score = assign_core_maths_score(parsed_data['results'])
        st.write(f"**Core Maths Score:** {core_maths_score}")
        
        if major == "Engineering":
            elective_maths_score = assign_elective_maths_score(parsed_data['results'])
            physics_score = assign_physics_score(parsed_data['results'])
            st.write(f"**Elective Maths Score:** {elective_maths_score}")
            st.write(f"**Physics Score:** {physics_score}")

    st.subheader("Detailed Results")
    detailed_results = ""
    for subject, grade in parsed_data['results'].items():
        detailed_results += f"{subject.replace('_', ' ').title()}: {grade}\n"
    st.text(detailed_results)

else:
    st.info("Please upload a results image to proceed.")


