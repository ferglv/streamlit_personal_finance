# backend/xml_processing/load_files.py
from typing import List

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from backend.xml_processing.xml_parser import parse_xml


def load_xmls(uploaded_files: List[UploadedFile]) -> List[dict]:
    """
    Processes a list of uploaded XML files, sorts them, parses each file,
    and displays their details in the Streamlit app.

    Args:
        uploaded_files (List[UploadedFile]): List of uploaded XML files.

    Returns:
        List[dict]: List of parsed data from each XML file.
    """
    if not uploaded_files:
        return []

    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    files_data = []

    for uploaded_file in sorted_files:
        try:
            data = parse_xml(uploaded_file)
            files_data.append(data)
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")

    if files_data:
        with st.expander("XML Files Details"):
            st.json(files_data)

    return files_data
