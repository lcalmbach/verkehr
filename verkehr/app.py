import streamlit as st
import numpy as np
import traffic
import config as cn
import tools

tr = traffic.Traffic('Info Datensatz')
st.sidebar.markdown('# 🧮<span style="color:steelblue">Mobility Explorer BS</span>', unsafe_allow_html=True)
st.sidebar.markdown('<small> MobEx.bs version: {}</small>'.format(traffic.__version__), unsafe_allow_html=True)
st.sidebar.markdown('### Menu')

tr.traffic_type = st.sidebar.selectbox('Verkehrsart', index=0,
                   options=list(cn.traffic_type_dic.keys()),
                   format_func=lambda x: cn.traffic_type_dic[x])

menu = st.sidebar.radio(label='', index=0, options=cn.menu_list)
print(menu)
if menu == 'Info Datensatz':
    tr.show_dataset_info()
    tr.show_about_box()
elif menu == 'Statistik':
    tr.result_type = menu
    tr.show_sidebar_controls()
    tr.show_results()
elif menu == 'Grafiken':
    tr.result_type = st.sidebar.selectbox("Grafik-Typ", index=0, options=cn.plot_type_list)
    tr.show_sidebar_controls()
    tr.show_results()

tr.show_help_icon()
