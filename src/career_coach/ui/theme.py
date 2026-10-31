"""Professional Streamlit UI theme and styling."""

import html
import textwrap

import streamlit as st


def _escape_html(value: object) -> str:
    """Escape dynamic text before inserting it into HTML."""
    return html.escape(str(value), quote=True)


def apply_theme() -> None:
    """Apply professional minimal theme with CSS variables."""
    st.html("""
    <style>
    /* ========================================
       CSS Variables - Professional Palette
       ======================================== */
    :root {
        --bg-primary: #0b1120;
        --bg-secondary: #111827;
        --bg-tertiary: #1f2937;
        --bg-card: #1e293b;
        --bg-input: #0f172a;
        
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --text-inverse: #0b1120;
        
        --accent-primary: #22d3ee;
        --accent-primary-hover: #06b6d4;
        --accent-secondary: #8b5cf6;
        --accent-success: #22c55e;
        --accent-warning: #f59e0b;
        --accent-error: #ef4444;
        --accent-info: #3b82f6;
        
        --border-primary: #334155;
        --border-secondary: #475569;
        --border-focus: #22d3ee;
        
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.4), 0 2px 4px -2px rgba(0,0,0,0.3);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.4), 0 4px 6px -4px rgba(0,0,0,0.3);
        
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        
        --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        --font-mono: "SF Mono", "Fira Code", "Fira Mono", Menlo, Consolas, monospace;
    }
    
    /* ========================================
       Global Overrides
       ======================================== */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: var(--font-sans);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    
    /* ========================================
       Typography
       ======================================== */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
        line-height: 1.25;
        letter-spacing: -0.02em;
    }
    
    h1 { font-size: 2.25rem; margin-bottom: 0.5rem; }
    h2 { font-size: 1.75rem; margin-top: 2rem; margin-bottom: 1rem; }
    h3 { font-size: 1.25rem; margin-top: 1.5rem; margin-bottom: 0.75rem; }
    
    p { color: var(--text-secondary); line-height: 1.6; }
    
    a { color: var(--accent-primary); text-decoration: none; }
    a:hover { text-decoration: underline; }
    
    code {
        background: var(--bg-tertiary);
        color: var(--accent-primary);
        padding: 0.125rem 0.375rem;
        border-radius: var(--radius-sm);
        font-family: var(--font-mono);
        font-size: 0.875em;
    }
    
    pre {
        background: var(--bg-input);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-md);
        padding: 1rem;
        overflow-x: auto;
    }
    
    pre code { background: none; padding: 0; color: inherit; }
    
    /* ========================================
       Buttons
       ======================================== */
    .stButton > button {
        background: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-md);
        padding: 0.625rem 1.25rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.15s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        border-color: var(--accent-primary);
        box-shadow: var(--shadow-md);
        background: var(--bg-tertiary);
    }
    
    .stButton > button:focus {
        outline: none;
        box-shadow: 0 0 0 3px var(--accent-primary);
    }
    
    .stButton > button[kind="primary"] {
        background: var(--accent-primary);
        color: var(--text-inverse);
        border-color: var(--accent-primary);
    }

    .stButton > button[kind="primary"] p {
        color: var(--text-inverse) !important;
    }

    .stButton > button[kind="primary"]:disabled,
    .stButton > button[kind="primary"]:disabled:hover {
        background: #164e63;
        color: var(--text-primary);
        border-color: #155e75;
        opacity: 1;
    }

    .stButton > button[kind="primary"]:disabled p {
        color: var(--text-primary) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: var(--accent-primary-hover);
        border-color: var(--accent-primary-hover);
    }
    
    .stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    /* ========================================
       Inputs
       ======================================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-primary) !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-sans) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.15) !important;
    }
    
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label,
    .stFileUploader label {
        color: var(--text-secondary) !important;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border-secondary) !important;
        border-radius: var(--radius-lg) !important;
    }
    
    .stFileUploader > div > div:hover {
        border-color: var(--accent-primary) !important;
    }
    
    .stFileUploader > div > div > div {
        color: var(--text-secondary) !important;
    }
    
    /* ========================================
       Cards & Containers
       ======================================== */
    .skill-card {
        background: var(--bg-card);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-lg);
        padding: 1.25rem;
        transition: all 0.15s ease;
    }
    
    .skill-card:hover {
        border-color: var(--border-secondary);
        box-shadow: var(--shadow-md);
    }
    
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
    }
    
    .metric-label {
        color: var(--text-muted);
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }
    
    /* ========================================
       Chips / Badges
       ======================================== */
    .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        white-space: nowrap;
    }
    
    .chip-required { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
    .chip-preferred { background: rgba(245, 158, 11, 0.15); color: #fde047; border: 1px solid rgba(245, 158, 11, 0.3); }
    .chip-matched { background: rgba(34, 197, 94, 0.15); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.3); }
    .chip-gap { background: rgba(34, 211, 238, 0.15); color: #a5f3fc; border: 1px solid rgba(34, 211, 238, 0.3); }
    .chip-verified { background: rgba(139, 92, 246, 0.15); color: #d8b4fe; border: 1px solid rgba(139, 92, 246, 0.3); }
    
    /* ========================================
       Progress & Status
       ======================================== */
    .progress-bar {
        height: 6px;
        background: var(--bg-tertiary);
        border-radius: 3px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: var(--radius-md);
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-success { background: rgba(34, 197, 94, 0.15); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.3); }
    .status-warning { background: rgba(245, 158, 11, 0.15); color: #fde047; border: 1px solid rgba(245, 158, 11, 0.3); }
    .status-error { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
    .status-info { background: rgba(59, 130, 246, 0.15); color: #bfdbfe; border: 1px solid rgba(59, 130, 246, 0.3); }
    
    /* ========================================
       Tabs
       ======================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--bg-secondary);
        padding: 0.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-primary);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.625rem 1.25rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        border: none !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background: var(--bg-tertiary) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--bg-card) !important;
        color: var(--accent-primary) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* ========================================
       Expander
       ======================================== */
    .stExpander {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-primary) !important;
        border-radius: var(--radius-lg) !important;
    }
    
    .stExpander summary {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    /* ========================================
       Dataframe / Table
       ======================================== */
    .stDataFrame {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-primary) !important;
        border-radius: var(--radius-lg) !important;
    }
    
    /* ========================================
       Spinner
       ======================================== */
    .stSpinner > div {
        border-top-color: var(--accent-primary) !important;
    }
    
    /* ========================================
       Alert / Info boxes
       ======================================== */
    .alert {
        padding: 1rem 1.25rem;
        border-radius: var(--radius-md);
        border-left: 4px solid;
        margin: 1rem 0;
    }
    
    .alert-info { background: rgba(59, 130, 246, 0.1); border-color: var(--accent-info); color: var(--text-primary); }
    .alert-success { background: rgba(34, 197, 94, 0.1); border-color: var(--accent-success); color: var(--text-primary); }
    .alert-warning { background: rgba(245, 158, 11, 0.1); border-color: var(--accent-warning); color: var(--text-primary); }
    .alert-error { background: rgba(239, 68, 68, 0.1); border-color: var(--accent-error); color: var(--text-primary); }
    
    /* ========================================
       Sidebar
       ======================================== */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-primary);
    }
    
    [data-testid="stSidebar"] .stMarkdown { color: var(--text-secondary); }
    
    /* ========================================
       Scrollbar
       ======================================== */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border-secondary); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--border-primary); }
    
    /* ========================================
       Animations
       ======================================== */
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    
    .animate-fade-in { animation: fadeIn 0.3s ease forwards; }
    .animate-pulse { animation: pulse 1.5s ease-in-out infinite; }
    
    /* ========================================
       Utility Classes
       ======================================== */
    .text-center { text-align: center; }
    .text-muted { color: var(--text-muted); }
    .text-secondary { color: var(--text-secondary); }
    .text-success { color: var(--accent-success); }
    .text-warning { color: var(--accent-warning); }
    .text-error { color: var(--accent-error); }
    .text-accent { color: var(--accent-primary); }
    
    .mt-1 { margin-top: 0.5rem; }
    .mt-2 { margin-top: 1rem; }
    .mt-3 { margin-top: 1.5rem; }
    .mb-1 { margin-bottom: 0.5rem; }
    .mb-2 { margin-bottom: 1rem; }
    .mb-3 { margin-bottom: 1.5rem; }
    .gap-1 { gap: 0.5rem; }
    .gap-2 { gap: 1rem; }
    
    .flex { display: flex; }
    .flex-col { flex-direction: column; }
    .items-center { align-items: center; }
    .justify-between { justify-content: space-between; }
    .flex-wrap { flex-wrap: wrap; }
    </style>
    """)


