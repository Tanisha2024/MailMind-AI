import streamlit as st

from llm import (
    analyze_email,
    generate_reply,
    handle_tool_request,
    load_emails,
    save_email,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MailMind AI",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Analyze"

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "current_email" not in st.session_state:
    st.session_state.current_email = ""

if "reply" not in st.session_state:
    st.session_state.reply = ""

if "selected_email" not in st.session_state:
    st.session_state.selected_email = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("📧 MailMind AI")
    st.caption("Your intelligent email copilot")

    st.divider()

    if st.button(
        "🧠 Analyze Email",
        use_container_width=True
    ):
        st.session_state.page = "Analyze"

    if st.button(
        "📥 Inbox",
        use_container_width=True
    ):
        st.session_state.page = "Inbox"

    if st.button(
        "⭐ Important",
        use_container_width=True
    ):
        st.session_state.page = "Important"

    if st.button(
        "ℹ️ About",
        use_container_width=True
    ):
        st.session_state.page = "About"

    st.divider()

    emails = load_emails()

    important_count = sum(
        1
        for email in emails
        if str(
            email.get("priority", "")
        ).lower()
        in ["high", "urgent", "critical"]
    )

    st.metric(
        "⭐ Important",
        important_count
    )

    st.divider()

    st.success("🟢 Groq Connected")

    st.caption("AI engine ready")


# =========================================================
# ANALYZE PAGE
# =========================================================

if st.session_state.page == "Analyze":

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    title_col, status_col = st.columns(
        [5, 1]
    )

    with title_col:

        st.title("📧 MailMind AI")

        st.subheader(
            "Your AI-powered email copilot"
        )

        st.caption(
            "Understand emails. Extract actions. "
            "Generate replies."
        )

    with status_col:

        st.write("")

        st.success("AI Ready")


    st.divider()


    # -----------------------------------------------------
    # EMAIL INPUT
    # -----------------------------------------------------

    st.header("📨 Analyze an Email")

    st.caption(
        "Paste an email below and MailMind will "
        "analyze its meaning and importance."
    )

    with st.container(border=True):

        email = st.text_area(
            "Email",
            height=240,
            placeholder=(
                "Paste the email you received here..."
            ),
            label_visibility="collapsed"
        )

        button_col, clear_col = st.columns(
            [3, 1]
        )

        with button_col:

            analyze_clicked = st.button(
                "✨ Analyze Email",
                type="primary",
                use_container_width=True
            )

        with clear_col:

            clear_clicked = st.button(
                "🗑️ Clear",
                use_container_width=True
            )


    # -----------------------------------------------------
    # CLEAR
    # -----------------------------------------------------

    if clear_clicked:

        st.session_state.analysis = None
        st.session_state.current_email = ""
        st.session_state.reply = ""

        st.rerun()


    # -----------------------------------------------------
    # ANALYZE
    # -----------------------------------------------------

    if analyze_clicked:

        if not email.strip():

            st.warning(
                "Please paste an email first."
            )

        else:

            with st.spinner(
                "🧠 MailMind is analyzing your email..."
            ):

                try:

                    result = analyze_email(
                        email
                    )

                    st.session_state.analysis = result
                    st.session_state.current_email = email

                except Exception as e:

                    st.error(
                        f"Analysis failed: {e}"
                    )


    # =====================================================
    # RESULTS
    # =====================================================

    if st.session_state.analysis:

        result = st.session_state.analysis

        st.divider()

        st.header("✨ Email Intelligence")

        category = result.get(
            "category",
            "Unknown"
        )

        priority = result.get(
            "priority",
            "Unknown"
        )

        summary = result.get(
            "summary",
            "No summary available."
        )

        actions = result.get(
            "action_items",
            []
        )

        suggested_reply = result.get(
            "suggested_reply",
            ""
        )


        # -------------------------------------------------
        # TOP INFORMATION
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🏷️ Category",
                category
            )

        with col2:

            st.metric(
                "🚨 Priority",
                priority
            )

        with col3:

            st.metric(
                "✅ Action Items",
                len(actions)
            )


        st.write("")


        # -------------------------------------------------
        # MAIN RESULT LAYOUT
        # -------------------------------------------------

        left, right = st.columns(
            [1.5, 1]
        )


        # SUMMARY
        with left:

            with st.container(border=True):

                st.subheader(
                    "📌 AI Summary"
                )

                st.write(summary)


        # ACTIONS
        with right:

            with st.container(border=True):

                st.subheader(
                    "✅ Action Items"
                )

                if actions:

                    for index, action in enumerate(
                        actions
                    ):

                        st.checkbox(
                            action,
                            key=f"action_{index}"
                        )

                else:

                    st.success(
                        "No action items detected."
                    )


        st.write("")


        # -------------------------------------------------
        # REPLY SECTION
        # -----------------------------------------------------

        with st.container(border=True):

            st.subheader(
                "✉️ Suggested Reply"
            )

            st.text_area(
                "AI reply",
                value=suggested_reply,
                height=230,
                label_visibility="collapsed"
            )


        st.write("")


        # -------------------------------------------------
        # ACTION BAR
        # -----------------------------------------------------

        col1, col2, col3 = st.columns(3)


        # SAVE
        with col1:

            if st.button(
                "💾 Save Email",
                use_container_width=True
            ):

                try:

                    save_result = save_email(
                        email_text=(
                            st.session_state.current_email
                        ),
                        category=result["category"],
                        priority=result["priority"],
                        summary=result["summary"]
                    )

                    st.success(
                        save_result["message"]
                    )

                except Exception as e:

                    st.error(
                        f"Save failed: {e}"
                    )


        # FRESH REPLY
        with col2:

            if st.button(
                "⚡ Generate Fresh Reply",
                use_container_width=True
            ):

                placeholder = st.empty()

                full_reply = ""

                try:

                    for chunk in generate_reply(
                        st.session_state.current_email
                    ):

                        full_reply += chunk

                        placeholder.text_area(
                            "Generating reply...",
                            value=full_reply,
                            height=230
                        )

                except Exception as e:

                    st.error(
                        f"Reply generation failed: {e}"
                    )


        # SMART ACTION
        with col3:

            if st.button(
                "🤖 Smart Action",
                use_container_width=True
            ):

                with st.spinner(
                    "Checking possible actions..."
                ):

                    try:

                        response = handle_tool_request(
                            st.session_state.current_email
                        )

                        st.success(
                            response
                        )

                    except Exception as e:

                        st.error(
                            f"Smart action failed: {e}"
                        )


        # -------------------------------------------------
        # ORIGINAL EMAIL
        # -------------------------------------------------

        with st.expander(
            "📨 View Original Email"
        ):

            st.text(
                st.session_state.current_email
            )


