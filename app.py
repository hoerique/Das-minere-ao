import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Mineração",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Dashboard de Análise de Dados de Mineração")
st.markdown("---")

# Função para carregar e tratar os dados
@st.cache_data
def carregar_dados():
    """Carrega e trata os dados do CSV"""
    try:
        # Carregar dados do link bruto do GitHub
        url = 'https://github.com/hoerique/Das-minere-ao/blob/main/Dados.csv'
        df = pd.read_csv(url)
        if df.empty:
            st.error("O arquivo CSV foi carregado, mas está vazio. Verifique o conteúdo do arquivo no GitHub.")
            return None
        
        # Converter colunas de data
        df['Data de Produção'] = pd.to_datetime(df['Data de Produção'])
        
        # Extrair informações da data
        df['Ano'] = df['Data de Produção'].dt.year
        df['Mês'] = df['Data de Produção'].dt.month
        df['Trimestre'] = df['Data de Produção'].dt.quarter
        
        # Converter colunas numéricas
        colunas_numericas = [
            'Quantidade (Toneladas)', 'Preço Unitário (R$)', 
            'Volume de Vendas (R$)', 'Custo de Produção (R$)', 
            'Lucro (R$)', 'Quantidade Exportada (Toneladas)', 
            'Custo Logístico (R$)'
        ]
        
        for coluna in colunas_numericas:
            df[coluna] = pd.to_numeric(df[coluna], errors='coerce')
        
        # Calcular métricas adicionais
        df['Margem de Lucro (%)'] = (df['Lucro (R$)'] / df['Volume de Vendas (R$)']) * 100
        df['Custo Total'] = df['Custo de Produção (R$)'] + df['Custo Logístico (R$)']
        df['ROI (%)'] = (df['Lucro (R$)'] / df['Custo Total']) * 100
        
        # Limpar dados inconsistentes
        df = df.dropna()
        
        # Remover outliers extremos (valores muito discrepantes)
        for coluna in colunas_numericas:
            Q1 = df[coluna].quantile(0.25)
            Q3 = df[coluna].quantile(0.75)
            IQR = Q3 - Q1
            limite_inferior = Q1 - 1.5 * IQR
            limite_superior = Q3 + 1.5 * IQR
            df = df[(df[coluna] >= limite_inferior) & (df[coluna] <= limite_superior)]
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar dados do GitHub: {e}\nVerifique se o arquivo está disponível e acessível.")
        return None

# Carregar dados
df = carregar_dados()

