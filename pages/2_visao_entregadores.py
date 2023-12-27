#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

#-----------------------------------------------------------
#FUNÇÕES
#-----------------------------------------------------------
def top_delivers(df1, top_asc):
    df_aux = (df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']]
                 .groupby(['City', 'Delivery_person_ID'])
                 .mean()
                 .sort_values(['City','Time_taken(min)'], ascending=top_asc).reset_index())
    df.aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df.aux02 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df.aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df.aux01, df.aux02, df.aux03]).reset_index(drop=True)

    return df3

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

#Import dataset
df = pd.read_csv('dataset/train.csv')

#LIMPEZA DOS DADOS
df1 = clean_code(df)

# ====================================
# BARRA LATERAL
# ====================================

st.header('Marketplace - Visão Entregadores')

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022, 4, 13),
    min_value=datetime.datetime(2022, 2, 11),
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low')


st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

# ====================================
# LAYOUT STREAMLIT
# ====================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #A maior idade dos entregadores
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
            
        
        with col2:
            #A menor idade dos entregadores
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        
        with col3:
            #A melhor condição de veículos
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)
            

        with col4:
            #A pior condição de veículos
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()    
            col4.metric('Pior condição', pior_condicao)

    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação Média por Entregador')
            df_avg_ratings_by_deliver = round(df1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index(),2)
            st.dataframe(df_avg_ratings_by_deliver)

        with col2:
            st.markdown('##### Avaliação Média por Trânsito')
            df1_media_trafego = round(df1.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']]
                                         .groupby('Road_traffic_density')
                                         .agg({'Delivery_person_Ratings':['mean','std']}),2)
            df1_media_trafego.columns = ['delivery_mean', 'delivery_std']
            df1_media_trafego = df1_media_trafego.reset_index()
            st.dataframe(df1_media_trafego)



            st.markdown('##### Avaliação Média por Clima')
            df1_media_clima = round(df1.loc[:,['Delivery_person_Ratings', 'Weatherconditions']]
                                       .groupby('Weatherconditions')
                                       .agg({'Delivery_person_Ratings':['mean', 'std']}),2)

            df1_media_clima.columns = ['delivery_mean_clima', 'delivery_std_clima']
            df1_media_clima = df1_media_clima.reset_index()
            st.dataframe(df1_media_clima)
    
    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc = True)
            st.dataframe(df3)  

        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc = False)
            st.dataframe(df3)  
