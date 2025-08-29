import streamlit as st

class NavBar:
    pages = {"Home": "main.py",
            "Spendings": "pages/spendings.py",
            "Income": "pages/income.py",
            "Settings": "pages/settings.py"}
    def __init__(self, pages:dict=pages) -> None:
        self.pages = pages

    def render(self):
        cols = st.columns([25, 25, 25, 25], gap="small")  # Adjust column widths to make buttons wider and closer
        selected_page = None

        for i, (page_name, page_key) in enumerate(self.pages.items()):
            if cols[i].button(page_name, use_container_width=True):
                selected_page = page_key
                st.switch_page(selected_page)
                break

