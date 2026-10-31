"""Shared navigation state for the Streamlit app."""

import streamlit as st

NAVIGATION_ITEMS = ("Intake", "Assessment", "Plan", "Interview", "Tracker", "Dashboard")


def navigate_to(tab_name: str) -> None:
    """Select a main app page before its navigation widget is rendered."""
    if tab_name not in NAVIGATION_ITEMS:
        raise ValueError(f"Unknown app page: {tab_name}")
    st.session_state["active_tab"] = tab_name
