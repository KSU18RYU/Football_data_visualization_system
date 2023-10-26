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

from src.plot_utils import * # 경기장 시각화해주는 코드, 공식 라이브러리 X, 해당 프로젝트의 plot_utils.py을 import

players_data = pd.read_pickle('user_pickle/player_name_match_id.pkl')
matchs_data = pd.read_pickle('user_pickle/match_id_team_name.pkl')

def player_input(player_name):
    data = players_data
    player_data = data[(data['player_name'] == player_name)]
    player_data.reset_index(drop=True, inplace=True)
    return player_data.match_id

# 데이터프레임에 vs추가하기
def match_id_input(match_id): # player_data.match_id(series)을 input받아서 해당 match_id의 팀 추출
    data = matchs_data
    match_data = matchs_data
    for i in range(0,len(match_id)):
        if i == 0:
            match_data = data[(data['match_id'] == match_id[i])]
        else:
            match_data = pd.concat([match_data, data[(data['match_id'] == match_id[i])]],ignore_index = True )
    match_data.reset_index(drop=True, inplace=True)
    match_data['vs'] = None
    for i in range(0, len(match_data.team_name), 2):
        match_data['vs'][i] = f'{match_data.team_name[i]}"vs"{match_data.team_name[i+1]}'
    return match_data['vs'].dropna()

def match_id_return(match_id, options): # player_data.match_id(series)을 input받아서 해당 match_id의 팀 추출
    data = matchs_data
    match_data = matchs_data
    for i in range(0,len(match_id)):
        if i == 0:
            match_data = data[(data['match_id'] == match_id[i])]
        else:
            match_data = pd.concat([match_data, data[(data['match_id'] == match_id[i])]],ignore_index = True )
    match_data.reset_index(drop=True, inplace=True)
    match_data['vs'] = None
    for i in range(0, len(match_data.team_name), 2):
        match_data['vs'][i] = f'{match_data.team_name[i]}"vs"{match_data.team_name[i+1]}'
    
    for i in range(0,len(match_data)):
        if match_data['vs'][i] == options:
            # print(match_data['match_id'][i])
            return match_data['match_id'][i]

#골 시각화
def plot_events_goal(events, col_name, group_dict, team1_name, team2_name, event_type='Goal', rotate_team2_events=False):
    if event_type == 'Goal':
        match_title = f'{team1_name} - {team2_name} (goal)'

    if rotate_team2_events: #team2의 이벤트 데이터 x,y 반전
        events = events.copy()
        team2_idx = events['team_name'] == team2_name
        events.loc[team2_idx, ['start_x', 'end_x']] = 104 - events.loc[team2_idx, ['start_x', 'end_x']]
        events.loc[team2_idx, ['start_y', 'end_y']] = 68 - events.loc[team2_idx, ['start_y', 'end_y']]

    label_func = lambda x: f"{x['event_type']} by {x['player_name']}, {x['display_time']}, {x['tags']}"
    trace_list = []

    for group_name, color in group_dict.items(): #items() = 딕셔너리의 키 값 얻기
        group_events = events[events[col_name] == group_name]
        trace = go.Scatter(
            x=group_events['start_x'],
            y=group_events['start_y'],
            text=group_events.apply(label_func, axis=1),
            mode='markers',
            marker=dict(size=15, color=color),
            ids=group_events['tags']
        )
        trace['name'] = group_name
        trace_list.append(trace)

    fig = go.FigureWidget(data=trace_list, layout=get_pitch_layout(match_title))
    return fig

# 패스, 슛 시각화
def plot_events(events, col_name, group_dict, team1_name, team2_name, event_type='', rotate_team2_events=False):
    if event_type == 'Shot' or event_type == 'Pass':
        events = events[events['event_type'] == event_type]
        match_title = f'{team1_name} - {team2_name} ({event_type})'

    if rotate_team2_events: #team2의 이벤트 데이터 x,y 반전
        events = events.copy()
        team2_idx = events['team_name'] == team2_name
        events.loc[team2_idx, ['start_x', 'end_x']] = 104 - events.loc[team2_idx, ['start_x', 'end_x']]
        events.loc[team2_idx, ['start_y', 'end_y']] = 68 - events.loc[team2_idx, ['start_y', 'end_y']]

    fig = go.Figure()
    i = 0
    for group_name, color in group_dict.items(): #items() = 딕셔너리의 키 값 얻기
        group_events = events[events[col_name] == group_name]
        dx=group_events['end_x']
        dy=group_events['end_y']
        for i in range(0,len(dx.values)):
            fig.add_trace(go.Scatter(
                x=[group_events['start_x'].values[i],group_events['end_x'].values[i]],
                y=[group_events['start_y'].values[i],group_events['end_y'].values[i]],
                
                text=f"{group_events['event_type'].values[i]} by " + group_events['player_name'],
                marker= dict(size=15, color=color, symbol= "arrow", angleref="previous"),
                name = group_name,
                showlegend=False
            ))
    fig.update_layout(get_pitch_layout(match_title))
    return fig