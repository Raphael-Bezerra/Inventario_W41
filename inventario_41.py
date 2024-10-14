import streamlit as st
import pandas as pd
import plotly.express as px

# Carregando os dados do arquivo CSV
df = pd.read_csv(r'https://raw.githubusercontent.comRaphael-Bezerra/Inventario_W41/master/inventario_W41.csv')
df.columns = df.columns.str.strip()  # Remove espaços em branco nos nomes das colunas

# Agrupando dados por data para obter o total de pacotes enviados por dia
daily_data = df.groupby('Recebimento')['Qtd'].sum().reset_index()

# Agrupando por data e status para obter as quantidades por subcategoria
status_data = df.groupby(['Recebimento', 'Status'])['Qtd'].sum().unstack().fillna(0)

# Agrupando por data, status e tipo de endereço para obter as quantidades por tipo de endereço
address_data = df.groupby(['Recebimento', 'Status', 'Tipo de Endereço'])['Qtd'].sum().unstack().fillna(0)

# Configurando o layout do Streamlit
st.set_page_config(page_title='Dashboard de Entregas', layout='wide')

# Título da página sem o logo
st.markdown("<h1 style='margin: 0;'>Inventário W41</h1>", unsafe_allow_html=True)

# Adicionando estilo para remover margens da div e definir largura e altura
st.markdown(
    """
    <style>
    .stColumn.st-emotion-cache-j5r0tf {
        margin: 0 !important;  /* Remove margens da div específica */
        padding: 0;  /* Remove padding se necessário */
        width: 68.7px !important;  /* Define a largura da div para 68.7 pixels */
        height: 68.7px !important;  /* Define a altura da div para 68.7 pixels */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Criando uma grade de colunas para as datas
cols = st.columns(len(daily_data))  # Cria colunas suficientes para o número de dias

for index, row in daily_data.iterrows():
    date = row['Recebimento']
    
    with cols[index]:  # Adiciona os elementos na coluna correspondente
        # Criando a data centralizada e em branco
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: -10px;">
                <h4 style="color: white; font-size: 16px; font-weight: bold; padding: 5px; border-radius: 5px; background-color: {'#B3CDE0' if 'on way' in status_data.columns else 'transparent'};">{date}</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Legenda com informações de subcategorias e cores específicas, formatadas como a data
        for status in status_data.columns:
            count = status_data.loc[date, status] if date in status_data.index else 0
            if count > 0:  # Mostra apenas se a contagem for maior que zero
                # Obtendo quantidades de tipos de endereço para o status atual
                residential_count = address_data.loc[date, status, 'Residential'] if ('Residential' in address_data.columns) and (date in address_data.index) and (status in address_data.columns) else 0
                business_count = address_data.loc[date, status, 'Business'] if ('Business' in address_data.columns) and (date in address_data.index) and (status in address_data.columns) else 0
                default_count = address_data.loc[date, status, 'Default'] if ('Default' in address_data.columns) and (date in address_data.index) and (status in address_data.columns) else 0
                
                # Criando a string de endereço somente se houver valores
                address_info = []
                if residential_count > 0:
                    address_info.append(f"R{int(residential_count)}")
                if business_count > 0:
                    address_info.append(f"B{int(business_count)}")
                if default_count > 0:
                    address_info.append(f"D{int(default_count)}")
                
                # Formatando a string final do endereço
                address_info_str = ' - '.join(address_info) if address_info else ''

                color = "#011F4B"  # Cor padrão (On time)

                if status.lower() == 'early' or status.lower() == 'on way':
                    color = "#B3CDE0"  # Verde claro para 'Early' e 'On Way'
                elif 'delay' in status.lower() or 'svc' in status.lower() or 'origem' in status.lower():
                    color = "#005B96"  # Azul para 'Delay'

                # Exibe a informação com a cor e o formato especificado
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-top: 10px;">
                        <h4 style="color: white; font-size: 16px; font-weight: bold; background-color: {color}; padding: 5px; border-radius: 5px;">
                            {status} {int(count)} {address_info_str}
                        </h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# Ajusta a largura das colunas para melhor apresentação
for col in cols:
    col.markdown("<style>div.row {display: flex;}</style>", unsafe_allow_html=True)

# Adicionando gráficos de barras no final do dashboard
st.markdown("---")  # Linha de separação

# Criando duas colunas para os gráficos de barras
col1, col2 = st.columns(2)

# Gráfico de barras para o total de cada tipo de status
status_totals = df.groupby('Status')['Qtd'].sum().reset_index()
status_totals = status_totals.sort_values(by='Qtd', ascending=False)  # Ordena em ordem decrescente

# Mapeando cores conforme as categorias
color_map = {
    'On Time': '#011F4B',
    'On Way': '#B3CDE0',
    'Early': '#B3CDE0',
    'Delay de SVC': '#005B96',
    'Delay de Origem': '#005B96'  # Azul para Origem
}

fig_status = px.bar(status_totals, x='Status', y='Qtd', title="Total por Tipo de Status", color='Status',
                    color_discrete_map=color_map)
fig_status.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
fig_status.update_traces(texttemplate='%{y}', textposition='outside')
col1.plotly_chart(fig_status, use_container_width=True)

# Gráfico de barras para o total de cada tipo de endereço
address_totals = df.groupby('Tipo de Endereço')['Qtd'].sum().reset_index()
address_totals = address_totals.sort_values(by='Qtd', ascending=False)  # Ordena em ordem decrescente
fig_address = px.bar(address_totals, x='Qtd', y='Tipo de Endereço', title="Total por Tipo de Endereço", orientation='h',
                     color='Tipo de Endereço', color_discrete_sequence=['#F8E45E'])  # Amarelo para todas as barras
fig_address.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
fig_address.update_traces(texttemplate='%{x}', textposition='outside')
col2.plotly_chart(fig_address, use_container_width=True)
























