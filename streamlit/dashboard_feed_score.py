import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Optional

# Configuração inicial da página
st.set_page_config(
    page_title="Análise de Feedback de Funcionários",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .header-text { 
        color: #000000;
        font-family: 'Arial';
        border-bottom: 2px solid #000000;
        padding-bottom: 10px;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8F9FA;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .data-table {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }
    .plot-container {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Carregando dados...")
def load_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Carrega e otimiza os dados do arquivo CSV
    
    Parâmetros:
        file_path (str): Caminho do arquivo CSV
        
    Retorna:
        pd.DataFrame: DataFrame com dados processados ou None em caso de erro
    """
    try:
        df = pd.read_csv(
            file_path,
            usecols=['name', 'feedback_score', 'department', 'position'],
            dtype={
                'name': 'category',
                'department': 'category',
                'position': 'category',
                'feedback_score': 'float32'
            }
        )
        return df.dropna(subset=['feedback_score'])
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

def display_basic_stats(df: pd.DataFrame) -> None:
    """
    Exibe métricas básicas de feedback
    
    Parâmetros:
        df (pd.DataFrame): DataFrame com dados dos funcionários
    """
    stats = df['feedback_score'].describe()
    
    cols = st.columns(4)
    with cols[0]:
        st.metric("📊 Média", f"{stats['mean']:.2f}")
    with cols[1]:
        st.metric("📈 Mediana", f"{stats['50%']:.2f}")
    with cols[2]:
        st.metric("📉 Desvio Padrão", f"{stats['std']:.2f}")
    with cols[3]:
        st.metric("🎯 Variação", f"{stats['max'] - stats['min']:.2f}")

def plot_interactive_distribution(df: pd.DataFrame) -> None:
    """
    Cria histograma interativo de distribuição de feedback
    
    Parâmetros:
        df (pd.DataFrame): DataFrame com dados dos funcionários
    """
    fig = px.histogram(
        df,
        x='feedback_score',
        nbins=20,
        color_discrete_sequence=['#333333'],
        labels={'feedback_score': 'Score de Feedback'},
        title='Distribuição dos Scores de Feedback'
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        xaxis_title="Score de Feedback",
        yaxis_title="Quantidade de Funcionários",
        bargap=0.1
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_interactive_boxplot(df: pd.DataFrame) -> None:
    """
    Cria boxplot interativo por departamento
    
    Parâmetros:
        df (pd.DataFrame): DataFrame com dados dos funcionários
    """
    fig = px.box(
        df,
        x='department',
        y='feedback_score',
        color='department',
        color_discrete_sequence=px.colors.qualitative.Dark24,
        labels={'department': 'Departamento', 'feedback_score': 'Score de Feedback'},
        title='Distribuição por Departamento'
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        xaxis_title="Departamento",
        yaxis_title="Score de Feedback",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

def display_top_employees(df: pd.DataFrame) -> None:
    """
    Exibe tabela com os melhores funcionários
    
    Parâmetros:
        df (pd.DataFrame): DataFrame com dados dos funcionários
    """
    top_df = df.nlargest(5, 'feedback_score')[['name', 'feedback_score', 'department', 'position']]
    top_df.columns = ['Nome', 'Score', 'Departamento', 'Cargo']
    
    st.markdown("### 🏆 Top 5 Funcionários")
    st.dataframe(
        top_df.style.format({'Score': '{:.2f}'}),
        use_container_width=True,
        hide_index=True
    )

def display_department_stats(df: pd.DataFrame) -> None:
    """
    Exibe estatísticas por departamento
    
    Parâmetros:
        df (pd.DataFrame): DataFrame com dados dos funcionários
    """
    dept_stats = df.groupby('department')['feedback_score'].agg(['mean', 'count'])
    dept_stats.columns = ['Média', 'Qtd. Funcionários']
    dept_stats['Média'] = dept_stats['Média'].round(2)
    
    st.markdown("### 📦 Estatísticas por Departamento")
    st.dataframe(
        dept_stats.style.background_gradient(cmap='Greys'),
        use_container_width=True
    )

def main():
    """Função principal do dashboard"""
    st.markdown('<h1 class="header-text">📈 Análise de Feedback de Funcionários</h1>', unsafe_allow_html=True)
    
    # Carregar dados
    df = load_data('../data/processed/hr_dashboard_data_atualizado.csv')
    
    if df is not None:
        # Filtros interativos
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                min_score = st.slider(
                    "🔍 Filtro Mínimo de Feedback",
                    min_value=float(df['feedback_score'].min()),
                    max_value=float(df['feedback_score'].max()),
                    value=float(df['feedback_score'].quantile(0.25)),
                    step=0.5
                )
            
            with col2:
                selected_dept = st.selectbox(
                    "🏢 Selecionar Departamento",
                    options=['Todos'] + list(df['department'].unique())
                )
        
        # Aplicar filtros
        filtered_df = df[df['feedback_score'] >= min_score]
        if selected_dept != 'Todos':
            filtered_df = filtered_df[filtered_df['department'] == selected_dept]
        
        # Seção de métricas
        with st.container():
            st.markdown("### 📋 Métricas Principais")
            display_basic_stats(filtered_df)
        
        # Layout em grid
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # Gráficos
            with st.container():
                st.markdown("### 📊 Visualizações Interativas")
                plot_interactive_distribution(filtered_df)
                plot_interactive_boxplot(filtered_df)
        
        with col_right:
            # Tabelas e insights
            with st.container():
                st.markdown("### 📌 Insights e Destaques")
                display_top_employees(filtered_df)
                display_department_stats(filtered_df)
                
                # Análise explicativa
                with st.expander("🔍 Metodologia da Análise"):
                    st.markdown("""
                        **Metodologia Utilizada:**
                        - Dados filtrados a partir do dataset principal
                        - Análise estatística descritiva
                        - Agrupamento por departamento
                        - Visualizações interativas com Plotly
                        - Filtros dinâmicos para exploração de dados
                    """)

if __name__ == "__main__":
    main()