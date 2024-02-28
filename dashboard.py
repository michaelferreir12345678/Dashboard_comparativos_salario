import streamlit as st
import pandas as pd
import plotly.express as px

# Função para carregar os dados do Excel
def carregar_dados():
    return pd.read_excel("salary_data.xlsx", sheet_name="salary_data")

# Função para calcular a média salarial de cada cargo
def calcular_media_salarial(df):
    return df.groupby('cargo')['salario_atual'].mean()

# Função para calcular o impacto do aumento salarial
def calcular_impacto(df, novo_salario):
    df['salario_atualizado'] = df['salario_atual'] + (novo_salario / 100) * df['salario_atual'].mean()
    return df

# Função para criar gráfico comparando média salarial atual com o novo salário
def plotar_grafico(df, novo_salario):
    media_salario_atual = df['salario_atual'].mean()
    dados = {'Tipo': ['Média Salário Atual', 'Novo Salário'],
             'Valor': [media_salario_atual, novo_salario]}
    df_grafico = pd.DataFrame(data=dados)
    fig = px.bar(df_grafico, x='Tipo', y='Valor', title='Comparação de Média Salarial Atual com Novo Salário')
    return fig

# Função para criar e exibir a tabela de salários por classe e referência
def exibir_tabela_salarios(TC, TR, num_classes, num_referencias, salario_base):
    # Criando um DataFrame para armazenar os resultados
    tabela = pd.DataFrame(index=range(1, num_referencias + 1), columns=range(1, num_classes + 1))

    # Preenchendo a tabela com os valores de salário
    for j in range(1, num_classes + 1):
        for i in range(1, num_referencias + 1):
            if i == 1 and j == 1:
                tabela.loc[i, j] = salario_base
            elif i == 1:
                tabela.loc[i, j] = tabela.loc[num_referencias, j - 1] * TC
            else:
                tabela.loc[i, j] = tabela.loc[i - 1, j] * TR

    # Renomeando índices e colunas
    tabela.index.name = 'Referência'
    tabela.columns.name = 'Classe'

    # Exibindo a tabela
    st.subheader('Tabela de Salários por Classe e Referência')
    st.write(tabela)

    return tabela

def main():
    
    st.set_page_config(page_icon="logo.png", page_title="Prefeitura de fortaleza")
    st.title('Comparação de Média Salarial Atual com Novo Salário')

    # Carregar dados
    df = carregar_dados()

    # Alterando a cor do painel lateral
    st.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            background-color: #fac70d;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Adicionando imagem centralizada acima do título da sidebar
    st.sidebar.image('logo.png', width=30, use_column_width=True )

    # Exibir filtro de cargo no painel lateral
    cargo_selecionado = st.sidebar.selectbox('Selecione um cargo:', df['cargo'].unique())

    # Calcular média salarial de cada cargo
    media_salarial_cargos = calcular_media_salarial(df)

    # Exibir média salarial de cada cargo
    st.sidebar.subheader('Média Salarial de Cada Cargo')
    st.sidebar.write(media_salarial_cargos)

    # Parâmetros
    TC = st.sidebar.number_input('Taxa de Classe:', value=1.05)
    TR = st.sidebar.number_input('Taxa de Referência:', value=1.02)
    num_classes = st.sidebar.number_input('Número de Classes:', value=5, min_value=1)
    num_referencias = st.sidebar.number_input('Número de Referências:', value=6, min_value=1)
    salario_base = st.sidebar.number_input('Salário Base:', value=1160.66, min_value=0.0)

    # Exibir e atualizar a tabela de salários por classe e referência
    tabela_salarios = exibir_tabela_salarios(TC, TR, num_classes, num_referencias, salario_base)

    # Novo salário
    novo_salario = st.sidebar.number_input('Digite o novo valor do salário:', min_value=0.0)

    # Calcular impacto
    if st.sidebar.button('Calcular Impacto'):
        df_atualizado = calcular_impacto(df, novo_salario)

        # Exibir gráfico
        st.subheader('Impacto da variação')
        fig = plotar_grafico(df_atualizado, novo_salario)
        st.plotly_chart(fig)

if __name__ == '__main__':
    main()
