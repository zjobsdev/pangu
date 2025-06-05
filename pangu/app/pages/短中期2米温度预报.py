# -*- coding: utf-8 -*-
# @Author: wqshen
# @Email: wqshen91@gmail.com
# @Date: 2022/10/21 9:51
# @Last Modified by: wqshen

import streamlit as st
from glob import glob
from datetime import time, datetime, timedelta

st.set_page_config(layout="wide", )
h1_title = '<h1 style="font-size: 30px;">PANGU大模型预报2米气温</h1>'
st.markdown(h1_title, unsafe_allow_html=True)

nowtime = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(hours=8)
if nowtime.time() > time(14, 30):
    it = nowtime.replace(hour=0, minute=0)
elif nowtime.time() > time(2, 30):
    it = nowtime.replace(hour=12, minute=0) - timedelta(hours=1)
else:
    it = nowtime.replace(hour=12, minute=0) - timedelta(hours=1)

pf_list = sorted(glob('../output/*/pangu.*.t2m.png'))
inittime_list = [pf.split('.')[-4] for pf in pf_list]
inittime_str = st.sidebar.selectbox("起报时间", inittime_list, index=len(inittime_list) - 1)
it = datetime.strptime(inittime_str, '%Y%m%d%H')


h2_title = '<h2 style="font-size: 24px;">1-84小时逐小时2米气温预报</h2>'
st.markdown(h2_title, unsafe_allow_html=True)

step = 1
fh_max = 84
forecast_time = st.slider(
    "预报时间（北京时）",
    min_value=it + timedelta(hours=step),
    max_value=it + timedelta(hours=fh_max),
    value=it + timedelta(hours=step),
    step=timedelta(hours=step),
    format='YYYY年MM月DD日HH时',
    key='same',
)
fh = int((forecast_time - it).total_seconds()/3600)
images = [f'../output/{it:%Y%m%d%H}/pangu.{inittime_str}.{fh:03d}.t2m.png']
st.image(images, caption=['2米气温填色、填值'])

h2_title = '<h2 style="font-size: 24px;">6-360小时逐3小时2米气温预报</h2>'
st.markdown(h2_title, unsafe_allow_html=True)

step = 3
fh_max = 360
forecast_time = st.slider(
    "预报时间（北京时）",
    min_value=it + timedelta(hours=step),
    max_value=it + timedelta(hours=fh_max),
    value=it + timedelta(hours=step),
    step=timedelta(hours=step),
    format='YYYY年MM月DD日HH时',
    key='step6',
)
fh = int((forecast_time - it).total_seconds()/3600)
images = [f'../output/{it:%Y%m%d%H}/pangu.{inittime_str}.{fh:03d}.t2m.png']
st.image(images, caption=['2米气温填色、填值'])
