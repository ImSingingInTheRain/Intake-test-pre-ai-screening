import streamlit as st

st.set_page_config(page_title="AI Ethics Assessment Pre-Screening", page_icon="🧭", layout="centered")

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
QUESTION_KEYS = [f"q{i}" for i in range(1, 10)]


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


def clear_hidden_answers(visible_questions: set[str]) -> None:
    for question_key in QUESTION_KEYS:
        if question_key not in visible_questions and question_key in st.session_state:
            st.session_state[question_key] = None


def render_question_title(question_number: int, title: str, tooltip: str) -> None:
    tooltip_html = tooltip.replace('"', "&quot;")
    st.markdown(
        f"""
        <div class='sn-card'>
            <h3>Q{question_number}. {title} <span title="{tooltip_html}" style="cursor: help;">(?)</span></h3>
        </div>
        """,
        unsafe_allow_html=True,
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
        for question_key in QUESTION_KEYS:
            st.session_state.pop(question_key, None)
        st.rerun()
else:
    st.markdown(
        """
        <div class='sn-header'>
            <h1>AI Ethics Assessment Pre-Screening</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Questions appear only when they are needed based on earlier answers.")

    visible_questions: set[str] = {"q1", "q3"}
    required_questions: set[str] = {"q1", "q3"}

    q1_help = (
        "Personal data includes identifiable info such as name, email, employee ID, IP address, "
        "user-linked chat transcripts, metadata, prompts, and feedback tied to an individual."
    )
    render_question_title(1, "Is the solution intended to process personal data?", q1_help)
    q1 = st.radio(
        "Q1",
        OPTIONS,
        index=None,
        key="q1",
        label_visibility="collapsed",
    )

    q2 = None
    if q1 == "Yes":
        visible_questions.add("q2")
        required_questions.add("q2")
        q2_help = (
            "Examples: authentication, access control, login records, telemetry, usage analytics, audit logs, "
            "technical troubleshooting, security monitoring, account provisioning."
        )
        render_question_title(
            2,
            "If yes, is processing limited to simple identifiers used only for technical/administrative purposes?",
            q2_help,
        )
        q2 = st.radio(
            "Q2",
            OPTIONS,
            index=None,
            key="q2",
            label_visibility="collapsed",
        )

    q3_help = (
        "Examples: model training/testing/evaluation in research projects, comparing methods, "
        "experimental results for publication, exploratory R&D or lab use."
    )
    render_question_title(
        3,
        "Is the solution solely used and developed for scientific research and scientific development purposes?",
        q3_help,
    )
    q3 = st.radio(
        "Q3",
        OPTIONS,
        index=None,
        key="q3",
        label_visibility="collapsed",
    )

    q4 = q5 = q6 = q7 = q8 = q9 = None
    if q3 != "Yes":
        visible_questions.update({"q4", "q5"})
        required_questions.update({"q4", "q5"})

        q4_help = (
            "Includes outputs affecting employees, applicants, patients, customers, participants, users, or population segments."
        )
        render_question_title(
            4,
            "Does it produce recommendations/insights/decisions/scores/rankings/profiles/classifications/predictions about people or specific groups?",
            q4_help,
        )
        q4 = st.radio(
            "Q4",
            OPTIONS,
            index=None,
            key="q4",
            label_visibility="collapsed",
        )

        q5_help = (
            "Includes chatbots, copilots, assistants, agents, and AI that generates/transforms text, images, audio, "
            "video, code, summaries, or answers."
        )
        render_question_title(
            5,
            "Is the solution using Generative AI systems, like Chatbots, agents or copilots?",
            q5_help,
        )
        q5 = st.radio(
            "Q5",
            OPTIONS,
            index=None,
            key="q5",
            label_visibility="collapsed",
        )

        if q5 == "Yes":
            visible_questions.add("q6")
            required_questions.add("q6")
            q6_help = (
                "Examples may include internally approved enterprise chatbot/copilot platforms that were pre-assessed."
            )
            render_question_title(
                6,
                "If yes, is it created using an approved platform that already underwent an AI Ethics Assessment?",
                q6_help,
            )
            q6 = st.radio(
                "Q6",
                OPTIONS,
                index=None,
                key="q6",
                label_visibility="collapsed",
            )

            if q6 == "Yes":
                visible_questions.update({"q7", "q8", "q9"})
                required_questions.update({"q7", "q8", "q9"})

                q7_help = (
                    "Examples: racial/ethnic origin, political opinions, religious beliefs, union membership, genetic data, "
                    "biometric data, health data, sex life, sexual orientation."
                )
                render_question_title(
                    7,
                    "For generative AI, is it intended to process special categories of personal data?",
                    q7_help,
                )
                q7 = st.radio(
                    "Q7",
                    OPTIONS,
                    index=None,
                    key="q7",
                    label_visibility="collapsed",
                )

                q8_help = (
                    "Examples: hiring prioritization, filtering applications, candidate evaluation, promotion/termination "
                    "recommendations, monitoring performance/conduct/productivity."
                )
                render_question_title(
                    8,
                    "Is it intended for employee management or recruitment activities?",
                    q8_help,
                )
                q8 = st.radio(
                    "Q8",
                    OPTIONS,
                    index=None,
                    key="q8",
                    label_visibility="collapsed",
                )

                q9_help = (
                    "Examples: unsafe actions, material wellbeing impact, distress/reputational harm, financial loss, "
                    "inappropriate intervention, or influencing opportunities/treatment/access."
                )
                render_question_title(
                    9,
                    "Can the outputs reasonably cause physical, psychological, or financial harm?",
                    q9_help,
                )
                q9 = st.radio(
                    "Q9",
                    OPTIONS,
                    index=None,
                    key="q9",
                    label_visibility="collapsed",
                )

    clear_hidden_answers(visible_questions)
    submitted = st.button("Evaluate", type="primary", use_container_width=True)

    if submitted:
        answers = {question_key: st.session_state.get(question_key) for question_key in required_questions}

        if any(value is None for value in answers.values()):
            st.error("Please answer every visible question using Yes, No, or Unsure.")
        else:
            st.session_state.result = evaluate(answers)
            st.session_state.completed = True
            st.rerun()
