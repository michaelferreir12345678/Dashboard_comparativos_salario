import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Função para carregar os dados do Excel
def carregar_dados():
    return pd.read_excel("planilha_impacto_salarial.xlsx", sheet_name="amc")

# Função para substituir o ponto pela vírgula nos valores do DataFrame
def substituir_ponto_por_virgula(df):
    return df.applymap(lambda x: str(x).replace('.', ','))

# Função para calcular a média salarial de cada cargo
def calcular_media_salarial(df):
    return df.groupby('Cargo')['VENCIMENTO BASE'].mean()

# Função para criar e exibir a tabela de salários por classe e referência
def exibir_tabela_salarios(TC, TR, num_classes, num_referencias, salario_base, nome_tabela):
    # Criando um DataFrame para armazenar os resultados
    tabela = pd.DataFrame(index=range(1, num_referencias + 1), columns=range(1, num_classes + 1))
    valores = {}  # Dicionário para armazenar os valores
    
    # Preenchendo a tabela com os valores de salário
    for j in range(1, num_classes + 1):
        for i in range(1, num_referencias + 1):
            if i == 1 and j == 1:
                valor = salario_base
            elif i == 1:
                valor = float(tabela.loc[num_referencias, j - 1]) * TC
            else:
                valor = float(tabela.loc[i - 1, j]) * TR
            
            # Armazenando o valor no dicionário
            valores[(i, j)] = valor, i + (j - 1) * num_referencias
            tabela.loc[i, j] = f"{valor:.2f}"  # Atribuindo o índice da célula com duas casas decimais
                        
    # Renomeando índices e colunas
    tabela.index.name = 'Referência'
    tabela.columns.name = 'Classe'
    
    return tabela, valores

def contar_pessoas(df):
    # Contar pessoas por cargo, carga horária e referência
    quantidade_pessoas = df.groupby(['Cargo', 'CH', 'Ref'])['VENCIMENTO BASE'].size().reset_index(name='Quantidade')
    
    # Calcular o consolidado do VENCIMENTO BASE
    consolidado_vencimento_base = df.groupby(['Cargo', 'CH', 'Ref'])['VENCIMENTO BASE'].sum().reset_index(name='Consolidado VENCIMENTO BASE')
    
    # Concatenar o consolidado com a tabela de quantidade de pessoas
    quantidade_pessoas = pd.merge(quantidade_pessoas, consolidado_vencimento_base, on=['Cargo', 'CH', 'Ref'])
    
    return quantidade_pessoas

def main():
    st.header(' :orange[Prefeitura de Fortaleza] ', divider='rainbow'   )
    col1 = st.columns(1)
    col2, col3 = st.columns(2)    
    
    # Carregar dados
    df = carregar_dados()

    # Adicionando imagem centralizada acima do título da sidebar
    st.sidebar.image('logo.png', width=150, use_column_width=True)

    # Exibir filtro de cargo no painel lateral
    cargo_selecionado = st.sidebar.selectbox('Selecione um cargo:', df['Cargo'].unique())
    
    # Opção para escolher qual tabela será exibida
    tabela_selecionada = st.sidebar.selectbox('Selecione a tabela:', ['Tabela B - 180h', 'Tabela C - 180h', 'Tabela D - 180h'])

    # Calcular média salarial de cada cargo
    media_salarial_cargos = calcular_media_salarial(df)

    # Parâmetros Tabela 1
    st.sidebar.subheader('Tabela Personalizável')
    TC1 = st.sidebar.number_input('Taxa de Classe:', value=1.05)
    TR1 = st.sidebar.number_input('Taxa de Referência:', value=1.02)
    num_classes1 = st.sidebar.number_input('Número de Classes:', value=5, min_value=1)
    num_referencias1 = st.sidebar.number_input('Número de Referências:', value=6, min_value=1)
    salario_base1 = st.sidebar.number_input('Salário Base:', value=1160.66, min_value=0.0)

    # Parâmetros Tabela B
    num_classes_b = 5
    num_referencias_b = 6
    salario_base_b = 886.29

    # Parâmetros Tabela C
    num_classes_c = 5
    num_referencias_c = 6
    salario_base_c = 1160.66

    # Parâmetros Tabela D
    num_classes_d = 5
    num_referencias_d = 6
    salario_base_d = 1582.67

    # Exibir e atualizar a tabela de salários por classe e referência (Tabela 1)
    tabela_salarios1, valores1 = exibir_tabela_salarios(TC1, TR1, num_classes1, num_referencias1, salario_base1, 'Tabela personalizável')
    col2.write("Tabela Personalizável")
    tabela_salarios1 = col2.dataframe(tabela_salarios1, use_container_width=True)
    
    indice_desejado = 6 # Índice desejado

    # Verificar se o índice está presente no dicionário
    # if (indice_desejado, 1) in valores1:
    #     valor_desejado = valores1[(indice_desejado, 1)][0]
    #     return valor_desejado
    
    # Exibir e atualizar a tabela de salários por classe e referência (Tabela B)
    if tabela_selecionada == 'Tabela B - 180h':
        tabela_salarios_b, valores_b = exibir_tabela_salarios(1.05, 1.02, num_classes_b, num_referencias_b, salario_base_b, 'Tabela B - 180h')
        col3.write("Tabela B - 180h")
        col3.dataframe(tabela_salarios_b, use_container_width=True)

    # Exibir e atualizar a tabela de salários por classe e referência (Tabela C)
    if tabela_selecionada == 'Tabela C - 180h':
        tabela_salarios_c, valores_c = exibir_tabela_salarios(1.05, 1.02, num_classes_c, num_referencias_c, salario_base_c, 'Tabela C - 180h')
        col3.write("Tabela C - 180h")
        col3.dataframe(tabela_salarios_c, use_container_width=True)

    # Exibir e atualizar a tabela de salários por classe e referência (Tabela D)
    if tabela_selecionada == 'Tabela D - 180h':
        tabela_salarios_d, valores_d = exibir_tabela_salarios(1.05, 1.02, num_classes_d, num_referencias_d, salario_base_d, 'Tabela D - 180h')
        col3.write("Tabela D - 180h")
        col3.dataframe(tabela_salarios_d, use_container_width=True)

    # Quantidade de pessoas por cargo, carga horária e referência
    quantidade_pessoas = contar_pessoas(df)
    
    # Adicionando o totalizador geral
    total_quantidade = quantidade_pessoas['Quantidade'].sum()
    total_cons_venc_base = quantidade_pessoas['Consolidado VENCIMENTO BASE'].sum()
    total_geral = pd.DataFrame({'Cargo': ['Total Geral'], 'CH': [''], 'Ref': [''], 'Quantidade': [total_quantidade], 'Consolidado VENCIMENTO BASE': [total_cons_venc_base]})
    
    quantidade_pessoas = pd.concat([quantidade_pessoas, total_geral], ignore_index=True)
    
    quantidade_pessoas.insert(0, "Tabela", "Tabela 1")  # Adicionando a informação da tabela
    st.write("Quantidade de pessoas por cargo, carga horária e referência:")
    st.dataframe(quantidade_pessoas)

if __name__ == '__main__':
    main()
