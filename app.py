# streamlit_app.py

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1676BtnMSE1K1pcmId3ddjX6y-2pVXb70GsI1sp_I1d8"
SHEET_NAME = "Database"
SHEET_URL = st.secrets["private_gsheets_url"]

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[SCOPE],
)

service = build("sheets", "v4", credentials=credentials)
sheet = service.spreadsheets()


def get_data():
    values = (
        sheet.values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:C",
        )
        .execute()
    )

    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]
    return df


def add_row_to_gsheet(row):
    values = (
        sheet.values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:C",
            body=dict(values=row),
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )


if __name__ == "__main__":
    st.set_page_config(page_title="Bug report", page_icon="🐞", layout="centered")
    st.title("🐞 Bug report!")

    st.sidebar.write(
        "This app is intended to show how a Streamlit app can interact easily with a [Google Sheet](https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}) to read or store data."
    )

    form = st.form(key="annotation")

    with form:
        cols = st.columns((1, 1))
        author = cols[0].text_input("Author:")
        bug_type = cols[1].selectbox(
            "Bug type:", ["Front-end", "Back-end", "Data related", "404"], index=2
        )
        comment = st.text_input("Comment:", "\n\n\n \n\n\n")
        submitted = st.form_submit_button(label="Submit")

    if submitted:
        add_row_to_gsheet([[author, bug_type, comment]])
        st.success("Thanks! Your bug was recorded.")
        st.balloons()

    expander = st.expander("See all records")
    with expander:
        st.table(get_data())
