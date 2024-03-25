# -*- coding:utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px 
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
from streamlit_folium import folium_static
import geopandas as gpd
from plotly.subplots import make_subplots
from utils.data_loader import load_data, load_shp_data, load_excel_data
from utils.filters import select_data, select_dong
from utils.visualizations import visualize_bar_chart, visualize_housing_type_distribution_by_selected_dong, visualize_elderly_population_ratio_by_selected_year, visualize_elderly_population_by_year, visualize_population_by_selected_year, visualize_fire_counts_by_selected_year, visualize_pie_chart, visualize_bar_chart_updated, visualize_horizontal_bar_chart
from utils.map_visualization import create_and_show_map, create_fire_equip_map, display_fire_extinguisher_map

# 페이지 설정

st.set_page_config(
   layout="wide",
   initial_sidebar_state="expanded", page_icon='🧯'
)
st.sidebar.page_link("서울시_화재사고_현황.py", label="서울시 화재사고 현황", icon="🔥")
st.sidebar.page_link("pages/1-화재사고_취약지역.py", label="화재사고 취약지역", icon="⚠️")
st.sidebar.page_link("pages/2-소방_인프라_분석.py", label="소방 인프라 분석", icon="🚒")
st.sidebar.page_link("pages/3-비상소화장치_위치_제안.py", label="비상소화장치 위치 제안", icon="🧯")
st.sidebar.page_link("pages/4-건의사항.py", label="건의사항", icon="💬")
data = load_excel_data("data/(송파소방서)비상소화장치.xlsx")
df = load_data("data/2020-2022_송파구_동별_화재건수.csv", encoding='CP949')
df_P = load_data("data/2022-2023_송파구_인구.csv", encoding='CP949')
df_O = load_data("data/2021-2023_송파구_고령자현황.csv", encoding='CP949')
df_H = load_data("data/2020_송파구_주택.csv", encoding='CP949')

df = df.replace('-', 0)
df['화재건수'] = df['화재건수'].astype(int)

df_H = df_H.replace('X', 0)
df_H['단독주택'] = df_H['단독주택'].astype(int)
df_H['연립주택'] = df_H['연립주택'].astype(int)
df_H['다세대주택'] = df_H['다세대주택'].astype(int)
df_H['비거주용건물내주택'] = df_H['비거주용건물내주택'].astype(int)

