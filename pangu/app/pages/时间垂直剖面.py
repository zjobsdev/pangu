# -*- coding: utf-8 -*-
# @Author: wqshen
# @Email: wqshen91@gmail.com
# @Date: 2022/10/21 9:51
# @Last Modified by: wqshen

import streamlit as st
from glob import glob
from datetime import time, datetime, timedelta

st.set_page_config(layout="wide", )
h1_title = '<h1 style="font-size: 30px;">PANGU大模型预报站点时间垂直剖面</h1>'
st.markdown(h1_title, unsafe_allow_html=True)

nowtime = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(hours=8)
if nowtime.time() > time(14, 30):
    it = nowtime.replace(hour=0, minute=0)
elif nowtime.time() > time(2, 30):
    it = nowtime.replace(hour=12, minute=0) - timedelta(hours=1)
else:
    it = nowtime.replace(hour=12, minute=0) - timedelta(hours=1)

pf_list = sorted(glob('../output/*/pangu.*.ptsection.杭州.png'))
inittime_list = [pf.split('.')[-4] for pf in pf_list]
inittime_str = st.sidebar.selectbox("起报时间", inittime_list, index=len(inittime_list) - 1)

it_latest = datetime.strptime(inittime_str, '%Y%m%d%H')
pfs = glob(f'../output/{inittime_str}/pangu.{inittime_str}.ptsection*.png')
stations = [pf.split('.')[-2] for pf in pfs]
station_name = st.sidebar.selectbox("站点", stations, index=stations.index('杭州'))
idx = stations.index(station_name)


h2_title = f'<h3 style="font-size: 18px;">{station_name}站逐小时温度场、相对湿度和风场时间垂直剖面</h2>'
st.markdown(h2_title, unsafe_allow_html=True)
images = [pfs[idx]]
st.image(images, caption=[f'{station_name}站温度场、相对湿度和风场时间垂直剖面'])


pfs = glob(f'../output/{inittime_str}/pangu.{inittime_str}.ptsection*.3hourly.png')
stations = [pf.split('.')[-3] for pf in pfs]
idx = stations.index(station_name)


h2_title = f'<h3 style="font-size: 18px;">{station_name}站逐3小时温度场、相对湿度和风场时间垂直剖面</h2>'
st.markdown(h2_title, unsafe_allow_html=True)
images = [pfs[idx]]
st.image(images, caption=[f'{station_name}站温度场、相对湿度和风场时间垂直剖面'])
