"""Interview tab UI - Mock interview practice."""

import streamlit as st

from career_coach.domain.schemas import InterviewCriterion, InterviewRubricScore, SkillGap
from career_coach.services.interview_service import (
    calculate_session_score,
    evaluate_answer,
    generate_interview_session,
    get_rubric_for_question,
)
from career_coach.ui.theme import render_alert, render_empty_state, render_section_header
from career_coach.ui.navigation import navigate_to


def render_interview_tab():
    """Render the Interview Practice tab."""
    results = st.session_state.get("analysis_results")
    
    if not results:
        st.markdown(render_empty_state(
            title="No Analysis Results",
            description="Complete the Intake tab first to generate interview questions tailored to your skill gaps.",
            icon="file-text",
        ), unsafe_allow_html=True)
        st.button(
            "Go to Intake",
            key="goto_intake_interview",
            on_click=navigate_to,
            args=("Intake",),
        )
        return
    
    gaps = [SkillGap.model_validate(gap) for gap in results.get("gaps", [])]
    
    if not gaps:
        st.markdown(
            render_alert("🎉 No significant skill gaps found! You're well-prepared for interviews.", "success"),
            unsafe_allow_html=True,
        )
        return
    
    # Session management
    sessions = st.session_state.get("interview_sessions")
    
    if sessions is None:
        # Configuration
        st.markdown(
            render_section_header(
                "🎯 Interview Session Setup",
                "Generate questions targeting your top skill gaps",
            ),
            unsafe_allow_html=True,
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            target_role = st.text_input("Target Role", "Senior Data Engineer", key="interview_role")
        with col2:
            max_skills = st.slider("Skills to Cover", 3, 8, 5, key="interview_skills")
        with col3:
            questions_per_skill = st.slider("Questions per Skill", 1, 3, 2, key="interview_qps")
        
        if st.button(
            "Generate Interview Session",
            type="primary",
            key="gen_interview_btn",
            width="stretch",
        ):
            with st.spinner("Generating tailored interview questions..."):
                sessions = generate_interview_session(
                    gaps,
                    target_role=target_role,
                    max_skills=max_skills,
                    questions_per_skill=questions_per_skill,
                )
                st.session_state.interview_sessions = sessions
                st.session_state.interview_current = 0
            st.success(f"Generated {len(sessions)} questions!")
            st.rerun()
        return
    
    # Display interview session
    if not sessions:
        st.warning("No questions generated. Try different parameters.")
        if st.button("Regenerate", key="regen_interview"):
            st.session_state.interview_sessions = None
            st.rerun()
        return
    
    current_idx = st.session_state.get("interview_current", 0)
    current_idx = max(0, min(current_idx, len(sessions) - 1))
    st.session_state.interview_current = current_idx
    
    session = sessions[current_idx]
    
    # Progress bar
    progress = (current_idx + 1) / len(sessions)
    st.progress(progress, text=f"Question {current_idx + 1} of {len(sessions)}")
    
    # Question card
    st.markdown(render_section_header(
        f"🎤 {session.category.title()}",
        f"Question {current_idx + 1} of {len(sessions)}",
        icon="help-circle",
    ), unsafe_allow_html=True)
    
    st.markdown(f"### {session.question}")
    
    # Answer input
    answer = st.text_area(
        "Your Answer",
        value=session.answer,
        height=200,
        placeholder="Type your answer here... Use STAR format for behavioral questions.",
        key=f"answer_{current_idx}",
    )
    
    # Update answer
    if answer != session.answer:
        session.answer = answer
    
    # Rubric display
    with st.expander("📋 Evaluation Rubric", expanded=False):
        rubric = get_rubric_for_question(
            session.question,
            session.category,
            session.question_type,
        )
        for criterion, details in rubric.items():
            st.markdown(f"**{criterion.value.replace('_', ' ').title()}** ({details['weight']:.0%})")
            st.caption(details['description'])
    
    # Evaluation
    if session.answer.strip():
        eval_result = evaluate_answer(session, session.answer)
        
        st.markdown("---")
        st.markdown("### 📊 Self-Evaluation")
        st.caption(eval_result["feedback"])
        
        scores = {}
        for criterion, default_score in eval_result["scores"].items():
            score = st.slider(
                criterion.replace('_', ' ').title(),
                1, 5, default_score,
                key=f"score_{current_idx}_{criterion}",
                help=eval_result["rubric"][criterion]["description"]
            )
            scores[criterion] = score
        
        if st.button("Save Evaluation", key=f"save_eval_{current_idx}"):
            session.scores = [
                InterviewRubricScore(
                    criterion=InterviewCriterion(c),
                    score=s,
                    evidence=session.answer.strip()[:1000],
                    improvement_action=(
                        f"Practice the {c.replace('_', ' ')} part of this answer using the rubric."
                    ),
                )
                for c, s in scores.items()
            ]
            session.completed = True
            st.success("Evaluation saved!")
            st.rerun()
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if current_idx > 0:
            if st.button("← Previous", key="prev_q"):
                st.session_state.interview_current = current_idx - 1
                st.rerun()
    with col2:
        st.caption(f"Progress: {sum(1 for s in sessions if s.completed)}/{len(sessions)} completed")
    with col3:
        if current_idx < len(sessions) - 1:
            if st.button("Next →", key="next_q"):
                st.session_state.interview_current = current_idx + 1
                st.rerun()
        elif all(s.completed for s in sessions):
            if st.button("View Results", type="primary", key="view_results"):
                st.session_state.show_interview_results = True
                st.rerun()
    
    # Results
    if st.session_state.get("show_interview_results"):
        st.markdown("---")
        st.markdown(
            render_section_header("📈 Interview Results", "Your self-evaluation summary"),
            unsafe_allow_html=True,
        )
        
        score_data = calculate_session_score(sessions)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Score", f"{score_data['overall_score']:.1f}/5.0")
        with col2:
            st.metric("Percentage", f"{score_data['percentage']}%")
        with col3:
            st.metric("Completed", f"{score_data['completed']}/{score_data['total_questions']}")
        
        st.markdown("**By Criterion:**")
        for criterion, avg in score_data['by_criterion'].items():
            st.progress(avg / 5.0, text=f"{criterion.replace('_', ' ').title()}: {avg:.1f}/5.0")
        
        if st.button("Start New Session", key="new_interview"):
            st.session_state.interview_sessions = None
            st.session_state.show_interview_results = False
            st.rerun()