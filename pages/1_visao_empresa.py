
#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='📊', layout='wide')

#-----------------------------------------------------------
#FUNÇÕES
#-----------------------------------------------------------
def clean_code(df1):
    """Esta função tem a responsabilidade de limpar o dataframe

       Tipos de limpeza:
       1. Remoção de Dados Nan
       2. Mudança do tipo da coluna de dados
       3. Remoção dos espaços das variáveis de texto
       4. Formatação da coluna de datas
       5. Limpeza da coluna de tempo (remoção do texto da variável numérica) 

       input: Dataframe
       output: Dataframe
    """

    # 1. Converter a coluna Age de texto para inteiro
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # 2. Convertendo a coluna Ratings de texto para decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 3. Convertendo a coluna Order_Date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y' )

    # 4. Convertendo a coluna multiple_deliveries de texto para números inteiros
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #  5. Removendo os espaços dentro de strings/texto
    # df1 = df1.reset_index(drop=True)
    # for i in range(42805):
    #   df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()

    #5. Removendo os espaços dentro de strings/texto
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    #6. Removendo linhas com NaN da coluna Road_traffic_density
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #7. Removendo linhas com NaN da coluna City
    linhas_selecionadas = (df1['City'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #8. Removendo linhas com NaN da coluna Festival
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #9. Limpando a coluna Time_taken(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1] )
    df1['Time_taken(min)']  = df1['Time_taken(min)'].astype( int )

    return df1


def order_metric(df1):
    st.markdown('# Orders by Day')

    #Calculando a quantidade de pedidos por dia
    df_aux = df1.loc[:,['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()

    #Plotando o gráfico de barras
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig

def traffic_order_share(df1):
    #Calculando a quantidade de pedidos por tipo de tráfego
    df_aux = df1.loc[:,['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

    #Criando a coluna "percent_order" para termos a porcentagem de pedido por cada tipo de densidade
    df_aux['percent_order'] = df_aux['ID'] / df_aux['ID'].sum()

    #Criando o gráfico de pizza
    fig = px.pie(df_aux,names='Road_traffic_density', values='ID')

    return fig

def traffic_order_city(df1):
    #Variável com as colunas que irei utilizar
    cols = ['ID', 'City', 'Road_traffic_density']

    #Calculando a quantidade de pedidos por cidade e por tipo de tráfego
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()

    #Criando o gráfico de bolhas
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density',size='ID')

    return fig

def order_by_week(df1): 
    #Criando a coluna 'Semana do ano' no dataframe
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    #Calculando a quantidade de pedidos por semana
    df1_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    #Plotando o gráfico de linhas
    fig = px.line(df1_aux, x='week_of_year', y='ID')

    return fig

def order_share_by_week(df1):
    #Criando a coluna 'Semana do ano' no dataframe
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    #Calculando a quantidade de pedidos por semana
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    #Calculando a quantidade de entregadores únicos por semana
    df_aux2 = df1.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()

    #Mesclando os dois dataframes
    df_aux = pd.merge(df_aux1, df_aux2, how = 'inner')

    #Criando a coluna de Pedidos por entregador em casa semana
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    #Criando o gráfico de linhas
    fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')
    
    return fig

def country_maps(df1):
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']

    df_aux = df1.loc[:,cols].groupby(['City', 'Road_traffic_density']).median().reset_index()

    map = folium.Map()

    for index,location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']]).add_to(map)
        
    folium_static(map, width=1024, height=600)

#Início da estruta lógica do código
    
#--------------------------------------
#Import dataset
#--------------------------------------
df = pd.read_csv('dataset/train.csv')

#--------------------------------------
#Limpeza dos dados
#--------------------------------------
df1 = clean_code(df)

# ====================================
# BARRA LATERAL
# ====================================
st.header('Marketplace - Visão Cliente')

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low')


st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ====================================
# LAYOUT STREAMLIT
# ====================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        fig = order_metric(df1)
        st.markdown("# Order by Day")
        st.plotly_chart(fig, use_container_width=True)

        
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            fig = traffic_order_share(df1)
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)
                           
        with col2:
            fig = traffic_order_city(df1)
            st.header('Traffic Order City')
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with st.container():
            st.markdown('# Orders by Week')
            fig = order_by_week(df1)
            st.plotly_chart(fig, use_container_width=True)        
                
        with st.container():
            st.markdown('# Order Share by Week')
            fig = order_share_by_week(df1)
            st.plotly_chart(fig, use_container_width=True)  

            
    with tab3:
        st.markdown('# Country Maps')
        country_maps(df1)
        