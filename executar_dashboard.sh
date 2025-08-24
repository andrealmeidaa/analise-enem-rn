#!/bin/bash

echo "🚀 INICIANDO DASHBOARD INTERATIVO STREAMLIT"
echo "=========================================="
echo ""
echo "📊 Dashboard ENEM 2024 - Escolas do RN"
echo "🌐 URL: http://localhost:8501"
echo ""
echo "💡 Funcionalidades:"
echo "   • Filtros por escola, dependência e município"
echo "   • Ranking interativo de escolas"
echo "   • Gráficos de desempenho por área"
echo "   • Tabela com busca e classificação"
echo "   • Download de dados filtrados"
echo ""
echo "⚠️  Para parar o servidor: Ctrl+C"
echo ""

# Navega para o diretório do projeto
cd /home/andre/projects/analise-enem-rn

# Executa o Streamlit
/home/andre/projects/.venv/bin/python -m streamlit run dashboard_escolas.py --server.port 8501 --server.address 0.0.0.0
