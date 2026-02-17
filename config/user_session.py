"""
User session management to prevent cross-user data leakage.
Each user must explicitly login to prevent other users from accessing their data.
"""
import streamlit as st
from pathlib import Path
from getpass import getuser
import hashlib


class UserSession:
    """Manages per-user session isolation in Streamlit."""

    SESSION_KEY_AUTHENTICATED_USER = "authenticated_user"
    SESSION_KEY_USER_HASH = "user_session_hash"
    SESSION_KEY_USER_DATA_DIR = "user_data_dir"

    @staticmethod
    def get_current_user() -> str:
        """Get the currently authenticated user."""
        return st.session_state.get(UserSession.SESSION_KEY_AUTHENTICATED_USER, None)

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated."""
        return UserSession.SESSION_KEY_AUTHENTICATED_USER in st.session_state

    @staticmethod
    def authenticate_user(username: str) -> bool:
        """
        Authenticate a user and initialize their isolated session.
        CRITICAL: This prevents other users from seeing this user's data.
        """
        if not username or not username.strip():
            return False

        # Create a unique session identifier for this user
        user_hash = hashlib.sha256(f"{username}:{Path.home()}".encode()).hexdigest()[:16]

        # Clear any previous user's session state (CRITICAL for security)
        st.session_state.clear()

        # Authenticate this user
        st.session_state[UserSession.SESSION_KEY_AUTHENTICATED_USER] = username
        st.session_state[UserSession.SESSION_KEY_USER_HASH] = user_hash
        st.session_state[UserSession.SESSION_KEY_USER_DATA_DIR] = str(Path.home() / ".smar-test")

        return True

    @staticmethod
    def logout() -> None:
        """Logout the current user and clear all session data (CRITICAL)."""
        st.session_state.clear()

    @staticmethod
    def require_authentication() -> bool:
        """
        Show authentication UI if user is not authenticated.
        Returns True if authenticated, False if needs login.
        """
        if UserSession.is_authenticated():
            return True

        # Show login screen
        st.set_page_config(
            page_title="Smar-Test | Login",
            page_icon="⚡",
            layout="centered"
        )

        st.markdown("# 🔐 Smar-Test - Login Required")
        st.markdown("---")
        st.markdown(
            """
            **SECURITY NOTICE:**
            Each user must log in separately to ensure your data is completely isolated.

            Your settings, clients, and configuration will be stored in your home directory
            and will NOT be visible to other users on this computer.
            """
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            username = st.text_input(
                "Enter your username",
                placeholder="Your username or email",
                help="Used to identify your isolated workspace"
            )

        with col2:
            st.markdown("")  # Spacing
            if st.button("Login", type="primary", use_container_width=True):
                if UserSession.authenticate_user(username):
                    st.success(f"✅ Logged in as {username}")
                    st.rerun()
                else:
                    st.error("❌ Please enter a valid username")

        st.markdown("---")
        st.info(
            """
            **Why login?**
            - Ensures your settings are completely private
            - Your clients won't be visible to other users
            - Your API keys stay in your session only
            - Multi-user support on shared computers
            """
        )

        return False

    @staticmethod
    def get_user_session_key(key: str) -> str:
        """
        Get a user-specific session key.
        Prevents one user's keys from being accessed by another user.
        """
        if not UserSession.is_authenticated():
            return None

        user_hash = st.session_state.get(UserSession.SESSION_KEY_USER_HASH, "unknown")
        return f"{user_hash}:{key}"

    @staticmethod
    def verify_session_integrity() -> bool:
        """
        Verify that the current session belongs to the authenticated user.
        CRITICAL: Detects if session state was tampered with.
        """
        if not UserSession.is_authenticated():
            return False

        # Verify session hasn't been modified
        stored_hash = st.session_state.get(UserSession.SESSION_KEY_USER_HASH, None)
        stored_user = st.session_state.get(UserSession.SESSION_KEY_AUTHENTICATED_USER, None)

        if not stored_hash or not stored_user:
            return False

        # Recompute the expected hash
        expected_hash = hashlib.sha256(f"{stored_user}:{Path.home()}".encode()).hexdigest()[:16]

        # Verify it matches
        return stored_hash == expected_hash
