import streamlit as st
from tkinter.tix import COLUMN
from pyparsing import empty
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.offline as pyo #plotly 그래프가 주피터 노트북에서 안나올때 실행
import plotly.graph_objects as go
import plotly.figure_factory as ff
from skimage import io # 이미지 처리 라이브러리
from IPython.display import Image # gif 처리 라이브러리?
from IPython.display import HTML, display
import base64
from glob import glob

from src.plot_utils import * # 경기장 시각화해주는 코드, 공식 라이브러리 X, 해당 프로젝트의 plot_utils.py을 import
from streamlit_function import *
import time

# st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>축구 데이터 시각화 시스템</h1>", unsafe_allow_html=True)

empty1,col1,empty2 = st.columns([0.3,0.5,0.3])
empty1,col2,empty2 = st.columns([0.3,0.5,0.3])
empty1,col3,empty2 = st.columns([0.3,0.5,0.3])

empty1 = st.empty()
empty2 = st.empty()

players_data = pd.read_pickle('user_pickle/player_name_match_id.pkl')
matchs_data = pd.read_pickle('user_pickle/match_id_team_name.pkl')

players_name = st.selectbox(
    '보고 싶은 선수를 선택해주세요.',
    options=players_data.player_name.drop_duplicates(),
    index=None,
    placeholder="Select player name")

players_event_type = st.selectbox(
        '이벤트 유형을 선택해주세요.',
        options=('Pass', 'Shot', 'Goal'),
        index=None,
        placeholder="Select players event_type"
    )

players_match = st.selectbox(
        '시각화할 경기를 선택해주세요.',
        options=match_id_input(player_input(players_name)),
        index=None,
        placeholder="Select players event_type"
    )

match_id = match_id_return(player_input(players_name),players_match)
match_events = pd.read_pickle(f'data/refined_events/World_Cup/{match_id}.pkl')

team1_name, team2_name = match_events['team_name'].unique()

match_events['display_time'] = match_events.apply( #람다 표현식
    lambda x: f"{x['period']} {int(x['time'] // 60):02d}:{int(x['time'] % 60):02d}", axis=1)

group_dict = {
    players_name: 'red'
}

# 이벤트 유형별 시각화 함수
if players_event_type!=None and players_match!=None:
    if players_event_type == 'Goal':
        sam = pd.DataFrame()
        for i in range(0, len(match_events)):
            if match_events['event_type'][i] == 'Shot':
                if match_events['tags'][i][0] == 'Goal':
                    sam = pd.concat([sam, match_events.loc[i].to_frame().transpose()], axis=0)
            elif match_events['event_type'][i] == 'Free kick':
                if len(match_events['tags'][i]) > 1 and match_events['tags'][i][0] == 'Goal':
                    sam = pd.concat([sam, match_events.loc[i].to_frame().transpose()], axis=0)
        if sam.empty: 
            st.write('해당 경기에 골 데이터가 없습니다.')
        else:             
            fig = plot_events_goal(sam, col_name='player_name', group_dict=group_dict, 
                           team1_name=team1_name, team2_name=team2_name, event_type='Goal')
            st.plotly_chart(fig, use_container_width=True)

            with st.spinner('Wait for it...'):
                time.sleep(2)
            
            search_query = f'2018 world cup {players_name} {players_event_type} {players_match}'
            if search_query:
                search_url = f'https://www.youtube.com/results?search_query={search_query}'
                st.components.v1.iframe(search_url, width=800, height=700)

    else:
        fig = plot_events(match_events, col_name='player_name', group_dict=group_dict, 
                               team1_name=team1_name, team2_name=team2_name ,event_type=players_event_type)
        st.plotly_chart(fig, use_container_width=True)


# st.button("Reset", type="primary")
# if st.button('Say hello'):
#     st.write('Why hello there')
# else:
#     st.write('Goodbye')
# 시각화 함수의 input으로 player_input함수(player_data.match_id 리턴)사용
# st.write('You selected:', match_id_input(player_input(players_name)))

# 슛은 전꺼(방향 화살표 나오는거)로 띄우기
# 패스는 화살표 나오게 띄우되 반응 제거
# 골은 동그라미로 나오게하고 골 영상 즉시 실행