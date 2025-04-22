# Importações necessárias
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import seaborn as sns
from scipy.stats import pearsonr
from typing import Tuple, Dict

# Configuração inicial da página
st.set_page_config(
    page_title="Análise de Satisfação vs Feedback",
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
    .report-box {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 25px;
        margin: 20px 0;
        background-color: #F8F9FA;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-box {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        padding: 20px;
        margin: 15px 0;
    }
    .stSlider>div>div>div>div {
        background-color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

class SatisfactionFeedbackAnalysis:
    """
    Classe para análise da relação entre satisfação e feedback
    Mantém a lógica original com otimizações para o dashboard
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.correlation = None
        self.regression_line = None
        
    def _load_data(self) -> None:
        """Carrega dados com otimização de memória"""
        try:
            self.df = pd.read_csv(
                self.file_path,
                usecols=['satisfaction_rate_percent', 'feedback_score'],
                dtype={'satisfaction_rate_percent': 'float32', 'feedback_score': 'float32'}
            )
        except FileNotFoundError:
            raise ValueError("Arquivo de dados não encontrado")
            
    def _clean_data(self) -> None:
        """Tratamento de dados e outliers"""
        if self.df is None:
            return
            
        # Remoção de valores faltantes
        self.df = self.df.dropna()
        
        # Filtro de outliers usando IQR
        for col in self.df.columns:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            self.df = self.df[~((self.df[col] < (Q1 - 1.5 * IQR)) | 
                              (self.df[col] > (Q3 + 1.5 * IQR)))]
    
    def _calculate_correlation(self) -> None:
        """Cálculo estatístico da correlação"""
        if self.df is None or len(self.df) < 30:
            return
            
        x = self.df['satisfaction_rate_percent']
        y = self.df['feedback_score']
        
        # Cálculo da correlação de Pearson
        corr, p_value = pearsonr(x, y)
        
        # Regressão linear
        coeffs = np.polyfit(x, y, 1)
        self.regression_line = np.poly1d(coeffs)
        
        self.correlation = {
            'pearson_r': round(corr, 3),
            'p_value': p_value,
            'r_squared': round(corr**2, 3),
            'significancia': 'Significativa' if p_value < 0.05 else 'Não Significativa',
            'slope': coeffs[0],
            'intercept': coeffs[1]
        }
    
    def plot_interactive(self) -> go.Figure:
        """Gera gráfico interativo com Plotly"""
        fig = go.Figure()
        
        # Scatter plot
        fig.add_trace(go.Scatter(
            x=self.df['satisfaction_rate_percent'],
            y=self.df['feedback_score'],
            mode='markers',
            marker=dict(
                color='#1f77b4',
                opacity=0.7,
                size=8,
                line=dict(width=0.5, color='white')
            )
        ))
        
        # Linha de regressão
        x_values = np.linspace(
            self.df['satisfaction_rate_percent'].min(),
            self.df['satisfaction_rate_percent'].max(),
            100
        )
        fig.add_trace(go.Scatter(
            x=x_values,
            y=self.regression_line(x_values),
            line=dict(color='#d62728', width=3, dash='dash'),
            name='Linha de Tendência'
        ))
        
        # Layout do gráfico
        fig.update_layout(
            title='Relação entre Satisfação e Feedback',
            xaxis_title='Taxa de Satisfação (%)',
            yaxis_title='Pontuação de Feedback',
            template='plotly_white',
            height=600,
            margin=dict(l=40, r=40, t=80, b=40),
            hovermode='closest',
            annotations=[dict(
                x=0.05,
                y=0.95,
                xref='paper',
                yref='paper',
                text=f"Correlação: {self.correlation['pearson_r']}<br>R²: {self.correlation['r_squared']}",
                showarrow=False,
                bgcolor='white',
                bordercolor='gray'
            )]
        )
        
        return fig
    
    def generate_insights(self) -> str:
        """Gera relatório de insights formatado"""
        if not self.correlation:
            return "Dados insuficientes para gerar insights"
            
        # Formatação numérica segura
        def format_num(value, precision=2):
            try: return f"{float(value):,.{precision}f}"
            except: return "N/A"
        
        # Classificação da correlação
        strength_map = {
            (0.7, 1): "Forte Positiva",
            (0.3, 0.7): "Moderada Positiva",
            (-0.3, 0.3): "Fraca/Nula",
            (-0.7, -0.3): "Moderada Negativa",
            (-1, -0.7): "Forte Negativa"
        }
        
        corr_strength = next(
            (v for k, v in strength_map.items() 
             if k[0] <= abs(self.correlation['pearson_r']) <= k[1]), 
            "Indeterminada"
        )
        
        # Cálculos para o relatório
        try:
            impact = self.correlation['slope'] * 10
            top_25 = self.df[self.df['satisfaction_rate_percent'] >= 75]['feedback_score'].mean()
            bottom_25 = self.df[self.df['satisfaction_rate_percent'] <= 25]['feedback_score'].mean()
        except Exception:
            impact = top_25 = bottom_25 = "N/A"
        
        return f"""

1. **Relação Estatística**
   - **Correlação**: {self.correlation['pearson_r']} ({corr_strength})
   - **Significância**: {self.correlation['significancia']}
   - **Variação Explicada**: {format_num(self.correlation['r_squared']*100, 1)}%

2. **Impacto Operacional**
   - +10% Satisfação → +{format_num(impact, 2)} pts no Feedback
   - Top 25%: {format_num(top_25, 2)} pts
   - Base 25%: {format_num(bottom_25, 2)} pts

3. **Recomendações**
   - Implementar programa de reconhecimento
   - Criar sistema de feedback contínuo
   - Desenvolver planos de ação setoriais
"""

@st.cache_data(show_spinner="Carregando dados...")
def load_analysis(file_path: str):
    """Carrega e processa dados com cache"""
    try:
        analyzer = SatisfactionFeedbackAnalysis(file_path)
        analyzer._load_data()
        analyzer._clean_data()
        if len(analyzer.df) < 30:
            raise ValueError("Dados insuficientes")
        analyzer._calculate_correlation()
        return analyzer
    except Exception as e:
        st.error(f"Erro no processamento: {str(e)}")
        return None

def main():
    """Função principal do dashboard"""
    st.markdown('<h1 class="header-text">📈 Análise de Satisfação vs Feedback</h1>', unsafe_allow_html=True)
    
    # Controles interativos
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col2:
            min_satisfaction = st.slider(
                "Filtro Mínimo de Satisfação",
                0, 100, 0,
                help="Filtrar por taxa mínima de satisfação"
            )
    
    # Carregamento de dados
    analyzer = load_analysis('../data/processed/hr_dashboard_data_atualizado.csv')
    
    if analyzer is not None:
        # Aplicar filtro
        filtered_df = analyzer.df[analyzer.df['satisfaction_rate_percent'] >= min_satisfaction]
        analyzer.df = filtered_df
        
        # Seção do gráfico
        with st.container():
            st.plotly_chart(analyzer.plot_interactive(), use_container_width=True)
        
        # Seção de insights
        with st.container():
            cols = st.columns([2, 1])
            
            with cols[0]:
                st.markdown(
                    f'<div class="report-box">{analyzer.generate_insights()}</div>',
                    unsafe_allow_html=True
                )
            
            with cols[1]:
                st.markdown("""
                    <div class="metric-box">
                        <h4>📊 Estatísticas Chave</h4>
                        <p>Média de Satisfação: <b>{:.1f}%</b></p>
                        <p>Média de Feedback: <b>{:.1f}/10</b></p>
                        <p>Correlação Significativa: <b>{}</b></p>
                    </div>
                """.format(
                    analyzer.df['satisfaction_rate_percent'].mean(),
                    analyzer.df['feedback_score'].mean(),
                    "Sim" if analyzer.correlation['significancia'] == 'Significativa' else "Não"
                ), unsafe_allow_html=True)
                
                # Simulador de impacto
                with st.form("simulador"):
                    st.markdown("### 🧮 Simulador de Impacto")
                    aumento = st.slider(
                        "Aumento de Satisfação (%)",
                        1, 20, 5,
                        help="Selecione o percentual de aumento desejado"
                    )
                    if st.form_submit_button("Calcular"):
                        impacto = analyzer.correlation['slope'] * aumento
                        st.metric(
                            "Impacto Esperado no Feedback",
                            f"+{impacto:.2f} pontos"
                        )

if __name__ == "__main__":
    main()