# -*- coding: utf-8 -*-
# @Author: wqshen
# @Email: wqshen91@gmail.com
# @Date: 2022/10/21 9:51
# @Last Modified by: wqshen

import os
import streamlit as st
from datetime import time, datetime, timedelta

st.set_page_config(layout="wide", )
h1_title = '<h1 style="font-size: 30px;">PANGU大模型预报稳定性</h1>'
st.markdown(h1_title, unsafe_allow_html=True)
st.sidebar.markdown('# 模型稳定性')

h2_title = '<h2 style="font-size: 24px;">PANGU模型不同起报时次预报的比较</h2>'
st.markdown(h2_title, unsafe_allow_html=True)

nowtime = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(hours=8)
if nowtime.time() > time(14, 30):
    it = nowtime.replace(hour=0, minute=0)
elif nowtime.time() > time(2, 30):
    it = nowtime.replace(hour=12, minute=0) - timedelta(hours=1)
else:
    it = nowtime.replace(hour=12, minute=0) - timedelta(hours=1)


inittime_list = sorted(os.listdir('../output'))
inittime_str = st.sidebar.selectbox("起报时间", inittime_list, index=len(inittime_list) - 1)
zone_name = st.sidebar.selectbox("区域", ['浙江区域', '全国'])
zone = 'S' if zone_name == '浙江区域' else 'L'

it_latest = datetime.strptime(inittime_str, '%Y%m%d%H')
it_last = it_latest - timedelta(hours=12)
step = 1
fh_min = 13
fh_max = 60

it = datetime.strptime(inittime_str, '%Y%m%d%H')
forecast_time = st.slider(
    "预报时间（北京时）",
    min_value=it_last + timedelta(hours=fh_min),
    max_value=it_latest + timedelta(hours=fh_max),
    value=it_last + timedelta(hours=fh_min),
    step=timedelta(hours=step),
    format='YYYY年MM月DD日HH时',
    key='same',
)
fh_latest = int((forecast_time - it_latest).total_seconds()/3600)
fh_last = int((forecast_time - it_last).total_seconds()/3600)

h2_title = '<h3 style="font-size: 18px;">500hPa高度场、850hPa相对湿度+风场</h2>'
st.markdown(h2_title, unsafe_allow_html=True)
images = [f'../output/{it_latest:%Y%m%d%H/pangu.%Y%m%d%H}.{fh_latest:03d}.h500uvr850.{zone}.png',
          f'../output/{it_last:%Y%m%d%H/pangu.%Y%m%d%H}.{fh_last:03d}.h500uvr850.{zone}.png']
captions = [f'{zone_name}500hPa高度场（等值线）+850hPa风场+850hPa相对湿度场（填色）',
            f'{zone_name}500hPa高度场（等值线）+850hPa风场+850hPa相对湿度场（填色）',]
st.image(images, width=660, caption=captions)

h2_title = '<h3 style="font-size: 18px;">500hPa高度场、925hPa相对湿度+风场</h2>'
st.markdown(h2_title, unsafe_allow_html=True)
images = [f'../output/{it_latest:%Y%m%d%H/pangu.%Y%m%d%H}.{fh_latest:03d}.h500uvr925.{zone}.png',
          f'../output/{it_last:%Y%m%d%H/pangu.%Y%m%d%H}.{fh_last:03d}.h500uvr925.{zone}.png']
captions = [f'{zone_name}500hPa高度场（等值线）+925hPa风场+925hPa相对湿度场（填色）',
            f'{zone_name}500hPa高度场（等值线）+925hPa风场+925hPa相对湿度场（填色）',]
st.image(images, width=660, caption=captions)

h2_title = '<h3 style="font-size: 18px;">500hPa高度场、相对湿度+风场</h2>'
st.markdown(h2_title, unsafe_allow_html=True)
images = [f'../output/{it_latest:%Y%m%d%H/pangu.%Y%m%d%H}.{fh_latest:03d}.h500uvr500.{zone}.png',
          f'../output/{it_last:%Y%m%d%H/pangu.%Y%m%d%H}.{fh_last:03d}.h500uvr500.{zone}.png']
captions = [f'{zone_name}500hPa高度场（等值线）+500hPa风场+500hPa相对湿度场（填色）',
            f'{zone_name}500hPa高度场（等值线）+500hPa风场+500hPa相对湿度场（填色）',]
st.image(images, width=660, caption=captions)
