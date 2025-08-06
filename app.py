import streamlit as st
import requests

st.set_page_config(page_title="StudyBot", page_icon=":robot_face:", layout="centered")
st.title("StudyBot :robot_face:")
# Input fields
subject = st.selectbox(" Select Subject", ["Maths", "Science", "History", "Geography", "English", "Hindi", "Computer Science", "Economics", "Political Science", "Psychology" , "Philosophy", "Sociology", "Business Studies", "Accountancy", "Physical Education", "Fine Arts", "Music", "Physical Science", "Life Science", "Environmental Science", "Statistics", "Agriculture", "Home Science", "Information Technology", "Engineering", "Architecture", "Law", "Medicine", "Nursing", "Pharmacy", "Veterinary Science", "Agricultural Engineering", "Forestry", "Fisheries", "Horticulture", "Animal Husbandry", "Dairy Technology", "Food Technology", "Textile Technology", "Leather Technology", "Plastic Technology", "Rubber Technology", "Ceramic Technology", "Glass Technology", "Mining Engineering", "Petroleum Engineering", "Chemical Engineering", "Civil Engineering", "Mechanical Engineering", "Electrical Engineering", "Electronics Engineering", "Computer Engineering", "Information Science and Engineering", "Aerospace Engineering", "Automobile Engineering", "Marine Engineering", "Metallurgical Engineering", "Mining and Mineral Engineering"])
level = st.selectbox("Select Level", ["Beginner", "Intermediate", "Advanced"])
style = st.selectbox("Select Learning Style", ["Visual", "Auditory", "Kinesthetic", text-based", hands-on"])
language = st.selectbox("Select Language", ["English", "Hindi", "Spanish", "French", "German", "Chinese", "Japanese", "Korean", "Russian", "Italian", "Portuguese", "Arabic", "Bengali", "Punjabi", "Gujarati", "Marathi", "Tamil", "Telugu", "Malayalam", "Kannada", "Odia", "Assamese", "Urdu"])
question = st.text_input("Enter your question")

if st.button("Get Answer"):
    try:
        response = requests.post(
            "http://localhost:8000/ask",
            json={
                "subject": subject,
                "level": level,
                "style": style,
                "language": language,
                "question": question
            }
        )

        if response.headers.get("Content-Type") == "application/json":
            res_json = response.json()
            if response.status_code == 200:
                st.markdown(res_json["answer"])
                st.session_state["initialized"] = True
            else:
                st.error(f"Error: {res_json.get('detail', 'Unknown error')}")
        else:
            st.error("Unexpected response format. Please try again later.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
st.divider()

if "initialized" in st.session_state:
    st.subheader("Ask Follow-up Questions")
    followup_question = st.text_input("Further question?")
    

    if st.button("Ask"):
        with st.spinner("Fetching answer..."):
            response = requests.post("http://127.0.0.1:8000/ask", json={"question": followup_question})

            if response.headers.get("Content-Type") == "application/json":
                res_json = response.json()
                if response.status_code == 200:
                    st.markdown(res_json["answer"])
                else:
                    st.error(f"Error: {res_json.get('detail', 'Unknown error')}")
            else:
                st.error("Unexpected response format. Please try again later.")