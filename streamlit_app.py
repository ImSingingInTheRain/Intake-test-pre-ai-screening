import streamlit as st

st.set_page_config(page_title="AI Ethics Assessment Screening", page_icon="🧭", layout="centered")

# ServiceNow-inspired mock styling
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f4f8fb 0%, #eef3f7 100%);
        color: #1f2937;
    }
    .sn-header {
        background: linear-gradient(90deg, #0f172a 0%, #0b4f7d 100%);
        color: #ffffff;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.18);
    }
    .sn-header h1 {
        margin: 0;
        font-size: 1.35rem;
        font-weight: 700;
    }
    .sn-header p {
        margin: 0.45rem 0 0;
        font-size: 0.95rem;
        opacity: 0.95;
    }
    .sn-card {
        background: #ffffff;
        border: 1px solid #dbe4ee;
        border-left: 5px solid #0b5cad;
        border-radius: 12px;
        padding: 1rem 1rem 0.5rem;
        box-shadow: 0 2px 8px rgba(2, 28, 55, 0.06);
        margin-bottom: 0.9rem;
    }
    .sn-card h3 {
        margin-top: 0;
        margin-bottom: 0.4rem;
        font-size: 1.02rem;
        color: #0f172a;
    }
    .outcome-box {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #dbe4ee;
        padding: 1.15rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
    }
    .outcome-a {
        border-left: 6px solid #0f9d58;
    }
    .outcome-b {
        border-left: 6px solid #c62828;
    }
    .subtle {
        color: #526071;
        font-size: 0.93rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "completed" not in st.session_state:
    st.session_state.completed = False
if "result" not in st.session_state:
    st.session_state.result = None


OPTIONS = ["Yes", "No", "Unsure"]


def evaluate(answers: dict[str, str]) -> tuple[str, str]:
    # Fallback rule
    if any(answer == "Unsure" for answer in answers.values()):
        return (
            "Outcome B: AI Ethics Assessment required",
            "At least one answer was marked as Unsure, so the fallback rule routes this to Outcome B.",
        )

    q1 = answers.get("q1")
    q2 = answers.get("q2")
    q3 = answers.get("q3")
    q4 = answers.get("q4")
    q5 = answers.get("q5")
    q6 = answers.get("q6")
    q7 = answers.get("q7")
    q8 = answers.get("q8")
    q9 = answers.get("q9")

    # Path 1 — research-only
    if q3 == "Yes":
        return (
            "Outcome A: Limited Risk — no AI Ethics Assessment needed",
            "Q3 is Yes (research-only scientific use/development).",
        )

    # Path 2 — clearly low-impact non-generative AI
    if q5 == "No" and q4 == "No" and (q1 == "No" or q2 == "Yes"):
        return (
            "Outcome A: Limited Risk — no AI Ethics Assessment needed",
            "Low-impact non-generative path met: Q5=No, Q4=No, and (Q1=No or Q2=Yes).",
        )

    # If non-generative but path 2 not met, route to B
    if q5 == "No":
        return (
            "Outcome B: AI Ethics Assessment required",
            "Non-generative path did not satisfy all Limited Risk conditions.",
        )

    # Generative AI branch
    if q6 == "No":
        return (
            "Outcome B: AI Ethics Assessment required",
            "Generative AI solution is not on an approved pre-assessed platform (Q6=No).",
        )

    if q7 == "Yes" or q8 == "Yes" or q9 == "Yes":
        return (
            "Outcome B: AI Ethics Assessment required",
            "Generative AI involves special-category data, employee/recruitment usage, or potential harm.",
        )

    # Path 3 — approved low-risk generative AI
    if q6 == "Yes" and q7 == "No" and q8 == "No" and q9 == "No":
        return (
            "Outcome A: Limited Risk — no AI Ethics Assessment needed",
            "Approved low-risk generative path met: Q6=Yes, Q7=No, Q8=No, Q9=No.",
        )

    return (
        "Outcome B: AI Ethics Assessment required",
        "Default routing rule applied for any combination outside limited-risk paths.",
    )


if st.session_state.completed:
    outcome_text, reason = st.session_state.result
    outcome_class = "outcome-a" if outcome_text.startswith("Outcome A") else "outcome-b"
    st.markdown(f"<div class='outcome-box {outcome_class}'>", unsafe_allow_html=True)
    st.markdown(f"### {outcome_text}")
    st.markdown(f"<p class='subtle'>{reason}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Restart assessment", type="primary"):
        st.session_state.completed = False
        st.session_state.result = None
        st.rerun()
else:
    st.markdown(
        """
        <div class='sn-header'>
            <h1>AI Ethics Assessment Screening</h1>
            <p>ServiceNow-style mockup · No data storage · Complete questionnaire to route to Outcome A or B.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("assessment_form"):
        st.markdown("<div class='sn-card'><h3>Q1. Personal data processing?</h3></div>", unsafe_allow_html=True)
        q1 = st.radio(
            "Is the solution intended to process personal data?",
            OPTIONS,
            index=None,
            help=(
                "Personal data includes identifiable info such as name, email, employee ID, IP address, "
                "user-linked chat transcripts, metadata, prompts, and feedback tied to an individual."
            ),
        )

        st.markdown("<div class='sn-card'><h3>Q2. Limited to simple identifiers for technical/admin use?</h3></div>", unsafe_allow_html=True)
        q2 = st.radio(
            "If yes, is processing limited to simple identifiers used only for technical/administrative purposes?",
            OPTIONS,
            index=None,
            help=(
                "Examples: authentication, access control, login records, telemetry, usage analytics, audit logs, "
                "technical troubleshooting, security monitoring, account provisioning."
            ),
        )

        st.markdown("<div class='sn-card'><h3>Q3. Scientific research/development only?</h3></div>", unsafe_allow_html=True)
        q3 = st.radio(
            "Is the solution solely used and developed for scientific research and scientific development purposes?",
            OPTIONS,
            index=None,
            help=(
                "Examples: model training/testing/evaluation in research projects, comparing methods, "
                "experimental results for publication, exploratory R&D or lab use."
            ),
        )

        st.markdown("<div class='sn-card'><h3>Q4. Outputs about people/groups?</h3></div>", unsafe_allow_html=True)
        q4 = st.radio(
            "Does it produce recommendations/insights/decisions/scores/rankings/profiles/classifications/predictions about people or specific groups?",
            OPTIONS,
            index=None,
            help=(
                "Includes outputs affecting employees, applicants, patients, customers, participants, users, or population segments."
            ),
        )

        st.markdown("<div class='sn-card'><h3>Q5. Generative AI system?</h3></div>", unsafe_allow_html=True)
        q5 = st.radio(
            "Is the solution a Generative AI system?",
            OPTIONS,
            index=None,
            help=(
                "Includes chatbots, copilots, assistants, agents, and AI that generates/transforms text, images, audio, "
                "video, code, summaries, or answers."
            ),
        )

        st.markdown("<div class='sn-card'><h3>Q6. Approved pre-assessed platform?</h3></div>", unsafe_allow_html=True)
        q6 = st.radio(
            "If yes, is it created using an approved platform that already underwent an AI Ethics Assessment?",
            OPTIONS,
            index=None,
            help=(
                "Examples may include internally approved enterprise chatbot/copilot platforms that were pre-assessed."
            ),
        )

        st.markdown("<div class='sn-card'><h3>Q7. Special categories of personal data?</h3></div>", unsafe_allow_html=True)
        q7 = st.radio(
            "For generative AI, is it intended to process special categories of personal data?",
            OPTIONS,
            index=None,
            help=(
                "Examples: racial/ethnic origin, political opinions, religious beliefs, union membership, genetic data, "
                "biometric data, health data, sex life, sexual orientation."
            ),
        )

        st.markdown("<div class='sn-card'><h3>Q8. Employee management or recruitment use?</h3></div>", unsafe_allow_html=True)
        q8 = st.radio(
            "Is it intended for employee management or recruitment activities?",
            OPTIONS,
            index=None,
            help=(
                "Examples: hiring prioritization, filtering applications, candidate evaluation, promotion/termination "
                "recommendations, monitoring performance/conduct/productivity."
            ),
        )

        st.markdown("<div class='sn-card'><h3>Q9. Potential physical/psychological/financial harm?</h3></div>", unsafe_allow_html=True)
        q9 = st.radio(
            "Can the outputs reasonably cause physical, psychological, or financial harm?",
            OPTIONS,
            index=None,
            help=(
                "Examples: unsafe actions, material wellbeing impact, distress/reputational harm, financial loss, "
                "inappropriate intervention, or influencing opportunities/treatment/access."
            ),
        )

        submitted = st.form_submit_button("Evaluate", type="primary", use_container_width=True)

    if submitted:
        answers = {
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "q4": q4,
            "q5": q5,
            "q6": q6,
            "q7": q7,
            "q8": q8,
            "q9": q9,
        }

        if any(value is None for value in answers.values()):
            st.error("Please answer every question using Yes, No, or Unsure.")
        else:
            st.session_state.result = evaluate(answers)
            st.session_state.completed = True
            st.rerun()
