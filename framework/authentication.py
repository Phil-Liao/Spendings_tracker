
import streamlit as st
from streamlit_oauth import OAuth2Component



def authenticate_user() -> bool:
    """
    Prompt the user for a password to authenticate.
    """
    st.session_state["authenticated"] = False
    email = st.text_input("Enter your email address:")
    password = st.text_input("Enter password to access the application:", type="password")

    submit_button = st.button("Submit")
    st.write("Or sign in with Google:")
    oauth2 = OAuth2Component(
        client_id=st.secrets.google_oauth.client_id,
        client_secret=st.secrets.google_oauth.client_secret,
        authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
        token_endpoint="https://oauth2.googleapis.com/token",
    )
    result = oauth2.authorize_button(
        

        "Sign in with Google",
        redirect_uri="https://spendings-tracker.streamlit.app/",
        scope="openid email profile",
        key="google"
    )

    if submit_button:
        if (password == st.secrets.login.password) and (email == st.secrets.login.email):
            st.session_state["authenticated"] = True
            st.success("Authentication successful!")
            return True
        elif email:
            st.error("Email address not registered. Please try again.")
        elif password:
            st.error("Incorrect password. Please try again.")

    if result and "token" in result:
        # Restrict access to only cheweiphil@gmail.com
        user_email = result.get("user", {}).get("email") or result.get("email")
        if user_email == st.secrets.login.email:
            st.session_state["authenticated"] = True
            st.success("Authenticated with Google!")
            return True
        else:
            st.error("Only certain accounts is allowed to sign in with Google.")

    return False
