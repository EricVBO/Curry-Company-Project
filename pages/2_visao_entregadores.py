# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import pandas as pd
import streamlit as st
import folium
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide')


# ----------------------------------------
# Funções
# ---------------------------------------
def top_delivers( df1, top_asc ):
    """ Esta funcao tem a responsabilidade de exibir um dataframe com a média dos entregadores mais rápidos e mais lentos 

        Passos:
        1. Seleção das colunas
        2. Agrupamento
        3. Aplicação da função
        4. Filtragem
        5. Junção dos dados
        6. Exibição do DataFrame
      
    """
    df2 = ( df1.loc[:, ['Delivery_person_ID','Time_taken(min)' ,'City']]
             .groupby(['City', 'Delivery_person_ID'])
             .mean()
             .sort_values(['City','Time_taken(min)'], ascending = top_asc).reset_index() )
    
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index( drop=True )
    
    return df3

def clean_code( df1 ):
    """" Esta funcao tem a responsabilidade de limpar o dataframe 
        
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )

        Input: Dataframe
        Output: Dataframe
    """
    #1. convertendo a coluna Age de texto para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #2. convertendo a coluna Ratings de texto para numero decimal ( float )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    
    #3. convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y' )
    
    #4. convertendo multiple_deliveries de texto para numero inteiro ( int )
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    #6. removendo os espacos dentro de strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    #7. Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min)' )[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

# -------------------- Inicio da Estrutura Lógica do Código -----------------------------------
# --------------------
#Import dataset
df = pd.read_csv('train.csv')

# cleaning dataset
df1 = clean_code( df )


# ==============================================
# Barra Lateral
# ==============================================
st.header( 'Marketplace - Visão Entregadores' )

image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
   'Até qual data?',
    value=datetime( 2022, 4, 13 ),
    min_value=datetime( 2022, 2, 11 ),
    max_value=datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY' )

st.sidebar.markdown("""---""")


traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default= ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# ==============================================
# Layout no Streamlit
# ==============================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])
with tab1:
    with st.container():
        st.title('Métricas Gerais')
        
        
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
           
            # A maior idade dos entregadores
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade do entregador', maior_idade)
        
        with col2:
           
            # A menor idade dos entregadores
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade do entregador', menor_idade)
         
        with col3:
            
            # A melhor condição de veículo
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição do veículo', melhor_condicao)
            
        with col4:
            
            # A pior condição de veículo
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição do veículo', pior_condicao)
    
    
    with st.container():
        st.markdown("""---""")        
        st.title('Avaliações')
    
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df_avg_ratings_per_deliver = df1.loc[:, ['Delivery_person_ID','Delivery_person_Ratings']].groupby(['Delivery_person_ID']).mean().reset_index()
            st.dataframe(df_avg_ratings_per_deliver)
    
        with col2:
            st.markdown('##### Avaliação média e STD por trânsito')
            df_traffic_mean_std = df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']].groupby(['Road_traffic_density']).agg({'Delivery_person_Ratings' : ['mean', 'std']})
            df_traffic_mean_std.columns = ['delivery_mean', 'delivery_std']
            st.dataframe(df_traffic_mean_std.reset_index())
            
            st.markdown('##### Avaliação média e STD por clima')
            df_wheather_mean_std = df1.loc[:, ['Delivery_person_Ratings','Weatherconditions']].groupby(['Weatherconditions']).agg({'Delivery_person_Ratings' : ['mean', 'std']})
            df_wheather_mean_std.columns = ['delivery_mean', 'delivery_std']
            st.dataframe(df_wheather_mean_std.reset_index())
    
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
    
        col1, col2 = st.columns( 2 )
    
        with col1:
            st.markdown('##### Top Média Entregadores mais rápidos')
            df3 = top_delivers( df1, top_asc = True )
            st.dataframe(df3)
        
        with col2:
            st.markdown('##### Top Média Entregadores mais lentos')
            df3 = top_delivers( df1, top_asc = False )
            st.dataframe(df3)
    
    
    
    
            
    
