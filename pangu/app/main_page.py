# -*- coding: utf-8 -*-
# @Author: wqshen
# @Email: wqshen91@gmail.com
# @Date: 2022/10/21 9:51
# @Last Modified by: wqshen

import os
import streamlit as st
from datetime import time, datetime, timedelta

st.set_page_config(layout="wide", )
h1_title = '<h1 style="font-size: 30px;">PANGU大模型预报</h1>'
st.markdown(h1_title, unsafe_allow_html=True)
st.sidebar.markdown('# 主页')

h2_title = '<h2 style="font-size: 24px;">基于ECMWF D1D分析场数据驱动PANGU模型的短中期天气预报</h2>'
st.markdown(h2_title, unsafe_allow_html=True)

nowtime = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(hours=8)
if nowtime.time() > time(14, 30):
    it = nowtime.replace(hour=0, minute=0)
elif nowtime.time() > time(2, 30):
    it = nowtime.replace(hour=12, minute=0) - timedelta(hours=1)
else:
    it = nowtime.replace(hour=12, minute=0) - timedelta(hours=1)

inittime_list = os.listdir('../output')
inittime_str = st.sidebar.selectbox("起报时间", inittime_list, index=len(inittime_list)-1)
step = 1
fh_max = 84
it = datetime.strptime(inittime_str, '%Y%m%d%H')
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


h2_title = '<h3 style="font-size: 18px;">500hPa高度场、850hPa相对湿度+风场</h2>'
st.markdown(h2_title, unsafe_allow_html=True)
images = [f'../output/{it:%Y%m%d%H}/pangu.{inittime_str}.{fh:03d}.h500uvr850.L.png',
          f'../output/{it:%Y%m%d%H}/pangu.{inittime_str}.{fh:03d}.h500uvr850.S.png']
captions = ['全国500hPa高度场（等值线）+850hPa风场+850hPa相对湿度场（填色）',
            '浙江区域500hPa高度场（等值线）+850hPa风场+850hPa相对湿度场（填色）',]
st.image(images, width=580, caption=captions)

h2_title = '<h3 style="font-size: 18px;">500hPa高度场、925hPa相对湿度+风场</h2>'
st.markdown(h2_title, unsafe_allow_html=True)
images = [f'../output/{it:%Y%m%d%H}/pangu.{inittime_str}.{fh:03d}.h500uvr925.L.png',
          f'../output/{it:%Y%m%d%H}/pangu.{inittime_str}.{fh:03d}.h500uvr925.S.png']
captions = ['全国500hPa高度场（等值线）+925hPa风场+925hPa相对湿度场（填色）',
            '浙江区域500hPa高度场（等值线）+925hPa风场+925hPa相对湿度场（填色）',]
st.image(images, width=580, caption=captions)

h2_title = '<h3 style="font-size: 18px;">500hPa高度场、相对湿度+风场</h2>'
st.markdown(h2_title, unsafe_allow_html=True)
images = [f'../output/{it:%Y%m%d%H}/pangu.{inittime_str}.{fh:03d}.h500uvr500.L.png',
          f'../output/{it:%Y%m%d%H}/pangu.{inittime_str}.{fh:03d}.h500uvr500.S.png']
captions = ['全国500hPa高度场（等值线）+500hPa风场+500hPa相对湿度场（填色）',
            '浙江区域500hPa高度场（等值线）+500hPa风场+500hPa相对湿度场（填色）',]
st.image(images, width=580, caption=captions)
