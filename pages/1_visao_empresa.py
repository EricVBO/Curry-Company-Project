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

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide')

# ----------------------------------------
# Funções
# ---------------------------------------

def country_maps( df1 ):
    """ Esta funcao tem a responsabilidade de plotar a localização do pedido de acordo com a densidade do trânsito
        
    """
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude',	'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    if df_aux.empty:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
    else:
        map = folium.Map()
        for index, location_info in df_aux.iterrows():
            folium.Marker( [location_info['Delivery_location_latitude'],
                            location_info['Delivery_location_longitude']],
                            popup=location_info[['City','Road_traffic_density']]).add_to(map)
            folium_static(map, width=1024 , height=600 )
            return None

def order_share_by_week( df1 ):
    """ Esta funcao tem a responsabilidade agrupar os pedidos do entregador por semana e plotar um gráfico de linhas

            Ações:
            1. Criar coluna semana do ano
            2. Agrupar os pedidos por semana do ano e realizar a contagem
            3. Agrupar os pedidos por semana do ano do entregador e realizar a contagem
            4. Unir dataframes
            5. Plotar a quantidade de pedidos
        
    """
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    df_aux01 = df1.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux01, df_aux02, how='inner' )
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    
    return fig
    
def order_by_week( df1 ):
    """ Esta funcao tem a responsabilidade agrupar os pedidos por semana e plotar um gráfico de linhas

        Ações:
        1. Criar coluna semana do ano
        2. Agrupar os pedidos por semana do ano e realizar a contagem
        3. Plotar a quantidade de pedidos
        
    """
    # criar a coluna da semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    
    return fig
        
def traffic_order_city( df1 ):
    """ Esta funcao tem a responsabilidade de agrupar pedidos por tipo de cidade e densidade de trânsito e plotar um gráfico de dispersão

        Ações:
        1. Agrupar os pedidos por tipo de cidade e densidade do trânsito e realizar a contagem
        2. Plotar a quantidade de pedidos
        
    """
    df_aux = df1.loc[:, ['ID', 'City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size ='ID', color='City')    
    
    return fig
     
def traffic_order_share(df1):
    """ Esta função agrupa pedidos percentualmente por densidade de trânsito e plota um gráfico de pizza. """

    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

    # Verifica se há dados; se não houver, cria um DataFrame com um valor mínimo para manter o gráfico visível
    if df_aux.empty:
        df_aux = pd.DataFrame({
            'Road_traffic_density': ['Não há dados'],  # Rótulo fictício
            'entregas_perc': [1]  # 100% da pizza vai para "No Data"
        })
    else:
        df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    # Criando o gráfico de pizza
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig

def order_metric( df1 ):
    """ Esta funcao tem a responsabilidade de agrupar pedidos por data e plotar um gráfico de barras

        Ações:
        1. Agrupar os pedidos por data e realizar a contagem
        2. Plotar a quantidade de pedidos
        
    """
    # colunas
    cols = ['Order_Date', 'ID']
    
    # selecao de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    
    # desenhar o grafico de linhas
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    
    return fig
    
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
#---------------------
df = pd.read_csv('train.csv')

# --------------------
# Limpando os dados
# --------------------
df1 = clean_code ( df )

# ==============================================
# Barra Lateral
# ==============================================
st.header( 'Marketplace - Visão Empresa' )

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric( df1 )
        st.markdown( '# Pedidos por dia' )
        st.plotly_chart( fig, use_container_width=True )
        

    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = traffic_order_share( df1 )
            st.markdown('## Percentual de pedidos por trânsito')
            st.plotly_chart( fig, use_container_width=True )

        with col2:
            fig = traffic_order_city( df1 )
            st.markdown('## Pedidos por cidade e trânsito')
            st.plotly_chart( fig, use_container_width=True )
               
with tab2:
        with st.container():
            st.markdown( "# Média de pedidos por semana anual")
            fig = order_by_week( df1 )
            st.plotly_chart( fig, use_container_width=True )
            
        with st.container():
            st.markdown('# Média de pedidos do entregador por semana anual')
            fig = order_share_by_week( df1 )
            st.plotly_chart(fig, use_container_width=True)
        
with tab3:
    st.markdown( "# Localização geográfica média")
    country_maps ( df1 )
  
