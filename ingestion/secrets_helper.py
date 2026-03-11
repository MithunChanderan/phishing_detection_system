import os
import json
import tempfile
import streamlit as st

def get_gmail_credential_paths() -> tuple[str, str]:
    """
    Returns (credentials_path, token_path) as temp file paths.
    Works both locally and on Streamlit Cloud.
    """
    try:
        if hasattr(st, "secrets") and "gmail_credentials" in st.secrets:
            secrets = st.secrets["gmail_credentials"]
            
            if "credentials_json" not in secrets:
                raise KeyError("credentials_json details missing from st.secrets['gmail_credentials']")
            if "token_json" not in secrets:
                raise KeyError("token_json details missing from st.secrets['gmail_credentials']")
                
            creds_str = secrets["credentials_json"]
            token_str = secrets["token_json"]
            
            json.loads(creds_str)
            json.loads(token_str)
            
            tmp_dir = tempfile.gettempdir()
            credentials_path = os.path.join(tmp_dir, "credentials.json")
            token_path = os.path.join(tmp_dir, "token.json")
            
            with open(credentials_path, "w") as f:
                f.write(creds_str)
            with open(token_path, "w") as f:
                f.write(token_str)
                
            return credentials_path, token_path
            
    except KeyError as e:
        st.error(f"Missing Secret Key: {e}. Please add it to your Streamlit Cloud Secrets.")
        st.stop()
    except json.JSONDecodeError as e:
        st.error(f"Malformed JSON in Streamlit Secrets: {e}. Please ensure your JSON is valid.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading credentials from secrets: {e}")
        st.stop()
        
    return "credentials.json", "token.json"