# =========================================================
# INBOX
# =========================================================

elif st.session_state.page == "Inbox":

    st.title("📥 Inbox")

    st.caption(
        "Your saved emails and AI insights."
    )

    emails = load_emails()


    # -----------------------------------------------------
    # STATS
    # -----------------------------------------------------

    total = len(emails)

    important = sum(
        1
        for email in emails
        if str(
            email.get("priority", "")
        ).lower()
        in ["high", "urgent", "critical"]
    )

    category_count = len(
        set(
            email.get("category")
            for email in emails
            if email.get("category")
        )
    )


    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📧 Total Emails",
            total
        )

    with col2:

        st.metric(
            "🚨 Important",
            important
        )

    with col3:

        st.metric(
            "🏷️ Categories",
            category_count
        )


    st.divider()


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = st.text_input(
        "🔎 Search inbox",
        placeholder="Search by email content or summary..."
    )


    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    categories = sorted(
        set(
            email.get("category")
            for email in emails
            if email.get("category")
        )
    )

    priorities = sorted(
        set(
            email.get("priority")
            for email in emails
            if email.get("priority")
        )
    )


    col1, col2 = st.columns(2)

    with col1:

        selected_category = st.selectbox(
            "Category",
            ["All"] + categories
        )

    with col2:

        selected_priority = st.selectbox(
            "Priority",
            ["All"] + priorities
        )


    # -----------------------------------------------------
    # FILTER
    # -----------------------------------------------------

    filtered = []

    for email_data in emails:

        email_text = email_data.get(
            "email",
            ""
        ).lower()

        summary_text = email_data.get(
            "summary",
            ""
        ).lower()


        if search:

            query = search.lower()

            if (
                query not in email_text
                and query not in summary_text
            ):
                continue


        if (
            selected_category != "All"
            and email_data.get(
                "category"
            ) != selected_category
        ):
            continue


        if (
            selected_priority != "All"
            and email_data.get(
                "priority"
            ) != selected_priority
        ):
            continue


        filtered.append(email_data)


    st.caption(
        f"{len(filtered)} email(s) found"
    )


    # -----------------------------------------------------
    # EMAIL LIST
    # -----------------------------------------------------

    for index, email_data in enumerate(
        reversed(filtered)
    ):

        category = email_data.get(
            "category",
            "Email"
        )

        priority = email_data.get(
            "priority",
            "Normal"
        )

        summary = email_data.get(
            "summary",
            "No summary available."
        )

        preview = summary[:100]

        if len(summary) > 100:
            preview += "..."


        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [1.4, 4, 1]
            )

            with col1:

                st.write(
                    f"### {category}"
                )

                st.caption(
                    f"🚨 {priority}"
                )

            with col2:

                st.write(
                    f"**{preview}**"
                )

                st.caption(
                    email_data.get(
                        "saved_at",
                        ""
                    )
                )

            with col3:

                if st.button(
                    "Open",
                    key=f"open_{index}",
                    use_container_width=True
                ):

                    st.session_state.selected_email = (
                        email_data
                    )

                    st.rerun()


    # -----------------------------------------------------
    # SELECTED EMAIL
    # -----------------------------------------------------

    if st.session_state.selected_email:

        selected = (
            st.session_state.selected_email
        )

        st.divider()

        st.header("📨 Email")

        col1, col2 = st.columns(
            [2, 1]
        )

        with col1:

            st.subheader(
                selected.get(
                    "category",
                    "Email"
                )
            )

        with col2:

            st.metric(
                "Priority",
                selected.get(
                    "priority",
                    "Normal"
                )
            )


        with st.container(border=True):

            st.subheader(
                "🧠 MailMind Summary"
            )

            st.write(
                selected.get(
                    "summary",
                    "No summary."
                )
            )


        with st.expander(
            "📨 Original Email",
            expanded=True
        ):

            st.text(
                selected.get(
                    "email",
                    ""
                )
            )


