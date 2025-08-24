import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard ENEM 2024 - Escolas do RN",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def carregar_dados():
    """
    Carrega e processa os dados do ENEM 2024
    """
    try:
        # Carrega os dados
        df = pd.read_csv('data-raw/RESULTADOS_2024_RN.csv', sep=';', encoding='latin-1')
        
        # Filtra apenas registros com nome da escola e scores válidos
        df_clean = df.dropna(subset=['NOME_ESCOLA', 'SCORE_FINAL'])
        
        # Mapear dependência administrativa para nomes legíveis
        dep_map = {
            1: 'Federal',
            2: 'Estadual', 
            3: 'Municipal',
            4: 'Privada'
        }
        df_clean = df_clean.copy()  # Criar cópia explícita para evitar warning
        df_clean['DEPENDENCIA_NOME'] = df_clean['TP_DEPENDENCIA_ADM_ESC'].map(dep_map)
        
        # Agrupa por escola
        escola_stats = df_clean.groupby(['NOME_ESCOLA', 'NO_MUNICIPIO_ESC', 'TP_DEPENDENCIA_ADM_ESC', 'DEPENDENCIA_NOME']).agg({
            'NU_NOTA_CN': 'mean',
            'NU_NOTA_CH': 'mean', 
            'NU_NOTA_LC': 'mean',
            'NU_NOTA_MT': 'mean',
            'NU_NOTA_REDACAO': 'mean',
            'SCORE_OBJETIVA': 'mean',
            'SCORE_FINAL': 'mean',
            'CO_ESCOLA': 'count'
        }).round(1).reset_index()
        
        # Renomeia as colunas
        escola_stats.columns = ['NOME_ESCOLA', 'Municipio', 'TP_DEPENDENCIA_ADM_ESC', 'DEPENDENCIA_NOME', 
                               'Nota_CN', 'Nota_CH', 'Nota_LC', 'Nota_MT', 'Nota_Redacao', 
                               'SCORE_OBJETIVA', 'SCORE_FINAL', 'Participantes']
        
        # Filtra escolas com pelo menos 10 participantes
        escola_stats = escola_stats[escola_stats['Participantes'] >= 5]
        
        # Renomeia colunas para exibição mais limpa
        escola_stats = escola_stats.rename(columns={
            'NU_NOTA_CN': 'Nota_CN',
            'NU_NOTA_CH': 'Nota_CH',
            'NU_NOTA_LC': 'Nota_LC', 
            'NU_NOTA_MT': 'Nota_MT',
            'NU_NOTA_REDACAO': 'Nota_Redacao',
            'CO_ESCOLA': 'Participantes'
        })
        
        # Cria classificação baseada no Score Final
        escola_stats = escola_stats.sort_values('SCORE_FINAL', ascending=False).reset_index(drop=True)
        escola_stats['Classificacao'] = escola_stats.index + 1
        
        # Adiciona categoria de desempenho
        def categoria_desempenho(score):
            if score >= 650: return 'Excelente'
            elif score >= 600: return 'Muito Bom'
            elif score >= 550: return 'Bom'
            elif score >= 500: return 'Regular'
            else: return 'Baixo'
        
        escola_stats['Categoria_Desempenho'] = escola_stats['SCORE_FINAL'].apply(categoria_desempenho)
        
        return escola_stats
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