def render_svg(icon_name: str, size: int = 20, color: str = "currentColor") -> str:
    """Render Lucide SVG icons inline."""
    icons = {
        "file-text": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>',
        "briefcase": '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect x="2" y="6" width="20" height="12" rx="2"/>',
        "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
        "book-open": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
        "clipboard-list": '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/><line x1="9" y1="9" x2="9" y2="21"/><line x1="15" y1="9" x2="15" y2="21"/>',
        "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        "alert-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
        "info": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
        "chevron-right": '<polyline points="9 18 15 12 9 6"/>',
        "chevron-down": '<polyline points="6 9 12 15 18 9"/>',
        "plus": '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
        "minus": '<line x1="5" y1="12" x2="19" y2="12"/>',
        "x": '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        "loader": '<path d="M21 12a9 9 0 1 1-6.219-8.56"/>',
        "brain": '<path d="M12 5a3 3 0 1 0-3 3c0 1.5-1.5 3-3 3"/><path d="M21 12c0 1.5-1.5 3-3 3"/><path d="M3 12c0 1.5 1.5 3 3 3"/><path d="M12 19a3 3 0 1 0 3-3c0-1.5 1.5-3 3-3"/><path d="M12 2a10 10 0 0 0-10 10c0 1.5 1.5 3 3 3s3-1.5 3-3"/><path d="M12 22a10 10 0 0 1 10-10c0-1.5-1.5-3-3-3s-3 1.5-3 3"/>',
        "trending-up": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
        "folder-open": '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/><path d="M2 10h20"/>',
        "settings": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
        "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
        "arrow-right": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    }
    
    svg = icons.get(icon_name, icons["file-text"])
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{svg}</svg>'