if df is not None:
    # Sidebar para filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por produto
    produtos = ['Todos'] + list(df['Produto'].unique())
    produto_selecionado = st.sidebar.selectbox("Produto:", produtos)
    
    # Filtro por região
    regioes = ['Todas'] + list(df['Região'].unique())
    regiao_selecionada = st.sidebar.selectbox("Região:", regioes)
    
    # Filtro por ano
    anos = ['Todos'] + sorted(list(df['Ano'].unique()))
    ano_selecionado = st.sidebar.selectbox("Ano:", anos)
    
    # Filtro por classificação de sustentabilidade
    classificacoes = ['Todas'] + sorted(list(df['Classificação de Sustentabilidade'].unique()))
    classificacao_selecionada = st.sidebar.selectbox("Classificação de Sustentabilidade:", classificacoes)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if produto_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Produto'] == produto_selecionado]
    
    if regiao_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Região'] == regiao_selecionada]
    
    if ano_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Ano'] == ano_selecionado]
    
    if classificacao_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Classificação de Sustentabilidade'] == classificacao_selecionada]
    
    # KPIs Principais - 4 KPIs recomendados
    st.subheader("📊 KPIs Principais")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # KPI 1: Lucro Total (R$)
        lucro_total = df_filtrado['Lucro (R$)'].sum()
        lucro_total_geral = df['Lucro (R$)'].sum()
        st.metric(
            label="💵 Lucro Total (R$)",
            value=f"R$ {lucro_total:,.0f}",
            delta=f"R$ {lucro_total - lucro_total_geral:+,.0f}" if len(df_filtrado) != len(df) else None,
            help="📈 Mede a rentabilidade da produção. Fórmula: Soma da coluna Lucro (R$)"
        )
    
    with col2:
        # KPI 2: Volume Total de Vendas (R$)
        vendas_totais = df_filtrado['Volume de Vendas (R$)'].sum()
        vendas_totais_geral = df['Volume de Vendas (R$)'].sum()
        st.metric(
            label="💰 Volume Total de Vendas (R$)",
            value=f"R$ {vendas_totais:,.0f}",
            delta=f"R$ {vendas_totais - vendas_totais_geral:+,.0f}" if len(df_filtrado) != len(df) else None,
            help="💰 Mostra o desempenho comercial. Fórmula: Soma da coluna Volume de Vendas (R$)"
        )
    
    with col3:
        # KPI 3: Margem de Lucro (%)
        margem_media = df_filtrado['Margem de Lucro (%)'].mean()
        margem_media_geral = df['Margem de Lucro (%)'].mean()
        st.metric(
            label="📊 Margem de Lucro (%)",
            value=f"{margem_media:.1f}%",
            delta=f"{margem_media - margem_media_geral:+.1f}%" if len(df_filtrado) != len(df) else None,
            help="📊 Indicador da eficiência da operação. Fórmula: Lucro / Volume de Vendas * 100"
        )
    
    with col4:
        # KPI 4: Custo Médio Logístico por Tonelada
        custo_logistico_total = df_filtrado['Custo Logístico (R$)'].sum()
        quantidade_total = df_filtrado['Quantidade (Toneladas)'].sum()
        custo_medio_logistico = custo_logistico_total / quantidade_total if quantidade_total > 0 else 0
        
        custo_logistico_geral = df['Custo Logístico (R$)'].sum()
        quantidade_geral = df['Quantidade (Toneladas)'].sum()
        custo_medio_geral = custo_logistico_geral / quantidade_geral if quantidade_geral > 0 else 0
        
        st.metric(
            label="🚚 Custo Médio Logístico por Tonelada",
            value=f"R$ {custo_medio_logistico:.2f}",
            delta=f"R$ {custo_medio_logistico - custo_medio_geral:+.2f}" if len(df_filtrado) != len(df) else None,
            help="🚚 Avalia a eficiência da distribuição. Fórmula: Custo Logístico (R$) / Quantidade (Toneladas)"
        )
    
    st.markdown("---")
    
    # 4 Gráficos Recomendados
    st.subheader("📊 Gráficos de Análise")
    
    # Gráfico 1: Gráfico de Barras – Lucro por Produto
    st.subheader("📌 Gráfico de Barras – Lucro por Produto")
    lucro_por_produto = df_filtrado.groupby('Produto')['Lucro (R$)'].sum().reset_index()
    if not lucro_por_produto.empty:
        fig_lucro_produto = px.bar(
            lucro_por_produto, 
            x='Produto', 
            y='Lucro (R$)',
            color='Produto',
            title="Comparar a lucratividade dos diferentes produtos",
            labels={'Lucro (R$)': 'Lucro Total (R$)', 'Produto': 'Produto'}
        )
        fig_lucro_produto.update_layout(showlegend=False)
        st.plotly_chart(fig_lucro_produto, use_container_width=True)
    else:
        st.info("Sem dados para o gráfico de Lucro por Produto.")
    
    # Gráfico 2: Gráfico de Linhas – Evolução de Vendas ao longo do tempo
    st.subheader("📆 Gráfico de Linhas – Evolução de Vendas ao longo do tempo")
    vendas_tempo = df_filtrado.groupby('Data de Produção')['Volume de Vendas (R$)'].sum().reset_index()
    if not vendas_tempo.empty:
        fig_vendas_tempo = px.line(
            vendas_tempo, 
            x='Data de Produção', 
            y='Volume de Vendas (R$)',
            title="Acompanhar a performance mensal ou anual com base em Data de Produção",
            labels={'Volume de Vendas (R$)': 'Volume de Vendas (R$)', 'Data de Produção': 'Data de Produção'}
        )
        st.plotly_chart(fig_vendas_tempo, use_container_width=True)
    else:
        st.info("Sem dados para o gráfico de Evolução de Vendas.")
    
    # Gráfico 3: Gráfico de Pizza – Distribuição de Volume de Vendas por Região
    st.subheader("🌍 Gráfico de Pizza – Distribuição de Volume de Vendas por Região")
    vendas_por_regiao = df_filtrado.groupby('Região')['Volume de Vendas (R$)'].sum().reset_index()
    if not vendas_por_regiao.empty:
        fig_vendas_regiao = px.pie(
            vendas_por_regiao, 
            values='Volume de Vendas (R$)', 
            names='Região',
            title="Visualizar onde estão concentradas as vendas"
        )
        st.plotly_chart(fig_vendas_regiao, use_container_width=True)
    else:
        st.info("Sem dados para o gráfico de Vendas por Região.")
    
    # Gráfico 4: Gráfico de Colunas Empilhadas – Custo de Produção vs Lucro por Fábrica
    st.subheader("🏭 Gráfico de Colunas Empilhadas – Custo de Produção vs Lucro por Fábrica")
    custo_lucro_fabrica = df_filtrado.groupby('Fábrica').agg({
        'Custo de Produção (R$)': 'sum',
        'Lucro (R$)': 'sum'
    }).reset_index()
    if not custo_lucro_fabrica.empty:
        # Preparar dados para gráfico empilhado
        custo_lucro_fabrica_melted = custo_lucro_fabrica.melt(
            id_vars=['Fábrica'], 
            value_vars=['Custo de Produção (R$)', 'Lucro (R$)'],
            var_name='Tipo', 
            value_name='Valor (R$)'
        )
        fig_custo_lucro = px.bar(
            custo_lucro_fabrica_melted,
            x='Fábrica',
            y='Valor (R$)',
            color='Tipo',
            title="Entender como os custos e lucros variam entre as unidades",
            barmode='group'  # Usar 'group' para colunas lado a lado em vez de empilhadas
        )
        st.plotly_chart(fig_custo_lucro, use_container_width=True)
    else:
        st.info("Sem dados para o gráfico de Custo vs Lucro por Fábrica.")
    
    # Análise de correlação
    st.subheader("🔗 Análise de Correlação")
    colunas_correlacao = ['Quantidade (Toneladas)', 'Preço Unitário (R$)', 'Volume de Vendas (R$)', 
                         'Custo de Produção (R$)', 'Lucro (R$)', 'Custo Logístico (R$)']
    if not df_filtrado[colunas_correlacao].empty:
        correlacao = df_filtrado[colunas_correlacao].corr()
        fig_correlacao = px.imshow(
            correlacao,
            text_auto=True,
            aspect="auto",
            title="Matriz de Correlação entre Variáveis Numéricas"
        )
        st.plotly_chart(fig_correlacao, use_container_width=True)
    else:
        st.info("Sem dados suficientes para análise de correlação.")
    
    # Tabela de estatísticas descritivas
    st.subheader("📋 Estatísticas Descritivas")
    colunas_estatisticas = ['Quantidade (Toneladas)', 'Preço Unitário (R$)', 'Volume de Vendas (R$)', 
                           'Custo de Produção (R$)', 'Lucro (R$)', 'Margem de Lucro (%)']
    estatisticas = df_filtrado[colunas_estatisticas].describe()
    if not estatisticas.empty:
        st.dataframe(estatisticas, use_container_width=True)
    else:
        st.info("Sem dados para estatísticas descritivas.")
    
    # Análise por classificação de sustentabilidade
    st.subheader("🌱 Análise por Sustentabilidade")
    col1, col2 = st.columns(2)
    
    with col1:
        sust_metrics = df_filtrado.groupby('Classificação de Sustentabilidade').agg({
            'Volume de Vendas (R$)': 'sum',
            'Lucro (R$)': 'sum',
            'Margem de Lucro (%)': 'mean'
        }).reset_index()
        if not sust_metrics.empty:
            fig_sust_vendas = px.bar(
                sust_metrics, 
                x='Classificação de Sustentabilidade', 
                y='Volume de Vendas (R$)',
                title="Volume de Vendas por Classificação de Sustentabilidade"
            )
            st.plotly_chart(fig_sust_vendas, use_container_width=True)
        else:
            st.info("Sem dados para o gráfico de Vendas por Sustentabilidade.")
    
    with col2:
        if not sust_metrics.empty:
            fig_sust_margem = px.bar(
                sust_metrics, 
                x='Classificação de Sustentabilidade', 
                y='Margem de Lucro (%)',
                title="Margem de Lucro por Classificação de Sustentabilidade"
            )
            st.plotly_chart(fig_sust_margem, use_container_width=True)
        else:
            st.info("Sem dados para o gráfico de Margem de Lucro por Sustentabilidade.")
    
    # Dados tratados para download
    st.subheader("💾 Download dos Dados Tratados")
    
    # Criar versão tratada dos dados
    df_download = df_filtrado.copy()
    
    # Formatar colunas monetárias
    colunas_monetarias = ['Volume de Vendas (R$)', 'Custo de Produção (R$)', 'Lucro (R$)', 'Custo Logístico (R$)']
    for coluna in colunas_monetarias:
        df_download[coluna] = df_download[coluna].apply(lambda x: f"R$ {x:,.2f}")
    
    # Formatar percentuais
    df_download['Margem de Lucro (%)'] = df_download['Margem de Lucro (%)'].apply(lambda x: f"{x:.2f}%")
    df_download['ROI (%)'] = df_download['ROI (%)'].apply(lambda x: f"{x:.2f}%")
    
    # Botão de download
    csv = df_download.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Download CSV Tratado",
        data=csv,
        file_name=f"dados_mineracao_tratados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # Informações sobre o tratamento
    st.subheader("ℹ️ Informações sobre o Tratamento dos Dados")
    
    st.markdown("""
    **Etapas de tratamento realizadas:**
    
    1. **Conversão de tipos de dados:**
       - Datas convertidas para formato datetime
       - Colunas numéricas convertidas para float/int
       
    2. **Criação de novas variáveis:**
       - Ano, Mês e Trimestre extraídos da data
       - Margem de Lucro (%) calculada
       - Custo Total (Produção + Logística)
       - ROI (%) calculado
       
    3. **Limpeza de dados:**
       - Remoção de valores nulos
       - Remoção de outliers extremos usando método IQR
       
    4. **KPIs Implementados:**
       - 💵 **Lucro Total (R$)**: Mede a rentabilidade da produção
       - 💰 **Volume Total de Vendas (R$)**: Mostra o desempenho comercial
       - 📊 **Margem de Lucro (%)**: Indicador da eficiência da operação
       - 🚚 **Custo Médio Logístico por Tonelada**: Avalia a eficiência da distribuição
       
    5. **Gráficos Implementados:**
       - 📌 **Gráfico de Barras – Lucro por Produto**: Comparar a lucratividade dos diferentes produtos
       - 📆 **Gráfico de Linhas – Evolução de Vendas**: Acompanhar a performance temporal
       - 🌍 **Gráfico de Pizza – Vendas por Região**: Visualizar concentração de vendas
       - 🏭 **Gráfico de Colunas – Custo vs Lucro por Fábrica**: Entender variações entre unidades
    """)

else:
    st.error("❌ Não foi possível carregar os dados. Verifique se o arquivo 'mineração.csv' está presente no diretório.")