@st.cache_data
def carregar_dados_top10():
    """
    Carrega e processa os dados considerando apenas os 10 melhores alunos por escola
    """
    try:
        # Carrega os dados originais
        df = pd.read_csv('data-raw/RESULTADOS_2024_RN.csv', sep=';', encoding='latin-1')
        
        # Filtra apenas registros com nome da escola e scores válidos
        df_clean = df.dropna(subset=['NOME_ESCOLA', 'SCORE_FINAL'])
        
        # Mapeia dependência administrativa
        dep_map = {
            1: 'Federal',
            2: 'Estadual', 
            3: 'Municipal',
            4: 'Privada'
        }
        df_clean = df_clean.copy()
        df_clean['DEPENDENCIA_NOME'] = df_clean['TP_DEPENDENCIA_ADM_ESC'].map(dep_map)
        
        # Para cada escola, pega apenas os 10 melhores alunos baseado no SCORE_FINAL
        top10_por_escola = []
        
        for escola in df_clean['NOME_ESCOLA'].unique():
            escola_data = df_clean[df_clean['NOME_ESCOLA'] == escola]
            # Ordena por SCORE_FINAL decrescente e pega os 10 primeiros
            top10_escola = escola_data.nlargest(10, 'SCORE_FINAL')
            top10_por_escola.append(top10_escola)
        
        # Concatena todos os top10 de cada escola
        df_top10 = pd.concat(top10_por_escola, ignore_index=True)
        
        # Agrupa por escola (agora com apenas os top 10 alunos de cada)
        escola_stats_top10 = df_top10.groupby(['NOME_ESCOLA', 'NO_MUNICIPIO_ESC', 'TP_DEPENDENCIA_ADM_ESC', 'DEPENDENCIA_NOME']).agg({
            'NU_NOTA_CN': 'mean',
            'NU_NOTA_CH': 'mean', 
            'NU_NOTA_LC': 'mean',
            'NU_NOTA_MT': 'mean',
            'NU_NOTA_REDACAO': 'mean',
            'SCORE_OBJETIVA': 'mean',
            'SCORE_FINAL': 'mean',
            'CO_ESCOLA': 'count'
        }).round(1).reset_index()
        
        # Renomeia as colunas
        escola_stats_top10.columns = ['NOME_ESCOLA', 'Municipio', 'TP_DEPENDENCIA_ADM_ESC', 'DEPENDENCIA_NOME', 
                                     'Nota_CN', 'Nota_CH', 'Nota_LC', 'Nota_MT', 'Nota_Redacao', 
                                     'SCORE_OBJETIVA', 'SCORE_FINAL', 'Top_Alunos_Considerados']
        
        # Filtra apenas escolas com pelo menos 3 alunos no top 10 (para ter uma amostra mínima)
        escola_stats_top10 = escola_stats_top10[escola_stats_top10['Top_Alunos_Considerados'] >= 3]
        
        # Cria classificação baseada no Score Final do Top 10
        escola_stats_top10 = escola_stats_top10.sort_values('SCORE_FINAL', ascending=False).reset_index(drop=True)
        escola_stats_top10['Classificacao_Top10'] = escola_stats_top10.index + 1
        
        # Adiciona categoria de desempenho
        def categoria_desempenho(score):
            if score >= 650: return 'Excelente'
            elif score >= 600: return 'Muito Bom'
            elif score >= 550: return 'Bom'
            elif score >= 500: return 'Regular'
            else: return 'Baixo'
        
        escola_stats_top10['Categoria_Desempenho_Top10'] = escola_stats_top10['SCORE_FINAL'].apply(categoria_desempenho)
        
        return escola_stats_top10
        
    except Exception as e:
        st.error(f"Erro ao carregar dados top 10: {e}")
        return None

