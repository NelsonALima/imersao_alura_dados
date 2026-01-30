import pandas as pd
import streamlit as st
import plotly.express as px

# Configuracao da pagina (o que aparece nas abas)
st.set_page_config(page_title="Dashboard Salários", layout="wide")

# Carrega os dados
df = pd.read_csv("/home/nelsoncasa/Área de trabalho/projeto_imersao/dados_imersao.csv")

# Filtros
anos_disponiveis = sorted(df['ano'].unique())
senioridades_disponiveis = sorted(df['senioridade'].unique())
contratos_disponiveis = sorted(df['contrato'].unique())
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())

with st.sidebar:
    st.title("Painel de Controle")
    
    # Criando duas colunas na barra lateral
    col1, col2 = st.columns(2)    
    with col1:
        st.write("**Anos**")        
        selecionados_anos = [ano for ano in anos_disponiveis if st.checkbox(str(ano), value=True, key=f"y_{ano}")]
        
    with col2:
        st.write("**Senioridade**")        
        selecionados_sen = [s for s in senioridades_disponiveis if st.checkbox(s, value=True, key=f"s_{s}")]
    st.divider()

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Contrato**")        
        selecionados_cont = [c for c in contratos_disponiveis if st.checkbox(c, value=True, key=f"c_{c}")]
    with col4:
        st.write("**Empresa**")       
        selecionados_tmh = [t for t in tamanhos_disponiveis if st.checkbox(t, value=True, key=f"t_{t}")]    

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(selecionados_anos)) &
    (df['senioridade'].isin(selecionados_sen)) &
    (df['contrato'].isin(selecionados_cont)) &
    (df['tamanho_empresa'].isin(selecionados_tmh))
]

# --- Conteúdo Principal ---
st.title("Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")
st.divider()

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_mediano = df_filtrado['usd'].median()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, 0, ""

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário mediano", f"${salario_mediano:,.0f}")
col3.metric("Salário máximo", f"${salario_maximo:,.0f}")
col4.metric("Total de registros", f"{total_registros:,}")
col5.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)
with col_graf1:
    # Cria o container 
    tile1 = st.container(border=True)     
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(top_cargos, x='usd', y='cargo', orientation='h', title="Top 10 cargos")        
        
        tile1.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        tile1.warning("Nenhum dado disponível.")

with col_graf2:
    tile2 = st.container(border=True) 
    
    if not df_filtrado.empty:
        grafico_hist = px.histogram(df_filtrado, x='usd', nbins=30, title="Distribuição de Salário")        
       
        tile2.plotly_chart(grafico_hist, use_container_width=True)
    else:
        tile2.warning("Nenhum dado disponível.")

col_graf3, col_graf4 = st.columns(2)
with col_graf3:
    tile3 = st.container(border=True) 
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )

        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        tile3.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        tile3.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    tile4 = st.container(border=True)
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        
        grafico_paises.update_layout(title_x=0.1)
        tile4.plotly_chart(grafico_paises, use_container_width=True)
    else:
        tile4.warning("Nenhum dado para exibir no gráfico de países.")

col_graf5, col_graf6 = st.columns(2)
with col_graf5:
    tile5 = st.container(border=True) 
    df_agrupado_line = df_filtrado.groupby(["ano", "senioridade"])["usd"].mean().reset_index()
    
    if not df_filtrado.empty:
        grafico_line = px.line(df_agrupado_line, 
                               x='ano', 
                               y="usd", 
                               color="senioridade", 
                               title="Evolução Salarial por Senioridade", 
                               labels={'usd': 'Salário (USD)'},
                               markers=True)
        
        tile5.plotly_chart(grafico_line, use_container_width=True)
    else:
        tile5.warning("Nenhum dado disponível.")

with col_graf6:
    tile6 = st.container(border=True)     
    
    if not df_filtrado.empty:
        grafico_box = px.box(
            df_filtrado, 
            x='contrato', 
            y='usd',
            color='contrato',
            title='Distribuição Salarial por Tipo de Contrato',
            labels={'usd': 'Salário (USD)', 'contrato': 'Tipo de Contrato'}
        )
        grafico_box.update_layout(showlegend=False, title_x=0.1)
        
        tile6.plotly_chart(grafico_box, use_container_width=True)
    else:
        tile6.warning("Nenhum dado disponível.")

#--- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado, hide_index=True)       