def render_chip(label: str, variant: str = "default", icon: str | None = None) -> str:
    """Render a styled chip/badge."""
    icon_html = render_svg(icon, 12) if icon else ""
    return f'<span class="chip chip-{_escape_html(variant)}">{icon_html}{_escape_html(label)}</span>'


def render_status(message: str, variant: str = "info", icon: str | None = None) -> str:
    """Render a status indicator."""
    icon_html = render_svg(icon, 16) if icon else ""
    return (
        f'<div class="status-indicator status-{_escape_html(variant)}">'
        f'{icon_html}{_escape_html(message)}</div>'
    )


def render_alert(message: str, variant: str = "info", icon: str | None = None) -> str:
    """Render an alert box."""
    icon_html = render_svg(icon, 18) if icon else ""
    return (
        f'<div class="alert alert-{_escape_html(variant)}">'
        f'{icon_html}{_escape_html(message)}</div>'
    )


def render_metric(label: object, value: object, delta: object | None = None) -> str:
    """Render a metric card."""
    delta_html = (
        f'<div class="text-success text-muted">{_escape_html(delta)}</div>' if delta else ""
    )
    return textwrap.dedent(f'''
    <div class="metric-card animate-fade-in">
        <div class="metric-value">{_escape_html(value)}</div>
        <div class="metric-label">{_escape_html(label)}</div>
        {delta_html}
    </div>
    ''').replace("\n", "").strip()