def main():
    # 스트림릿 대시보드
    st.header('비상소화장치 위치 제안', divider="gray")
    st.caption('현재 서비스는 송파구 내에서만 사용가능합니다.')
    col1, col2 = st.columns([7,3])
    with col1:
        with st.container(border=True, height=650):  
            col5, col6 = st.columns([7,3])
            with col5: 
                st.subheader('송파구 비상소화장치 제안 위치')
            with col6: 
                with st.popover("💡 **위치 선정 방법**"):
                    st.markdown("""
                        <div style="font-family: sans-serif;">
                            <h4>선정 단계</h4>
                            <ol>
                                <li><strong>화재 주택 밀집 지역 파악:</strong> 우선적으로 화재가 자주 발생하는 주택이 밀집된 지역을 선별했습니다.</li>
                                <li><strong>지역 상세 분석:</strong> 선택된 지역 및 인접 지역을 상세히 조사하여 화재 위험 요인을 식별했습니다.</li>
                                <li><strong>설치 필요 지역 결정:</strong> 
                                    <ul>
                                        <li>비상소화장치가 없는 화재 건물 밀집 지역을 설치 대상으로 선정했습니다.</li>
                                        <li>화재 위험이 없는 지역이라도, 길이 좁고 노후한 건물이 많아 위험성이 높은 곳은 설치를 고려했습니다.</li>
                                    </ul>
                                </li>
                            </ol>
                        </div>
                        """, unsafe_allow_html=True)


            # 송파구의 중심 좌표 설정
            center = [37.514543, 127.106597]
            # 비상 소화장치 위치 데이터 (위도, 경도, 설명)
            locations = [
                (37.5085071, 127.0825862, '잠실동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202024-03-25%20131913.png?raw=true'),
                (37.50511389, 127.0817572, '잠실동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202024-03-25%20132301.png?raw=true'),
                (37.50231025, 127.0901942, '삼전동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202024-03-25%20132425.png?raw=true'),
                (37.50094046, 127.0936817, '삼전동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202024-03-25%20132509.png?raw=true'),
                (37.504103, 127.090679, '삼전동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202024-03-25%20132839.png?raw=true'),
                (37.49991962, 127.0974103, '석촌동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202024-03-25%20132919.png?raw=true'),
                (37.50097974, 127.1000492, '석촌동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202024-03-25%20132956.png?raw=true'),
                (37.50884075, 127.1087034, '송파동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EB%B9%84%EC%83%81%EC%86%8C%ED%99%94%EC%9E%A5%EC%B9%98%EC%A0%9C%EC%95%88%EC%9C%84%EC%B9%98%EC%9D%98%20%EC%82%AC%EB%B3%B8_Img9.png?raw=true'),
                (37.511740, 127.110053, '방이동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EB%B9%84%EC%83%81%EC%86%8C%ED%99%94%EC%9E%A5%EC%B9%98%EC%A0%9C%EC%95%88%EC%9C%84%EC%B9%98%EC%9D%98%20%EC%82%AC%EB%B3%B8_Img13(1).png?raw=true'),  
                (37.51299316, 127.1161285, '방이동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EB%B9%84%EC%83%81%EC%86%8C%ED%99%94%EC%9E%A5%EC%B9%98%EC%A0%9C%EC%95%88%EC%9C%84%EC%B9%98%EC%9D%98%20%EC%82%AC%EB%B3%B8_Img14.png?raw=true'),
                (37.499000, 127.120611, '가락본동, 가락1동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EB%B9%84%EC%83%81%EC%86%8C%ED%99%94%EC%9E%A5%EC%B9%98%EC%A0%9C%EC%95%88%EC%9C%84%EC%B9%98%EC%9D%98%20%EC%82%AC%EB%B3%B8_Img5.png?raw=true'),
                (37.496917, 127.120417, '가락본동, 가락1동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EB%B9%84%EC%83%81%EC%86%8C%ED%99%94%EC%9E%A5%EC%B9%98%EC%A0%9C%EC%95%88%EC%9C%84%EC%B9%98%EC%9D%98%20%EC%82%AC%EB%B3%B8_Img4.png?raw=true'),
                (37.500694, 127.112639, '송파2동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EB%B9%84%EC%83%81%EC%86%8C%ED%99%94%EC%9E%A5%EC%B9%98%EC%A0%9C%EC%95%88%EC%9C%84%EC%B9%98%EC%9D%98%20%EC%82%AC%EB%B3%B8_Img6(1).png?raw=true'),
                (37.492321, 127.154682, '마천1동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202024-03-25%20133039.png?raw=true'),
                (37.499138, 127.149098, '마천2동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202024-03-25%20133212.png?raw=true'),
                (37.493358, 127.142836, '거여1동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EB%B9%84%EC%83%81%EC%86%8C%ED%99%94%EC%9E%A5%EC%B9%98%EC%A0%9C%EC%95%88%EC%9C%84%EC%B9%98%EC%9D%98%20%EC%82%AC%EB%B3%B8_Img25.png?raw=true'),
                (37.497698, 127.143332, '거여1동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EB%B9%84%EC%83%81%EC%86%8C%ED%99%94%EC%9E%A5%EC%B9%98%EC%A0%9C%EC%95%88%EC%9C%84%EC%B9%98%EC%9D%98%20%EC%82%AC%EB%B3%B8_Img29.png?raw=true'),
                (37.503962, 127.140793, '오금동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EB%B9%84%EC%83%81%EC%86%8C%ED%99%94%EC%9E%A5%EC%B9%98%EC%A0%9C%EC%95%88%EC%9C%84%EC%B9%98%EC%9D%98%20%EC%82%AC%EB%B3%B8_Img23.png?raw=true'),
                (37.502313, 127.134786, '오금동', 'https://github.com/suhyeon0325/multicamp_semi/blob/main/data/%EC%82%AC%EC%A7%84/%EB%B9%84%EC%83%81%EC%86%8C%ED%99%94%EC%9E%A5%EC%B9%98%EC%A0%9C%EC%95%88%EC%9C%84%EC%B9%98%EC%9D%98%20%EC%82%AC%EB%B3%B8_Img18.png?raw=true')
            ]

            # 지도 표시 함수 호출
            display_fire_extinguisher_map(center, locations)

    with col2:
        with st.container(border=True, height=650):  

            st.markdown("""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <button style='
                        border: none;
                        pointer-events: none;
                        color: white;
                        padding: 10px 12px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        font-weight: bold;
                        margin: 4px 2px;
                        cursor: pointer;
                        background-color: #F24C3D;
                        border-radius: 8px;'>
                    각 위치별 상세 정보
                    </button>
                </div>
                """, unsafe_allow_html=True)

            col3, col4 = st.columns([1,1])
            with col3:
                with st.popover("**1번 위치**", use_container_width=True):
                    st.markdown("가나다라")
                with st.popover("**3번 위치**", use_container_width=True):
                    st.markdown("가나다라")
                with st.popover("**5번 위치**", use_container_width=True):
                    st.markdown("가나다라") 
                with st.popover("**7번 위치**", use_container_width=True):
                    st.markdown("가나다라") 
                with st.popover("**9번 위치**", use_container_width=True):
                    st.markdown("주변에 식당•술집 골목이 있고 주택가로 들어오면 길이 확 좁아진다. 여기도 소방차가 안 쪽으로 진입하는 데 시간이 꽤 걸릴 것 같다. 지나다니는 사람들이 많아 차가 지나가면 움직이기 힘든 골목이다.")   
                with st.popover("**11번 위치**", use_container_width=True):
                    st.markdown("넓은 도로와 좁은 도로가 반복되는 곳. 신축건물과 노후건물이 같이 있는 구역임. 마커가 찍힌 곳은 좁긴 한데 바로 옆에 길들이 관리가 잘 되어있는 편이다. 그래도 임시로 주차가 되어있을 경우 길이 좁아지는 곳이 많음")  
                with st.popover("**13번 위치**", use_container_width=True):
                    st.markdown("로드맵으로 봤을 땐 바로 옆에 큰 도로가 있어서 비상소화장치가 크게 필요없지 않을까 했는데, 식당이 많고 좁은 골목이 많았으며 차량 통행이 많은 구역이라 일반 승용차들도 이 위치로 들어오는데 많은 시간이 걸리는 게 보였음. 아마 소방차가 와도 안쪽으로 진입하는 시간이 지체될 것으로 보임. 그래서인지 소화기가 설치되어 있는 주택이 꽤 보였다.")  
                with st.popover("**15번 위치**", use_container_width=True):
                    st.markdown("가나다라")  
                with st.popover("**17번 위치**", use_container_width=True):
                    st.markdown("낡은 주택이 많고 좁은 길이 많으며 경사가 많다. 길에 정차된 차량때문에 통행이 더 힘들 것 같다. 여기도 마찬가지로 소방차 진입시간을 고려하여 비상소화장치를 설치하면 좋겠다.") 
                with st.popover("**19번 위치**", use_container_width=True):
                    st.markdown("오래된 주택이 많고 길에 주정차된 차량과 쓰레기 등 장애물들이 많다. 근처 길도 전부 좁은 길이라 비상소화장치의 필요성이 있을 듯")                      
            with col4:
                with st.popover("**2번 위치**", use_container_width=True):
                    st.markdown("가나다라")
                with st.popover("**4번 위치**", use_container_width=True):
                    st.markdown("가나다라")                                                
                with st.popover("**6번 위치**", use_container_width=True):
                    st.markdown("가나다라")
                with st.popover("**8번 위치**", use_container_width=True):
                    st.markdown("네이버 지도 로드맵 사진(23년 3월)으로 볼 때보다 새로 지어진 건물이 많이 보였다. 놀이터 및 보행로, 좁은 길이 많고 지나다니는 사람이 많아서 일반 차량이 진입하는 데도 꽤 시간이 걸릴 것으로 보임.") 
                with st.popover("**10번 위치**", use_container_width=True):
                    st.markdown("도로 자체는 나름 깔끔하고 잘 관리되어 있는데 차량이 접근하는 시간이 꽤 걸릴 것 같다. 길에 주차구역이 종종 있는데 차량들이 여럿 지나갈 경우 통과하는 데 오래 걸림. 근데 신축빌라가 많이 지어지는 듯? 엄~청 오래된 건물과 신축건물이 섞여있는 지역이다. ") 
                with st.popover("**12번 위치**", use_container_width=True):
                    st.markdown("주변에 식당, 술집이 많은 편. 주택가에는 주차된 차가 있을 경우 승용차가 겨우 지나가는 폭임. 큰 도로가 옆에 있어서 진입이 어려울 것 같진 않지만 노후주택이 많아 화재가 나면 피해가 클 것으로 보임")   
                with st.popover("**14번 위치**", use_container_width=True):
                    st.markdown("가나다라")  
                with st.popover("**16번 위치**", use_container_width=True):
                    st.markdown("낡은 주택과 좁은 골목으로 이루어진 지역이다. 큰 도로가 바로 옆에 있긴 하지만 차들이 얽히면 사람이 지나가기 힘들어진다. 소방차 진입 시간을 고려하여 비상소화장치를 설치하면 좋을 듯…")  
                with st.popover("**18번 위치**", use_container_width=True):
                    st.markdown("주변 길이 모두 좁고 주차된 차들이 많다. 송파소방서가 가깝긴 하지만... 원활한 차량 통행이 힘들다는 점을 고려하여 비상소화장치를 배치하면 좋겠다.")  


    with st.container(border=True, height=900):
        st.subheader('송파구 소방 인프라 분석')
        tab1, tab2, tab3, tab4 = st.tabs(["송파구 소방 인프라", "화재 건수", "노년 인구", " 주택 현황"])
         
        with tab1:        
            st.subheader('현재 송파구 비상소화장치 위치')
            create_fire_equip_map(data)  # fire_equip_df는 당신의 데이터프레임 변수명입니다.



        # 송파구 화재 건수 분석
        with tab2:
            st.subheader('송파구 화재 건수 분석')
            select = st.radio("선택", ["동별 화재발생 건수", "연도별 화재발생 건수"],horizontal=True, label_visibility="collapsed")
            if select == '연도별 화재발생 건수':
                # 2020~2023 총 화재 건수 시각화
                new_data = pd.DataFrame({'시점': [2023],'화재건수': [382]})
                df_grouped = df.groupby(['시점'])['화재건수'].sum().reset_index()
                시점 = df_grouped['시점'].tolist()
                화재건수 = df_grouped['화재건수'].tolist()
                df_grouped_updated = pd.concat([df_grouped, new_data]).reset_index(drop=True)
                시점 = df_grouped_updated['시점'].tolist()
                화재건수 = df_grouped_updated['화재건수'].tolist()
                colors = ['#fc8d59', '#fdcc8a', '#e34a33', '#b30000']
                fig = go.Figure()
                fig.add_trace(go.Bar(x=시점, y=화재건수, width=0.4, marker_color=colors, text=df_grouped_updated['화재건수']))
                fig.update_layout(title_text='송파구 2020~2023 총 화재건수', xaxis_type='category',
                                yaxis_title='화재건수', xaxis_title='시점')
                st.plotly_chart(fig)

            else:
                # 연도 선택 위젯
                selected_year = st.selectbox('연도를 선택하세요.', options=sorted(df['시점'].unique(), reverse=True))

                # 선택된 연도에 대한 화재건수 시각화 함수 호출
                fig = visualize_fire_counts_by_selected_year(df, selected_year)
                st.plotly_chart(fig, use_container_width=True)
            
        # 송파구 노년 인구 분석
        with tab3:
            st.subheader('송파구 노년 인구 분석')
            select = st.radio("선택", ["거주인구", "노년인구", "동별 노년인구", "노년인구 비율"],horizontal=True, label_visibility="collapsed")

            if select == '거주인구':
                # 연도 선택 위젯
                selected_year = st.selectbox('연도를 선택하세요.', options=sorted(df_O['시점'].unique(), reverse=True))

                # 선택된 연도에 대한 거주인구 시각화 함수 호출
                fig = visualize_population_by_selected_year(df_O, selected_year)
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)

            elif select == '노년인구':
                시점 = df_P['시점'].tolist()
                노년인구 = df_P['노년 전체 인구'].tolist()
                시점.reverse()

                colors = ['tomato', 'crimson', 'darkred', 'lightsalmon']
                fig = go.Figure()
                fig.add_trace(go.Bar(x=시점, y=노년인구, marker_color=colors, width=0.4, text=df_P['노년 전체 인구']))
                fig.update_layout(title_text='송파구 2022~2023년도 노년인구 수', yaxis_title='노년인구', xaxis_title='시점')
                st.plotly_chart(fig)

            elif select == '동별 노년인구':
                    
                # 선택된 연도에 대한 거주 인구 시각화
                visualize_elderly_population_by_year(df_O)
                
            else:
                # 연도 선택 위젯
                selected_year = st.selectbox('연도를 선택하세요.', options=sorted(df_O['시점'].unique(), reverse=True))

                # 선택된 연도에 대한 노년인구 비율 시각화 함수 호출
                fig = visualize_elderly_population_ratio_by_selected_year(df_O, selected_year)
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)

        # 송파구 주택현황 분석
        with tab4:
            st.subheader('송파구 주택현황 분석')
            select_1 = st.radio("선택", ["동별 주택유형 분포", "동별 주택수"], horizontal=True, label_visibility="collapsed")
            if select_1 == "동별 주택유형 분포":
                # 동 선택 위젯
                selected_dong = st.selectbox('동을 선택하세요.', options=sorted(df_H['동'].unique()))

                # 선택된 동에 대한 주택 유형별 분포 시각화 함수 호출
                fig = visualize_housing_type_distribution_by_selected_dong(df_H, selected_dong)
                st.plotly_chart(fig, use_container_width=True)

            # 주택 현황 - 동별 주택 수
            else: 
                df_total = df_H[['동', '소계']]
                df_total_sorted = df_total.sort_values('소계', ascending=True)

                # 가로 막대 그래프 그리기
                fig_total_sorted = px.bar(df_total_sorted, y='동', x='소계', text='소계',
                                        orientation='h',  # 가로 막대 그래프 설정
                                        color='소계', color_continuous_scale=px.colors.sequential.OrRd,
                                        title="송파구 동별 주택 수(2020년)")
                fig_total_sorted.update_layout(height=600)
                st.plotly_chart(fig_total_sorted, use_container_width=True)

if __name__ =="__main__":
    main()
