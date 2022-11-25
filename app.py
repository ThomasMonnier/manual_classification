import base64
import shutil

import streamlit as st

st.set_page_config(layout="wide")


list_languages = ['French', 'Spanish', 'Italian', 'Catalan', 'Other']
list_verticals = ['Electricity', 'Gas', 'Heat', 'Ambigous', 'Other']
list_suppliers_fr = sorted(['EDF', 'Eni', 'ENGIE', 'Gaz Europeen', 'Sowee', 'Dyneff', 'Ekwateur', 'Mega Energie', 'Total Energies', 'other'])
list_suppliers_es = sorted(['Endesa', 'Iberdrola', 'Holaluz', 'Fenie', 'Energia XXI', 'Naturgy', 'Total Energies', 'Alcanzia', 'Aldoro', 'Audax', 'Bonpreu Esclat', 'Catllum', 'DRK Energia', 'EDP', 'Energy GO', 'FC Energia', 'Gana Energia', 'Gesternova', 'Nabalia', 'Podo', 'Repsol', 'Solelec', 'Somenergia', 'Catgas', 'Gas Natural Fenosa', 'Emivasa', 'other'])
list_suppliers_it = sorted(['Enel', 'Plenitude', 'A2A', 'Repower', 'Iren', 'Acea Energia', 'Sorgenia', 'Gas Sales Energia', 'Wekiwi', 'SEN', 'Edison', 'Hera Comm', 'Axpo', 'Metaenergia', 'Milano Gas e Luce'])
list_suppliers_all = sorted(list(set(list_suppliers_fr + list_suppliers_es + list_suppliers_it)))

dict_languages = {'French': 'fr', 'Spanish': 'es', 'Italian': 'it', 'Catalan': 'es', 'Other': 'other'}
dict_verticals = {'Electricity': 'electricity', 'Gas': 'gas', 'Heat': 'heat', 'Ambigous': 'other', 'Other': 'other'}
dict_suppliers = {'French': list_suppliers_fr, 'Spanish': list_suppliers_es, 'Catalan': list_suppliers_es, 'Italian': list_suppliers_it, 'Other': ['Other']}


def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="600" height="600" type="application/pdf"></iframe>'
    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def action():
    st.session_state.index += 1


if __name__ == "__main__":
    st.markdown(
        "<h1 style='text-align: center; color: green;'>Manual Classification</h1>",
        unsafe_allow_html=True,
    )
    st.write(
        "With this API, you can import one or more invoice(s) (PDF). You will have to identify its country, then its supplier, and then its energy type. Save the information and send the invoice to the S3."
    )

    uploaded_files = st.file_uploader(
        "Upload a file (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        progress_bar = st.progress(0)

        if "index" not in st.session_state:
            st.session_state.index = 0
        
        uploaded_file = uploaded_files[st.session_state.index]

        with open(uploaded_file.name, "wb") as buffer:
            shutil.copyfileobj(uploaded_file, buffer)
        
        col1, col2 = st.columns(2)
        
        with col1:
            displayPDF(uploaded_file.name)
        
        with col2:
            st.session_state.language = st.selectbox(
                'Select the language of the invoice',
                (el for el in list_languages),
            )

            st.session_state.vertical = st.selectbox(
                'Select the vertical of the invoice',
                (el for el in list_verticals)
            )

            list_suppliers = dict_suppliers[st.session_state.language]
            st.session_state.supplier = st.selectbox(
                'Select the supplier of the invoice',
                (el for el in list_suppliers)
            )

            validate = st.button('Validate')

            if validate:
                st.success("Path in S3: {}/{}/{}".format(
                    dict_languages.get(st.session_state.language),
                    st.session_state.supplier.lower().replace(' ', '_'),
                    dict_verticals.get(st.session_state.vertical)
                ))
                
                if st.session_state.index + 1 < len(uploaded_files):
                    next = st.button('Next', on_click=action)
                
                else:
                    st.info('All invoices have been processed ({} invoices)'.format(len(uploaded_files)))

            progress_bar.progress(int(100 * (st.session_state.index + 1) / len(uploaded_files)))