def main():
    """
    Função principal do dashboard
    """
    # Título principal
    st.title("📊 Dashboard ENEM 2024 - Escolas do Rio Grande do Norte")
    st.markdown("---")
    
    # Carrega dados
    with st.spinner("Carregando dados..."):
        df = carregar_dados()
    
    if df is None:
        st.error("Erro ao carregar os dados. Verifique se o arquivo está no local correto.")
        return
    
    # Sidebar para filtros
    st.sidebar.header("🔧 Filtros")
    
    # Filtro por escola
    escolas_disponiveis = ['Todas'] + sorted(df['NOME_ESCOLA'].unique().tolist())
    escola_selecionada = st.sidebar.selectbox(
        "Selecione uma escola:",
        escolas_disponiveis,
        help="Filtrar por uma escola específica"
    )
    
    # Filtro por dependência administrativa
    dependencias_disponiveis = sorted(df['DEPENDENCIA_NOME'].unique().tolist())
    dependencia_selecionada = st.sidebar.multiselect(
        "Dependência Administrativa:",
        dependencias_disponiveis,
        default=dependencias_disponiveis,
        help="Filtrar por tipo de dependência administrativa"
    )
    
    # Filtro por município
    municipios_disponiveis = ['Todos'] + sorted(df['Municipio'].unique().tolist())
    municipio_selecionado = st.sidebar.selectbox(
        "Município:",
        municipios_disponiveis,
        help="Filtrar por município"
    )
    
    # Filtro por número mínimo de participantes
    min_participantes = st.sidebar.slider(
        "Mínimo de Participantes:",
        min_value=1,
        max_value=int(df['Participantes'].max()),
        value=10,
        help="Filtrar escolas com pelo menos N participantes"
    )
    
    # Aplica filtros
    df_filtrado = df.copy()
    
    if escola_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['NOME_ESCOLA'] == escola_selecionada]
    
    if dependencia_selecionada:
        df_filtrado = df_filtrado[df_filtrado['DEPENDENCIA_NOME'].isin(dependencia_selecionada)]
    
    if municipio_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Municipio'] == municipio_selecionado]
    
    df_filtrado = df_filtrado[df_filtrado['Participantes'] >= min_participantes]
    
    # Informações gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏫 Escolas", len(df_filtrado))
    with col2:
        st.metric("👥 Participantes", f"{df_filtrado['Participantes'].sum():,}")
    with col3:
        st.metric("📊 Score Médio", f"{df_filtrado['SCORE_FINAL'].mean():.1f}")
    with col4:
        st.metric("🏆 Melhor Score", f"{df_filtrado['SCORE_FINAL'].max():.1f}")
    
    st.markdown("---")
    
    # Gráficos principais
    if len(df_filtrado) > 0:
        
        # Seção 1: Ranking das Escolas
        st.header("🏆 Ranking das Escolas por Score Final")
        
        # Limita a 20 melhores para visualização
        top_escolas = df_filtrado.head(20)
        
        fig_ranking = px.bar(
            top_escolas,
            y='NOME_ESCOLA',
            x='SCORE_FINAL',
            color='DEPENDENCIA_NOME',
            title="Top 20 Escolas por Score Final",
            hover_data=['Municipio', 'Participantes', 'Classificacao'],
            color_discrete_map={
                'Federal': '#FF6B6B',
                'Estadual': '#4ECDC4', 
                'Municipal': '#45B7D1',
                'Privada': '#96CEB4'
            }
        )
        fig_ranking.update_layout(
            height=600,
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_ranking, use_container_width=True)
        
        # Seção 2: Análise por Áreas de Conhecimento
        st.header("📚 Desempenho por Área de Conhecimento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico radar das melhores escolas
            if len(df_filtrado) >= 5:
                top_5 = df_filtrado.head(5)
                
                fig_radar = go.Figure()
                
                areas = ['Nota_CN', 'Nota_CH', 'Nota_LC', 'Nota_MT', 'Nota_Redacao']
                area_names = ['Ciências Natureza', 'Ciências Humanas', 'Linguagens', 'Matemática', 'Redação']
                
                for i, row in top_5.iterrows():
                    valores = [row[area] for area in areas]
                    escola_nome = row['NOME_ESCOLA']
                    if len(escola_nome) > 30:
                        escola_nome = escola_nome[:27] + "..."
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=valores,
                        theta=area_names,
                        fill='toself',
                        name=escola_nome
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[400, 700]
                        )),
                    title="Top 5 Escolas - Perfil por Área",
                    height=400
                )
                st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # Distribuição de scores por dependência
            fig_box = px.box(
                df_filtrado,
                x='DEPENDENCIA_NOME',
                y='SCORE_FINAL',
                title="Distribuição de Scores por Dependência",
                color='DEPENDENCIA_NOME',
                color_discrete_map={
                    'Federal': '#FF6B6B',
                    'Estadual': '#4ECDC4', 
                    'Municipal': '#45B7D1',
                    'Privada': '#96CEB4'
                }
            )
            fig_box.update_layout(height=400)
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Seção 3: Scatter Plot Score Objetiva vs Redação
        st.header("📈 Correlação: Score Objetiva vs Redação")
        
        fig_scatter = px.scatter(
            df_filtrado,
            x='SCORE_OBJETIVA',
            y='Nota_Redacao',
            size='Participantes',
            color='DEPENDENCIA_NOME',
            hover_data=['NOME_ESCOLA', 'Municipio', 'Classificacao'],
            title="Relação entre Score Objetiva e Nota da Redação",
            color_discrete_map={
                'Federal': '#FF6B6B',
                'Estadual': '#4ECDC4', 
                'Municipal': '#45B7D1',
                'Privada': '#96CEB4'
            }
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Seção 4: Score Final vs Número de Participantes
        st.header("🎯 Score Final vs Número de Participantes")
        
        # Adicionar informações sobre a relação
        st.markdown("""
        **💡 Interpretação do gráfico:**
        - **Eixo X**: Número de participantes por escola
        - **Eixo Y**: Score final médio da escola
        - **Tamanho do ponto**: Proporcional ao número de participantes
        - **Cor**: Tipo de dependência administrativa
        
        **🎯 O que observar:**
        - Escolas no **canto superior direito** têm alto score E muitos participantes (performance mais confiável)
        - Escolas no **canto superior esquerdo** têm alto score mas poucos participantes (podem ser outliers)
        - A **linha de tendência** mostra se há correlação entre número de participantes e performance
        """)
        
        fig_scatter_participantes = px.scatter(
            df_filtrado,
            x='Participantes',
            y='SCORE_FINAL',
            size='Participantes',
            color='DEPENDENCIA_NOME',
            hover_data=['NOME_ESCOLA', 'Municipio', 'Classificacao'],
            title='Score Final vs Número de Participantes por Escola',
            labels={
                'Participantes': 'Número de Participantes',
                'SCORE_FINAL': 'Score Final Médio',
                'NOME_ESCOLA': 'Escola',
                'DEPENDENCIA_NOME': 'Dependência'
            },
            color_discrete_map={
                'Federal': '#FF6B6B',
                'Estadual': '#4ECDC4', 
                'Municipal': '#45B7D1',
                'Privada': '#96CEB4'
            },
            trendline="ols"  # Adiciona linha de tendência
        )
        
        fig_scatter_participantes.update_layout(
            height=600,
            showlegend=True
        )
        
        # Customizar hover template
        fig_scatter_participantes.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>" +
                          "Participantes: %{x}<br>" +
                          "Score Final: %{y:.1f}<br>" +
                          "Dependência: %{customdata[3]}<br>" +
                          "Município: %{customdata[1]}<br>" +
                          "Classificação: #%{customdata[2]}<br>" +
                          "<extra></extra>"
        )
        
        st.plotly_chart(fig_scatter_participantes, use_container_width=True)
        
        # Análise estatística da correlação
        correlacao = df_filtrado['Participantes'].corr(df_filtrado['SCORE_FINAL'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Correlação", f"{correlacao:.3f}")
        with col2:
            if correlacao > 0.3:
                interpretacao = "Positiva Moderada"
                emoji = "📈"
            elif correlacao > 0.1:
                interpretacao = "Positiva Fraca"
                emoji = "📊"
            elif correlacao < -0.3:
                interpretacao = "Negativa Moderada"
                emoji = "📉"
            elif correlacao < -0.1:
                interpretacao = "Negativa Fraca"
                emoji = "📊"
            else:
                interpretacao = "Muito Fraca"
                emoji = "➡️"
            st.metric(f"{emoji} Interpretação", interpretacao)
        with col3:
            # Escolas com alto score e muitos participantes (mais confiáveis)
            confiáveis = df_filtrado[(df_filtrado['SCORE_FINAL'] >= df_filtrado['SCORE_FINAL'].quantile(0.75)) & 
                                   (df_filtrado['Participantes'] >= df_filtrado['Participantes'].quantile(0.5))]
            st.metric("🏆 Escolas Confiáveis", len(confiáveis))
        
        # Seção 5: Ranking dos Top 10 Alunos por Escola
        st.header("🌟 Ranking Baseado nos Top 10 Alunos por Escola")
        
        st.markdown("""
        **💡 Esta análise considera apenas os 10 melhores alunos de cada escola:**
        - Mostra o **potencial máximo** de cada escola
        - Útil para identificar escolas que produzem **excelência acadêmica**
        - Complementa a análise da média geral (que pode ser afetada por alunos com dificuldades)
        - Escolas com menos de 3 alunos no top 10 são excluídas para garantir representatividade
        """)
        
        # Carrega dados do top 10
        with st.spinner("Calculando estatísticas dos top 10 alunos por escola..."):
            df_top10 = carregar_dados_top10()
        
        if df_top10 is not None and len(df_top10) > 0:
            # Aplica os mesmos filtros da análise principal
            df_top10_filtrado = df_top10.copy()
            
            if escola_selecionada != 'Todas':
                df_top10_filtrado = df_top10_filtrado[df_top10_filtrado['NOME_ESCOLA'] == escola_selecionada]
            
            if dependencia_selecionada:
                df_top10_filtrado = df_top10_filtrado[df_top10_filtrado['DEPENDENCIA_NOME'].isin(dependencia_selecionada)]
            
            if municipio_selecionado != 'Todos':
                df_top10_filtrado = df_top10_filtrado[df_top10_filtrado['Municipio'] == municipio_selecionado]
            
            if len(df_top10_filtrado) > 0:
                # Informações do top 10
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("🏫 Escolas (Top 10)", len(df_top10_filtrado))
                with col2:
                    st.metric("👑 Score Médio (Top 10)", f"{df_top10_filtrado['SCORE_FINAL'].mean():.1f}")
                with col3:
                    st.metric("🥇 Melhor Score (Top 10)", f"{df_top10_filtrado['SCORE_FINAL'].max():.1f}")
                with col4:
                    # Comparação com a média geral
                    if len(df_filtrado) > 0:
                        diferenca = df_top10_filtrado['SCORE_FINAL'].mean() - df_filtrado['SCORE_FINAL'].mean()
                        st.metric("📈 Diferença vs Média Geral", f"+{diferenca:.1f}")
                
                # Gráfico de comparação: Média Geral vs Top 10
                st.subheader("📊 Comparação: Média Geral vs Top 10 Alunos")
                
                # Prepara dados para comparação
                escolas_comuns = set(df_filtrado['NOME_ESCOLA']) & set(df_top10_filtrado['NOME_ESCOLA'])
                
                if escolas_comuns:
                    df_comparacao = []
                    
                    for escola in list(escolas_comuns)[:15]:  # Limita a 15 escolas para visualização
                        score_geral = df_filtrado[df_filtrado['NOME_ESCOLA'] == escola]['SCORE_FINAL'].iloc[0]
                        score_top10 = df_top10_filtrado[df_top10_filtrado['NOME_ESCOLA'] == escola]['SCORE_FINAL'].iloc[0]
                        
                        df_comparacao.append({'Escola': escola, 'Tipo': 'Média Geral', 'Score': score_geral})
                        df_comparacao.append({'Escola': escola, 'Tipo': 'Top 10 Alunos', 'Score': score_top10})
                    
                    df_comp = pd.DataFrame(df_comparacao)
                    
                    fig_comp = px.bar(
                        df_comp,
                        x='Escola',
                        y='Score',
                        color='Tipo',
                        barmode='group',
                        title='Comparação: Score Médio Geral vs Top 10 Alunos por Escola',
                        color_discrete_map={
                            'Média Geral': '#45B7D1',
                            'Top 10 Alunos': '#FF6B6B'
                        }
                    )
                    fig_comp.update_layout(
                        xaxis_tickangle=-45,
                        height=500,
                        xaxis_title="Escola",
                        yaxis_title="Score Final"
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
                
                # Tabela detalhada do top 10
                st.subheader("📋 Ranking Detalhado - Top 10 Alunos por Escola")
                
                df_top10_display = df_top10_filtrado[[
                    'Classificacao_Top10', 'NOME_ESCOLA', 'Municipio', 'DEPENDENCIA_NOME',
                    'Nota_CN', 'Nota_CH', 'Nota_LC', 'Nota_MT', 'Nota_Redacao',
                    'SCORE_OBJETIVA', 'SCORE_FINAL', 'Top_Alunos_Considerados', 'Categoria_Desempenho_Top10'
                ]].copy()
                
                # Renomeia colunas para exibição
                df_top10_display.columns = [
                    'Classificação Top 10', 'Nome da Escola', 'Município', 'Dependência',
                    'CN', 'CH', 'LC', 'MT', 'Redação',
                    'Score Objetiva', 'Score Final', 'Alunos Top 10', 'Categoria'
                ]
                
                # Busca na tabela top 10
                busca_top10 = st.text_input("🔍 Buscar na tabela Top 10:", placeholder="Digite o nome da escola...")
                
                if busca_top10:
                    df_top10_display = df_top10_display[df_top10_display['Nome da Escola'].str.contains(busca_top10, case=False, na=False)]
                
                # Exibe tabela do top 10
                st.dataframe(
                    df_top10_display,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Score Final": st.column_config.NumberColumn(
                            "Score Final",
                            help="Score final médio dos top 10 alunos",
                            format="%.1f"
                        ),
                        "Alunos Top 10": st.column_config.NumberColumn(
                            "Alunos Top 10",
                            help="Número de alunos considerados no top 10 desta escola"
                        )
                    }
                )
            else:
                st.warning("⚠️ Nenhuma escola encontrada com os filtros aplicados para análise do Top 10.")
        else:
            st.error("❌ Erro ao carregar dados do Top 10.")
        
        # Seção 6: Tabela Detalhada Geral
        st.header("📋 Dados Detalhados das Escolas (Média Geral)")
        
        # Prepara dados para exibição
        df_display = df_filtrado[[
            'Classificacao', 'NOME_ESCOLA', 'Municipio', 'DEPENDENCIA_NOME',
            'Nota_CN', 'Nota_CH', 'Nota_LC', 'Nota_MT', 'Nota_Redacao',
            'SCORE_OBJETIVA', 'SCORE_FINAL', 'Participantes', 'Categoria_Desempenho'
        ]].copy()
        
        # Renomeia colunas para exibição
        df_display.columns = [
            'Classificação', 'Nome da Escola', 'Município', 'Dependência',
            'CN', 'CH', 'LC', 'MT', 'Redação',
            'Score Objetiva', 'Score Final', 'Participantes', 'Categoria'
        ]
        
        # Opção de busca na tabela
        busca_tabela = st.text_input("🔍 Buscar na tabela:", placeholder="Digite o nome da escola...")
        
        if busca_tabela:
            df_display = df_display[df_display['Nome da Escola'].str.contains(busca_tabela, case=False, na=False)]
        
        # Exibe tabela com formatação
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score Final": st.column_config.NumberColumn(
                    "Score Final",
                    help="Score final médio da escola",
                    format="%.1f"
                ),
                "Participantes": st.column_config.NumberColumn(
                    "Participantes",
                    help="Número total de participantes da escola"
                )
            }
        )
        
        # Download dos dados
        st.subheader("📥 Download dos Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Download da tabela geral
            csv_geral = df_display.to_csv(index=False)
            st.download_button(
                label="📊 Download Dados Gerais (CSV)",
                data=csv_geral,
                file_name="enem_2024_rn_ranking_geral.csv",
                mime="text/csv"
            )
        
        with col2:
            # Download da tabela top 10 (se disponível)
            if 'df_top10_filtrado' in locals() and len(df_top10_filtrado) > 0:
                csv_top10 = df_top10_display.to_csv(index=False)
                st.download_button(
                    label="🌟 Download Top 10 (CSV)",
                    data=csv_top10,
                    file_name="enem_2024_rn_ranking_top10.csv",
                    mime="text/csv"
                )
    
    else:
        st.warning("⚠️ Nenhuma escola encontrada com os filtros aplicados.")
    
    # Rodapé
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>📊 <strong>Dashboard ENEM 2024 - Rio Grande do Norte</strong></p>
        <p>Dados: INEP/MEC | Processamento: Python/Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
