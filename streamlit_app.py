import html

import streamlit as st

st.set_page_config(page_title="AI Ethics Assessment Pre-Screening", page_icon="🧭", layout="wide")

# ServiceNow-inspired mock styling
st.markdown(
    """
    <style>
    .stApp {
        background: #eef0f4;
        color: #1f2937;
    }
    .block-container {
        padding-top: 1.2rem;
    }
    .sn-tabs {
        display: flex;
        flex-wrap: wrap;
        border-bottom: 1px solid #98a2b3;
        margin-bottom: 0;
    }
    .sn-tab {
        padding: 0.7rem 1.2rem;
        border: 1px solid #98a2b3;
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        background: #d3d8e2;
        color: #111827;
        font-size: 0.95rem;
    }
    .sn-tab.active {
        background: #f4f6fa;
        border-top: 4px solid #0d47a1;
        padding-top: 0.5rem;
    }
    .sn-surface {
        border: 1px solid #98a2b3;
        border-top: none;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
        background: #f4f6fa;
        padding: 1.1rem 1rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.1);
    }
    .sn-row {
        border-bottom: 1px solid #d0d5dd;
        padding: 0.95rem 0.4rem;
    }
    .sn-row:last-child {
        border-bottom: none;
    }
    .sn-qtitle {
        font-size: 1.05rem;
        margin: 0;
        color: #111827;
    }
    .sn-qhint {
        margin-left: 0.3rem;
    }
    .qtitle-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        width: 100%;
    }
    .info-btn-wrap {
        display: inline-flex;
        position: relative;
        justify-content: flex-end;
        align-items: center;
    }
    .info-popover-btn {
        min-height: 2rem;
        height: 2rem;
        min-width: 2rem;
        width: 2rem;
        border-radius: 999px;
        border: 1px solid #98a2b3;
        background: #e6ebf3;
        padding: 0;
        font-size: 1rem;
        line-height: 1;
        cursor: help;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .info-popover-content {
        display: none;
        position: absolute;
        right: 0;
        top: calc(100% + 0.35rem);
        z-index: 999;
        width: 16rem;
        background: #ffffff;
        color: #1f2937;
        border: 1px solid #98a2b3;
        border-radius: 8px;
        padding: 0.65rem 0.75rem;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.18);
        font-size: 0.82rem;
        text-align: left;
    }
    .info-btn-wrap:hover .info-popover-content,
    .info-btn-wrap:focus-within .info-popover-content {
        display: block;
    }
    .stSelectbox > div > div {
        background: #c6ccd8;
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
            st.session_state[question_key] = "--Please select--"


def render_assessment_question(question_key: str, question_number: int, title: str, tooltip: str) -> str | None:
    st.markdown("<div class='sn-row'>", unsafe_allow_html=True)
    question_col, answer_col = st.columns([0.62, 0.38], vertical_alignment="center")
    with question_col:
        title_col, info_col = st.columns([0.92, 0.08], vertical_alignment="center")
        with title_col:
            st.markdown(f"<div class='qtitle-wrap'><p class='sn-qtitle'>Q{question_number}. {title}</p></div>", unsafe_allow_html=True)
        with info_col:
            escaped_tooltip = html.escape(tooltip)
            st.markdown(
                f"""
                <div class='info-btn-wrap'>
                    <span class='info-popover-btn' role='button' tabindex='0' aria-label='More information about question {question_number}'>💡</span>
                    <div class='info-popover-content'>{escaped_tooltip}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with answer_col:
        selected = st.selectbox(
            f"Q{question_number}",
            ["--Please select--", *OPTIONS],
            key=question_key,
            label_visibility="collapsed",
        )
    st.markdown("</div>", unsafe_allow_html=True)
    return None if selected == "--Please select--" else selected


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
        <div class='sn-tabs'>
            <div class='sn-tab active'>AI Ethics Assessment Pre-screening</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='sn-surface'>", unsafe_allow_html=True)

    visible_questions: set[str] = {"q1", "q3"}
    required_questions: set[str] = {"q1", "q3"}

    q1_help = (
        "Personal data includes identifiable info such as name, email, employee ID, IP address, "
        "user-linked chat transcripts, metadata, prompts, and feedback tied to an individual."
    )
    q1 = render_assessment_question("q1", 1, "Is the solution intended to process personal data?", q1_help)

    q2 = None
    if q1 == "Yes":
        visible_questions.add("q2")
        required_questions.add("q2")
        q2_help = (
            "Examples: authentication, access control, login records, telemetry, usage analytics, audit logs, "
            "technical troubleshooting, security monitoring, account provisioning."
        )
        q2 = render_assessment_question(
            "q2",
            2,
            "If yes, is processing limited to simple identifiers used only for technical/administrative purposes?",
            q2_help,
        )

    q3_help = (
        "Examples: model training/testing/evaluation in research projects, comparing methods, "
        "experimental results for publication, exploratory R&D or lab use."
    )
    q3 = render_assessment_question(
        "q3",
        3,
        "Is the solution solely used and developed for scientific research and scientific development purposes?",
        q3_help,
    )

    q4 = q5 = q6 = q7 = q8 = q9 = None
    if q3 != "Yes":
        visible_questions.update({"q4", "q5"})
        required_questions.update({"q4", "q5"})

        q4_help = (
            "Includes outputs affecting employees, applicants, patients, customers, participants, users, or population segments."
        )
        q4 = render_assessment_question(
            "q4",
            4,
            "Does it produce recommendations/insights/decisions/scores/rankings/profiles/classifications/predictions about people or specific groups?",
            q4_help,
        )

        q5_help = (
            "Includes chatbots, copilots, assistants, agents, and AI that generates/transforms text, images, audio, "
            "video, code, summaries, or answers."
        )
        q5 = render_assessment_question(
            "q5",
            5,
            "Is the solution using Generative AI systems, like Chatbots, agents or copilots?",
            q5_help,
        )

        if q5 == "Yes":
            visible_questions.add("q6")
            required_questions.add("q6")
            q6_help = (
                "Examples may include internally approved enterprise chatbot/copilot platforms that were pre-assessed."
            )
            q6 = render_assessment_question(
                "q6",
                6,
                "If yes, is it created using an approved platform that already underwent an AI Ethics Assessment?",
                q6_help,
            )

            if q6 == "Yes":
                visible_questions.update({"q7", "q8", "q9"})
                required_questions.update({"q7", "q8", "q9"})

                q7_help = (
                    "Examples: racial/ethnic origin, political opinions, religious beliefs, union membership, genetic data, "
                    "biometric data, health data, sex life, sexual orientation."
                )
                q7 = render_assessment_question(
                    "q7",
                    7,
                    "For generative AI, is it intended to process special categories of personal data?",
                    q7_help,
                )

                q8_help = (
                    "Examples: hiring prioritization, filtering applications, candidate evaluation, promotion/termination "
                    "recommendations, monitoring performance/conduct/productivity."
                )
                q8 = render_assessment_question(
                    "q8",
                    8,
                    "Is it intended for employee management or recruitment activities?",
                    q8_help,
                )

                q9_help = (
                    "Examples: unsafe actions, material wellbeing impact, distress/reputational harm, financial loss, "
                    "inappropriate intervention, or influencing opportunities/treatment/access."
                )
                q9 = render_assessment_question(
                    "q9",
                    9,
                    "Can the outputs reasonably cause physical, psychological, or financial harm?",
                    q9_help,
                )

    clear_hidden_answers(visible_questions)
    submitted = st.button("Evaluate", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        answers = {question_key: st.session_state.get(question_key) for question_key in required_questions}

        if any(value is None for value in answers.values()):
            st.error("Please answer every visible question using Yes, No, or Unsure.")
        else:
            st.session_state.result = evaluate(answers)
            st.session_state.completed = True
            st.rerun()
