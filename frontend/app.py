import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import os
from auth import login

API_URL = "https://authoritye.com"

if not login():
    st.stop()

st.set_page_config(
    page_title="AI Hiring Intelligence",
    layout="wide",
    page_icon=""
)
st.markdown("""
<style>
.stApp {
    background-color: #f4f6f9;
}
</style>
""", unsafe_allow_html=True)

st.title("AI Hiring Platform")
st.markdown("---")

#MODE SELECTION
mode = st.radio(
    "Select Mode",
    ["Resume Parsing (Bulk CSV)", "AI Shortlisting Engine"],
    horizontal=True
)

if mode == "Resume Parsing (Bulk CSV)":

    st.subheader("Upload Resumes")

    uploaded_files = st.file_uploader(
        "Upload PDF / DOCX",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if st.button("Process Resumes"):

        if not uploaded_files:
            st.warning("Upload resumes first.")
        else:

            files = [("files", (file.name, BytesIO(file.getvalue()))) for file in uploaded_files]

            with st.spinner("Processing..."):

                response = requests.post(
                    f"{API_URL}/upload/",
                    files=files
                )

            if response.status_code == 200:

                st.success("Processing Complete!")

                parsed_count = int(response.headers.get("X-Parsed", 0))
                duplicate_count = int(response.headers.get("X-Duplicate", 0))
                error_count = int(response.headers.get("X-Errors", 0))

                col1, col2, col3 = st.columns(3)

                col1.metric("Parsed", parsed_count)
                col2.metric("Duplicate", duplicate_count)
                col3.metric("Errors", error_count)

                st.download_button(
                    "Download Parsed CSV",
                    response.content,
                    "parsed_resumes.csv",
                    "text/csv"
                )

            else:
                st.error("Backend error.")
#Ai shortlisting Engine:
if mode == "AI Shortlisting Engine":

    st.subheader("Job Description")

    jd_text = st.text_area(
        "Paste Job Description Here",
        height=150
    )

    st.subheader("Upload Resumes")

    uploaded_files = st.file_uploader(
        "Upload PDF / DOCX",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="shortlist"
    )

    if st.button("Process & Rank Candidates"):

        if not uploaded_files:
            st.warning("Upload resumes first.")

        else:

            files = [("files", (file.name, BytesIO(file.getvalue()))) for file in uploaded_files]

            with st.spinner("Processing resumes..."):

                response = requests.post(
                    f"{API_URL}/upload/",
                    files=files,
                    data={"jd_text": jd_text}
                )

            if response.status_code == 200:

                df = pd.read_csv(BytesIO(response.content))
                st.session_state["rank_df"] = df
                st.success("Ranking Complete!")

                parsed_count = int(response.headers.get("X-Parsed", 0))
                duplicate_count = int(response.headers.get("X-Duplicate", 0))
                error_count = int(response.headers.get("X-Errors", 0))

                col1, col2, col3 = st.columns(3)

                col1.metric("Parsed", parsed_count)
                col2.metric("Duplicate", duplicate_count)
                col3.metric("Errors", error_count)

            else:
                st.error("Backend error.")
#dashboard
if "rank_df" in st.session_state:

    df = st.session_state["rank_df"].copy()

    st.markdown("---")
    st.subheader("Ranking Dashboard")

    min_score = st.slider(
        "Minimum JD Match Score",
        0,
        100,
        0
    )

    filtered_df = df[df["jd_match_score"] >= min_score]

    if not filtered_df.empty:

        col1, col2, col3 = st.columns(3)

        col1.metric("Candidates", len(filtered_df))
        col2.metric("Highest Score", int(filtered_df["jd_match_score"].max()))
        col3.metric("Average Score", round(filtered_df["jd_match_score"].mean(), 2))

    else:
        st.warning("No candidates match this filter.")

    # create Table
    st.markdown("Top 10 Candidates")

    top_columns = [
        "full_name",
        "email",
        "location",
        "designation",
        "total_experience",
        "matched_skills",
        "missing_skills",
        "jd_match_score",
        "rank"
    ]

    st.dataframe(
        filtered_df[top_columns].head(10),
        use_container_width=True
    )

    st.download_button(
        "Download Ranked CSV",
        filtered_df.to_csv(index=False),
        "ranked_candidates.csv",
        "text/csv"
    )

    #SEARCH block
    st.markdown("---")
    st.subheader("Search Candidates")
    search_skill = st.text_input("Search by Skill")
    search_location = st.text_input("Search by Location")

    search_df = filtered_df.copy()

    if search_skill:

        search_df = search_df[
            search_df["key_skills"].str.contains(search_skill, case=False, na=False)
        ]

    if search_location:

        search_df = search_df[
            search_df["location"].str.contains(search_location, case=False, na=False)
        ]

    st.dataframe(
        search_df[top_columns],
        use_container_width=True
    )
    #candite Profile

    st.markdown("---")
    st.subheader("Candidate Profile")

    if not search_df.empty:

        selected_name = st.selectbox(
            "Select Candidate",
            search_df["full_name"]
        )

        profile = search_df[
            search_df["full_name"] == selected_name
        ].iloc[0]

        col1, col2 = st.columns(2)

        with col1:

            st.write("Name:", profile.full_name)
            st.write("Location:", profile.location)
            st.write("Experience:", profile.total_experience)
            st.write("Skills:", profile.key_skills)

            #candidate summary using ai:
            summary_prompt = f"""
            Summarize this candidate for HR in 3 bullet points.

            Name: {profile.full_name}
            Skills: {profile.key_skills}
            Experience: {profile.total_experience}
            """

            response = requests.post(
                f"{API_URL}/summary/",
                json={"text": summary_prompt}
            )

            if response.status_code == 200:

                st.subheader("AI Candidate Summary")

                st.write(
                    response.json()["summary"]
                )

        with col2:

            st.subheader("Resume")

            file_path = os.path.join(
                "uploads",
                selected_name + ".pdf"
            )

            if os.path.exists(file_path):

                with open(file_path, "rb") as f:

                    st.download_button(
                        "Download Resume",
                        f,
                        file_name=os.path.basename(file_path)
                    )
#resume Prev.
st.markdown("---")
st.subheader("Resume Preview")
UPLOAD_FOLDER = "uploads"

if os.path.exists(UPLOAD_FOLDER):

    files = os.listdir(UPLOAD_FOLDER)

    if files:

        selected_file = st.selectbox(
            "Select Resume",
            files
        )

        file_path = os.path.join(
            UPLOAD_FOLDER,
            selected_file
        )

        with open(file_path, "rb") as f:

            st.download_button(
                "Download Resume",
                f,
                file_name=selected_file
            )