# =========================================================
# IMPORTANT
# =========================================================

elif st.session_state.page == "Important":

    st.title("⭐ Important Emails")

    st.caption(
        "High-priority messages that need your attention."
    )

    emails = load_emails()

    important_emails = [
        email
        for email in emails
        if str(
            email.get(
                "priority",
                ""
            )
        ).lower()
        in [
            "high",
            "urgent",
            "critical"
        ]
    ]


    if not important_emails:

        st.success(
            "🎉 You're all caught up!"
        )

    else:

        for email_data in reversed(
            important_emails
        ):

            with st.container(border=True):

                st.subheader(
                    f"🚨 "
                    f"{email_data.get('category', 'Important Email')}"
                )

                st.write(
                    email_data.get(
                        "summary",
                        "No summary available."
                    )
                )

                st.caption(
                    f"Priority: "
                    f"{email_data.get('priority', 'High')}"
                )


# =========================================================
# ABOUT
# =========================================================

elif st.session_state.page == "About":

    st.title("ℹ️ About MailMind AI")

    st.subheader(
        "Your AI-powered email copilot."
    )

    st.write(
        "MailMind AI uses an LLM to understand emails, "
        "detect important actions, generate replies, "
        "and organize your inbox."
    )

    st.divider()

    st.header("🚀 Features")

    col1, col2 = st.columns(2)

    with col1:

        st.write("🧠 Email Analysis")
        st.write("📝 Email Summarization")
        st.write("🏷️ Email Classification")
        st.write("🚨 Priority Detection")

    with col2:

        st.write("✅ Action Extraction")
        st.write("✉️ Reply Generation")
        st.write("⚡ Streaming Replies")
        st.write("🤖 Smart Actions")

    st.divider()

    st.header("🛠️ Tech Stack")

    st.write(
        "Python • Streamlit • Groq • LLM APIs"
    )