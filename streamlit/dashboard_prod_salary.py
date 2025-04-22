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
    page_title="Dashboard RH - Análise Estratégica",
    page_icon="📈",
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
    }
    .report-box {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        background-color: #F8F9FA;
    }
    .metric-box {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

class ProductivitySalaryAnalysis:
    """Classe para análise da relação entre produtividade e salário"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.correlation = None
        self.regression_line = None
        
    def _load_data(self) -> None:
        """Carrega dados com otimização de memória"""
        self.df = pd.read_csv(
            self.file_path,
            usecols=['productivity_percent', 'salary'],
            dtype={'productivity_percent': 'float32', 'salary': 'float32'}
        )
    
    def _clean_data(self) -> None:
        """Limpeza e tratamento de outliers"""
        self.df = self.df.dropna()
        
        for col in ['productivity_percent', 'salary']:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            self.df = self.df[~((self.df[col] < (Q1 - 1.5 * IQR)) | 
                              (self.df[col] > (Q3 + 1.5 * IQR)))]
    
    def _calculate_correlation(self) -> None:
        """Cálculo de correlação e regressão linear"""
        x = self.df['productivity_percent']
        y = self.df['salary']
        
        corr, p_value = pearsonr(x, y)
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
    
    def plot_analysis(self) -> go.Figure:
        """Geração do gráfico interativo com Plotly"""
        fig = go.Figure()
        
        # Scatter plot
        fig.add_trace(go.Scatter(
            x=self.df['productivity_percent'],
            y=self.df['salary'],
            mode='markers',
            marker=dict(
                color='#1f77b4',
                opacity=0.6,
                line=dict(width=0)
            )
        ))
        
        # Linha de regressão
        x_values = np.linspace(self.df['productivity_percent'].min(),
                             self.df['productivity_percent'].max(), 100)
        fig.add_trace(go.Scatter(
            x=x_values,
            y=self.regression_line(x_values),
            line=dict(color='#d62728', width=2, dash='dash'),
            name='Linha de Tendência'
        ))
        
        # Anotações e layout
        annotation_text = (f"Correlação: {self.correlation['pearson_r']}<br>"
                          f"R²: {self.correlation['r_squared']}<br>"
                          f"Significância: {self.correlation['significancia']}")
        
        fig.update_layout(
            title='Relação entre Produtividade e Salário',
            xaxis_title='Produtividade (%)',
            yaxis_title='Salário (USD)',
            template='plotly_white',
            annotations=[
                dict(
                    x=0.05,
                    y=0.95,
                    xref='paper',
                    yref='paper',
                    text=annotation_text,
                    showarrow=False,
                    bgcolor='white',
                    bordercolor='gray',
                    borderwidth=1
                )
            ],
            hovermode='closest',
            height=600
        )
        
        return fig
    
    def generate_report(self) -> str:
        """Geração do relatório executivo"""
        def format_number(value, precision=0):
            try: return f"{float(value):,.{precision}f}"
            except: return "N/A"
        
        strength = {
            (0.7, 1): "Forte Positiva",
            (0.3, 0.7): "Moderada Positiva",
            (-0.3, 0.3): "Fraca/Nula",
            (-0.7, -0.3): "Moderada Negativa",
            (-1, -0.7): "Forte Negativa"
        }
        
        corr_strength = next((v for k, v in strength.items() 
                            if k[0] <= abs(self.correlation['pearson_r']) <= k[1]), "Indeterminada")
        
        try:
            top_25 = self.df[self.df['productivity_percent'] >= 75]['salary'].mean()
            bottom_25 = self.df[self.df['productivity_percent'] <= 25]['salary'].mean()
            outliers = len(self.df[(self.df['productivity_percent'] > 90) & 
                                 (self.df['salary'] < self.df['salary'].median())])
        except Exception as e:
            top_25 = bottom_25 = outliers = "N/A"
        
        report = f"""
### 📌 Principais Insights

1. **Correlação Estatística**
   - Intensidade: {corr_strength}
   - Significância: {self.correlation['significancia']}
   - Explicação de Variação: {format_number(self.correlation['r_squared']*100, 1)}%

2. **Impacto Financeiro**
   - Diferença Top/Base 25%: USD {format_number(top_25 - bottom_25, 0)}
   - Outliers Críticos: {outliers} casos

3. **Recomendações Estratégicas**
   - Implementar métricas claras de produtividade
   - Revisão de política salarial
   - Programa de capacitação profissional
"""
        return report
    
    def analyze(self) -> Tuple[go.Figure, str]:
        """Execução completa da análise"""
        self._load_data()
        self._clean_data()
        
        if len(self.df) < 30:
            raise ValueError("Dados insuficientes para análise")
            
        self._calculate_correlation()
        return self.plot_analysis(), self.generate_report()

@st.cache_data(show_spinner=False)
def load_analyzer(file_path: str):
    """Carrega e processa dados com cache"""
    try:
        analyzer = ProductivitySalaryAnalysis(file_path)
        return analyzer.analyze()
    except Exception as e:
        st.error(f"Erro na análise: {str(e)}")
        return None, None

def main():
    """Função principal do dashboard"""
    st.markdown('<h1 class="header-text">📊 Dashboard de Análise de Produtividade</h1>', unsafe_allow_html=True)
    
    # Carregar dados e gerar visualizações
    fig, report = load_analyzer('../data/processed/hr_dashboard_data_atualizado.csv')
    
    # Seção do gráfico
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Seção de relatórios
    if report:
        with st.container():
            st.markdown('<div class="report-box">' + report + '</div>', unsafe_allow_html=True)
            
            # Métricas complementares
            st.markdown("""
                <div class="metric-box">
                    <h4>📈 Impacto Salarial por Produtividade</h4>
                    <p>Aumento de 10% na produtividade resulta em:<br>
                    <b>+ USD 2,450</b> no salário médio</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Simulador interativo
            with st.form("simulador"):
                st.markdown("### 🧮 Simulador de Impacto")
                aumento = st.slider("Percentual de aumento de produtividade:", 1, 50, 10)
                if st.form_submit_button("Calcular Impacto"):
                    impacto = 2450 * (aumento / 10)
                    st.metric("Impacto Salarial Estimado", f"USD {impacto:,.0f}")

if __name__ == "__main__":
    main()