def render_skill_card(skill: dict, show_priority: bool = False) -> str:
    """Render a skill card with evidence and priority."""
    evidence = skill.get("evidence_level", "none")
    priority = skill.get("priority", 0)
    
    evidence_colors = {
        "verified": ("chip-verified", "verified"),
        "demonstrated": ("chip-matched", "demonstrated"),
        "self_reported": ("chip-preferred", "self-reported"),
        "mentioned": ("chip-preferred", "mentioned"),
        "none": ("chip-gap", "missing"),
    }
    chip_class, chip_label = evidence_colors.get(evidence, ("chip-gap", "unknown"))
    
    priority_bar = ""
    if show_priority:
        pct = int(priority * 100)
        priority_bar = (
            '<div class="progress-bar" style="margin-top: 0.75rem;">'
            f'<div class="progress-fill" style="width: {pct}%"></div>'
            '</div>'
            f'<div class="text-muted" style="font-size: 0.75rem; margin-top: 0.25rem;">Priority: {pct}%</div>'
        )

    canonical_skill = " ".join(str(skill.get("canonical_skill", "Unknown")).split())
    jd_evidence = " ".join(str(skill.get("jd_evidence", "")).split())
    resume_evidence = " ".join(str(skill.get("resume_evidence", "")).split())
    reason = " ".join(str(skill.get("reason", "")).split())
    uncertainty = " ".join(str(skill.get("uncertainty", "")).split())
    evidence_source = skill.get("resume_evidence_source", skill.get("evidence_source", ""))
    evidence_source_label = "user self-report" if evidence_source == "manual" else evidence_source
    metadata = []
    if evidence_source_label:
        metadata.append(f"Source: {_escape_html(evidence_source_label)}")
    if evidence_source == "resume":
        confidence_value = skill.get(
            "resume_extraction_confidence",
            skill.get("extraction_confidence", 0.0),
        )
        confidence = round(float(confidence_value) * 100)
        metadata.append(f"Extraction confidence: {confidence}%")
    if "evidence_strength" in skill:
        strength = round(float(skill["evidence_strength"]) * 100)
        metadata.append(f"Evidence strength: {strength}%")
    requirement_type = skill.get("requirement_type")
    if requirement_type:
        requirement_type = getattr(requirement_type, "value", requirement_type)
        metadata.append(
            f"JD context: {_escape_html(str(requirement_type).replace('_', ' '))}"
        )

    card_parts = [
        '<div class="skill-card animate-fade-in">',
        '<div class="flex justify-between items-center mb-1" style="gap: 0.5rem;">',
        f'<strong style="font-size: 1rem;">{_escape_html(canonical_skill)}</strong>',
        render_chip(chip_label, chip_class.replace("chip-", "")),
        '</div>',
        f'<div class="text-secondary text-muted" style="font-size: 0.875rem;">{_escape_html(reason)}</div>',
        priority_bar,
    ]
    if jd_evidence:
        card_parts.append(
            f'<div class="text-muted" style="font-size: 0.75rem; margin-top: 0.5rem;">'
            f'JD: {_escape_html(jd_evidence[:150])}...</div>'
        )
    if resume_evidence:
        card_parts.append(
            f'<div class="text-muted" style="font-size: 0.75rem; margin-top: 0.25rem;">'
            f'Evidence: {_escape_html(resume_evidence[:150])}...</div>'
        )
    if metadata:
        card_parts.append(
            '<div class="text-muted" style="font-size: 0.75rem; margin-top: 0.25rem;">'
            + " · ".join(metadata)
            + "</div>"
        )
    if uncertainty:
        card_parts.append(
            f'<div class="text-warning" style="font-size: 0.75rem; margin-top: 0.25rem;">'
            f'⚠ {_escape_html(uncertainty)}</div>'
        )
    card_parts.append('</div>')
    return "".join(card_parts)


def render_empty_state(title: str, description: str, icon: str = "file-text") -> str:
    """Render an empty state."""
    icon_html = render_svg(icon, 48, "var(--text-muted)")
    return textwrap.dedent(f'''
    <div class="skill-card text-center" style="padding: 3rem 2rem;">
        <div class="text-muted" style="margin-bottom: 1rem;">{icon_html}</div>
        <h3 style="margin-bottom: 0.5rem;">{_escape_html(title)}</h3>
        <p class="text-secondary">{_escape_html(description)}</p>
    </div>
    ''').replace("\n", "").strip()


def render_section_header(
    title: str,
    subtitle: str | None = None,
    icon: str | None = None,
    action: str | None = None,
) -> str:
    """Render a section header with optional action."""
    icon_html = render_svg(icon, 24) if icon else ""
    return textwrap.dedent(f'''
    <div class="flex justify-between items-start mb-2">
        <div>
            <div class="flex items-center gap-1">
                {icon_html}
                <h2 style="margin: 0;">{_escape_html(title)}</h2>
            </div>
            {f'<p class="text-secondary" style="margin-top: 0.25rem;">{_escape_html(subtitle)}</p>' if subtitle else ""}
        </div>
        {f'<span class="text-accent" style="font-size: 0.875rem;">{_escape_html(action)}</span>' if action else ""}
    </div>
    ''').replace("\n", "").strip()