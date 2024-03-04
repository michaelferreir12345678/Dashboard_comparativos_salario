import streamlit as st
import pandas as pd
import locale


st.set_page_config(layout="wide")

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Função para carregar os dados do Excel
@st.cache_data
def carregar_dados():
    return pd.read_excel("planilha_impacto_salarial.xlsx", sheet_name="amc")

# Função para substituir o ponto pela vírgula nos valores do DataFrame
@st.cache_data
def substituir_ponto_por_virgula(df):
    return df.applymap(lambda x: str(x).replace('.', ','))

# Função para calcular a média salarial de cada cargo
@st.cache_data
def calcular_media_salarial(df):
    return df.groupby('Cargo')['VENCIMENTO BASE'].mean()

# Função para criar e exibir a tabela de salários por classe e referência
@st.cache_data
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

@st.cache_data
def contar_pessoas(df):
    # Contar pessoas por cargo, carga horária e referência
    quantidade_pessoas = df.groupby(['Cargo', 'CH', 'Ref'])['VENCIMENTO BASE'].size().reset_index(name='Quantidade')
    
    # Calcular o consolidado do VENCIMENTO BASE
    consolidado_vencimento_base = df.groupby(['Cargo', 'CH', 'Ref'])['VENCIMENTO BASE'].sum().reset_index(name='Consolidado VENCIMENTO BASE')
    
    # Concatenar o consolidado com a tabela de quantidade de pessoas
    quantidade_pessoas = pd.merge(quantidade_pessoas, consolidado_vencimento_base, on=['Cargo', 'CH', 'Ref'])

    return quantidade_pessoas

@st.cache_data
def tabela_novo_salario(df):
    # Contar pessoas por cargo, carga horária e referência
    tabela_nome_novo_salario = df[['Nome','CH','Ref', 'VENCIMENTO BASE', 'Novo Salário']]
    return tabela_nome_novo_salario

@st.cache_data
def calcular_impacto(df):
    # Agrupar por cargo e calcular a quantidade de funcionários, a remuneração anterior e a remuneração nova
    resumo_cargos = df.groupby('Cargo').agg({'Nome': 'count', 'VENCIMENTO BASE': 'sum', 'Novo Salário': 'sum'}).reset_index()

    # Calcular o impacto
    resumo_cargos['Impacto'] = resumo_cargos['Novo Salário'] - resumo_cargos['VENCIMENTO BASE']

    # Renomear colunas
    resumo_cargos.rename(columns={'Nome': 'Quantidade', 'VENCIMENTO BASE': 'Remuneração Anterior', 'Novo Salário': 'Remuneração Nova'}, inplace=True)

    return resumo_cargos

def calcular_irpf(base_irpf):
    if base_irpf > 4664.68:
        return base_irpf * 0.275 - 869.36
    elif base_irpf>3751.05:
        return base_irpf *0.225-636.13
    elif base_irpf>2826.65:
        return base_irpf *0.15-354.8
    elif base_irpf>1903.98:
        return base_irpf*0.075-142.8
    else:
        return 0


def main():
        
    st.header(' :orange[Prefeitura de Fortaleza] ', divider='rainbow'   )
    col1 = st.columns(1)
    col2, col3 = st.columns(2)    
    
    # Carregar dados
    df = carregar_dados()

    # Adicionando imagem centralizada acima do título da sidebar
    st.sidebar.image('logo.jpg', width=150, use_column_width=True)

    # Exibir filtro de cargo no painel lateral
    cargo_selecionado = st.sidebar.selectbox('Selecione um cargo:', df['Cargo'].unique())
    
    # Opção para escolher qual tabela será exibida
    tabela_selecionada = st.sidebar.selectbox('Selecione a tabela:', ['Tabela B - 180h', 'Tabela C - 180h', 'Tabela D - 180h','Tabela B - 240h', 'Tabela C - 240h', 'Tabela D - 240h'])

    st.sidebar.header('Configurações')
    indice_tabela = st.sidebar.number_input('Enquadramento:', min_value=0, value=0)


    # Calcular média salarial de cada cargo
    media_salarial_cargos = calcular_media_salarial(df)

    # Parâmetros Tabela 1
    st.sidebar.subheader('Tabela Personalizável')
    TC1 = st.sidebar.number_input('Taxa de Classe:', value=1.05)
    TR1 = st.sidebar.number_input('Taxa de Referência:', value=1.02)
    num_classes1 = st.sidebar.number_input('Número de Classes:', value=5, min_value=1)
    num_referencias1 = st.sidebar.number_input('Número de Referências:', value=6, min_value=1)
    salario_base1 = st.sidebar.number_input('Salário Base:', value=1160.66, min_value=0.0)

    # Parâmetros Tabela B - 180h
    num_classes_b_180 = 5
    num_referencias_b_180 = 6
    salario_base_b_180 = 886.29

    # Parâmetros Tabela C - 180h
    num_classes_c_180 = 5
    num_referencias_c_180 = 6
    salario_base_c_180 = 1160.66

    # Parâmetros Tabela D - 180h
    num_classes_d_180 = 5
    num_referencias_d_180 = 6
    salario_base_d_180 = 1582.67
    
    # Parâmetros Tabela B - 240h
    num_classes_b_240 = 5
    num_referencias_b_240 = 6
    salario_base_b_240 = 1181.71

    # Parâmetros Tabela C - 240h
    num_classes_c_240 = 5
    num_referencias_c_240 = 6
    salario_base_c_240 = 1547.55

    # Parâmetros Tabela D - 240h
    num_classes_d_240 = 5
    num_referencias_d_240 = 6
    salario_base_d_240 = 2110.22

    # Exibir e atualizar a tabela de salários por classe e referência (Tabela 1)
    tabela_salarios1, valores1 = exibir_tabela_salarios(TC1, TR1, num_classes1, num_referencias1, salario_base1, 'Tabela personalizável')
    col2.write("Tabela Personalizável")
    tabela_salarios1 = col2.dataframe(tabela_salarios1, use_container_width=True)
    
    def calcular_novo_salario(df, valores_tabela1, pular_indice=0):
        novo_salario = []   
        for indice_ref in df['Ref']:
            indice_alvo = indice_ref + pular_indice
            for chave, valor in valores_tabela1.items():
                if indice_alvo == valor[1]:
                    novo_salario.append(valor[0])
                    break  # Encerrar o loop interno após encontrar a correspondência
            else:
                novo_salario.append(None)  # Adicionar None se não houver correspondência encontrada
        return novo_salario
                    
    
    # Calcular novo salário usando a Tabela 1
    df['Novo Salário'] = calcular_novo_salario(df, valores1, pular_indice=indice_tabela)

    # Exibir e atualizar a tabela de salários por classe e referência (Tabela B)
    if tabela_selecionada == 'Tabela B - 180h':
        tabela_salarios_b_240, valores_b_240 = exibir_tabela_salarios(1.05, 1.02, num_classes_b_180, num_referencias_b_180, salario_base_b_180, 'Tabela B - 180h')
        col3.write("Tabela B - 180h")
        col3.dataframe(tabela_salarios_b_240.round(2), use_container_width=True)

    # Exibir e atualizar a tabela de salários por classe e referência (Tabela C)
    if tabela_selecionada == 'Tabela C - 180h':
        tabela_salarios_c_240, valores_c_240 = exibir_tabela_salarios(1.05, 1.02, num_classes_c_180, num_referencias_c_180, salario_base_c_180, 'Tabela C - 180h')
        col3.write("Tabela C - 180h")
        col3.dataframe(tabela_salarios_c_240.round(2), use_container_width=True)
        
    # Exibir e atualizar a tabela de salários por classe e referência (Tabela D)
    if tabela_selecionada == 'Tabela D - 180h':
        tabela_salarios_d_240, valores_d_240 = exibir_tabela_salarios(1.05, 1.02, num_classes_d_180, num_referencias_d_180, salario_base_d_180, 'Tabela D - 180h')
        col3.write("Tabela D - 180h")
        col3.dataframe(tabela_salarios_d_240.round(2), use_container_width=True)
        
        # Exibir e atualizar a tabela de salários por classe e referência (Tabela B)
    if tabela_selecionada == 'Tabela B - 240h':
        tabela_salarios_b_240, valores_b_240 = exibir_tabela_salarios(1.05, 1.02, num_classes_b_240, num_referencias_b_240, salario_base_b_240, 'Tabela B - 180h')
        col3.write("Tabela B - 240h")
        col3.dataframe(tabela_salarios_b_240.round(2), use_container_width=True)

    # Exibir e atualizar a tabela de salários por classe e referência (Tabela C)
    if tabela_selecionada == 'Tabela C - 240h':
        tabela_salarios_c_240, valores_c_240 = exibir_tabela_salarios(1.05, 1.02, num_classes_c_240, num_referencias_c_240, salario_base_c_240, 'Tabela C - 180h')
        col3.write("Tabela C - 240h")
        col3.dataframe(tabela_salarios_c_240.round(2), use_container_width=True)

    # Exibir e atualizar a tabela de salários por classe e referência (Tabela D)
    if tabela_selecionada == 'Tabela D - 240h':
        tabela_salarios_d_240, valores_d_240 = exibir_tabela_salarios(1.05, 1.02, num_classes_d_240, num_referencias_d_240, salario_base_d_240, 'Tabela D - 180h')
        col3.write("Tabela D - 240h")
        col3.dataframe(tabela_salarios_d_240.round(2), use_container_width=True)

    # Quantidade de pessoas por cargo, carga horária e referência
    quantidade_pessoas = contar_pessoas(df)
    
    # Adicionando o totalizador geral
    total_quantidade = quantidade_pessoas['Quantidade'].sum()
    total_cons_venc_base = quantidade_pessoas['Consolidado VENCIMENTO BASE'].sum()
    total_geral = pd.DataFrame({'Cargo': ['Total Geral'], 'Quantidade': [total_quantidade], 'Consolidado VENCIMENTO BASE': [total_cons_venc_base]})
    
    quantidade_pessoas = pd.concat([quantidade_pessoas, total_geral], ignore_index=True)
    
    tabela_com_novo_salario = tabela_novo_salario(df)
    
    # Calcular totais para a tabela do novo salário
    total_vencimento_base = tabela_com_novo_salario['VENCIMENTO BASE'].sum()
    total_novo_salario = tabela_com_novo_salario['Novo Salário'].sum()
    subtracao = total_novo_salario - total_vencimento_base
    total_impacto = total_novo_salario - total_vencimento_base
    
    # cálculo dos encargos
    provisao_ferias_rem_anterior = (total_vencimento_base/12)/3
    provisao_ferias_nova = (total_novo_salario/12)/3
    provisao_ferias_impacto = (total_impacto/12)/3
    provisao_decimo_rem_anterior = (total_vencimento_base/12)
    provisao_decimo_nova = (total_novo_salario/12)
    provisao_decimo_impacto = (total_impacto/12)
    provisao_ipm_rem_anterior = (total_vencimento_base + provisao_ferias_rem_anterior + provisao_decimo_rem_anterior) * 0.04
    provisao_ipm_nova = ((total_novo_salario + provisao_ferias_nova + provisao_decimo_nova) * 0.04)
    provisao_ipm_impacto = (total_impacto + provisao_ferias_nova + provisao_decimo_impacto) * 0.04
    ipm_previfor_anterior = df['0801-IPM PREVFOR'].sum() 
    

    # Adicionar linha com totais à tabela do novo salário
    tabela_com_novo_salario.loc['Total', ['VENCIMENTO BASE', 'Novo Salário']] = [total_vencimento_base, total_novo_salario]

    # Nova tabela com o novo salário calculado
    st.write("Nova tabela com o novo salário calculado usando a Tabela 1:")
    st.dataframe(tabela_com_novo_salario.round(2))

    # Calcular o resumo dos cargos
    resumo_cargos = calcular_impacto(df)

    # Totalizadores da tabela de impacto
    resumo_cargos.loc['Total', ['Cargo', 'Quantidade', 'Remuneração Anterior', 'Remuneração Nova', 'Impacto']] = ['',total_quantidade, total_vencimento_base, total_novo_salario, total_impacto]
    
    # Adicionar linha com subtítulo "Encargos" logo abaixo dos totalizadores
    resumo_cargos.loc[''] = ['Encargos', '', '', '', '']
    resumo_cargos.loc[len(resumo_cargos)] = ['Provisão de férias', '', provisao_ferias_rem_anterior, provisao_ferias_nova, provisao_ferias_impacto]
    resumo_cargos.loc[len(resumo_cargos)] = ['Provisão de 13º Salário', '', provisao_decimo_rem_anterior, provisao_decimo_nova, provisao_decimo_impacto]
    resumo_cargos.loc[len(resumo_cargos)] = ['Fortaleza Saúde- IPM (4%)', '', provisao_ipm_rem_anterior,provisao_ipm_nova , provisao_ipm_impacto]
    # resumo_cargos.loc['Total'] = []
    
    # Adicionando novas colunas
    df['novo_0085-ITA'] = (df['REF-ITA'] * df['Novo Salário']) / 100
    df['novo_0107-ANUENIO'] = (df['REF-ANUENIO'] * df['Novo Salário']) / 100
    df['nova_105-INSALUBRIDAD'] = (df['REF-INSALUBRIDAD'] * df['Novo Salário']) / 100
    df['nova_0118-GR.PRODUT_'] = (df['REF-GR.PRODUT'] * df['Novo Salário']) / 100
    df['nova_0096-GAT'] = (df['REF-GAT'] * df['Novo Salário']) / 100
    df['nova_0097-GEEF-AMC'] = (df['REF-GEEF-AMC'] * df['Novo Salário']) / 100
    df['nova_0159-GR.R.VIDA'] = (df['REF-GR.R.VIDA'] * df['Novo Salário']) / 100
    df['nova_0318-GE AMC'] = (df['REF-GE AMC'] * df['Novo Salário']) / 100
    df['novo_0817-B HR INC'] = df['0223-VP'] + df['0248-VPNI HEI'] + df['0001-G.F.INC-DNI1'] + df['0004-G.R.INC.DAS1'] + df['0005-G.R.INC.DAS2'] + df['0006-G.R.INC.DAS3'] + df['0007-G.R.INC.DNS1'] + df['0008-G.R.INC.DNS2'] + df['0009-G.R.INC.DNS3'] + df['0026-GR INC AT1'] + df['0027-GR INC AT2'] + df['Novo Salário'] + df['novo_0085-ITA'] + df['novo_0107-ANUENIO'] + df['nova_105-INSALUBRIDAD'] + df['nova_0118-GR.PRODUT_'] + df['nova_0096-GAT'] + df['nova_0097-GEEF-AMC'] + df['nova_0159-GR.R.VIDA'] + df['nova_0318-GE AMC']
    df['nova_0133-HR.EXTR.INCO'] = df['novo_0817-B HR INC'] / df['CH'] * 1.25 * df['REF-HR.EXTR.INCO']
    df['novo_0996-TOT.PROVENTO'] = df['Novo Salário'] + df['novo_0085-ITA'] + df['novo_0107-ANUENIO'] + df['nova_105-INSALUBRIDAD'] + df['nova_0118-GR.PRODUT_'] + df['nova_0096-GAT'] + df['nova_0097-GEEF-AMC'] + df['nova_0159-GR.R.VIDA'] + df['nova_0318-GE AMC'] + df['nova_0133-HR.EXTR.INCO'] + df['0223-VP'] + df['0248-VPNI HEI'] + df['0001-G.F.INC-DNI1'] + df['0004-G.R.INC.DAS1'] + df['0005-G.R.INC.DAS2'] + df['0006-G.R.INC.DAS3'] + df['0007-G.R.INC.DNS1'] + df['0008-G.R.INC.DNS2'] + df['0009-G.R.INC.DNS3'] + df['0026-GR INC AT1'] + df['0027-GR INC AT2'] + df['0308-DIF.AJ.PCCS'] + df['0320-GAJ 9903/12'] + df['0170-DIR.NIV.SUPE'] + df['0174-VRB.ESP.REP'] + df['0180-DIR.ASS.SUPE'] + df['0190-DIR.NIV.INT.'] + df['058-DIR GER 01'] + df['0326-GTRTC                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           '] + df['0206-AB.PERMANENC']
    df['nova_0872-B HR NOTURNA'] = df['nova_0133-HR.EXTR.INCO'] + df['0223-VP'] + df['0223-VP'] + df['0248-VPNI HEI'] + df['0001-G.F.INC-DNI1'] + df['0004-G.R.INC.DAS1'] + df['0005-G.R.INC.DAS2'] + df['0006-G.R.INC.DAS3'] + df['0007-G.R.INC.DNS1'] + df['0008-G.R.INC.DNS2'] + df['0009-G.R.INC.DNS3'] + df['0026-GR INC AT1'] + df['0027-GR INC AT2'] + df['Novo Salário'] + df['novo_0085-ITA'] + df['novo_0107-ANUENIO'] + df['nova_105-INSALUBRIDAD'] + df['nova_0118-GR.PRODUT_'] + df['nova_0096-GAT'] + df['nova_0097-GEEF-AMC'] + df['nova_0159-GR.R.VIDA'] + df['nova_0318-GE AMC']
    df['nova_0099-HR NOTURNAS'] = df['nova_0872-B HR NOTURNA'] / df['CH'] * 0.2 * df['REF-HR NOTURNAS']
    df['nova_0183-GR SER EXTRA'] = df['nova_0872-B HR NOTURNA'] / df['CH'] * 1.5 * df['REF-GR SER EXTRA']
    df['nova_0383-HE NOTURNA'] = df['nova_0872-B HR NOTURNA'] / df['CH'] * 1.5 * 1.2 * df['REF-HE NOTURNA                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ']
    df['nova_0801-IPM PREVFOR'] = df['Novo Salário'] + df['novo_0085-ITA'] + df['novo_0107-ANUENIO'] + df['nova_105-INSALUBRIDAD'] + df['nova_0118-GR.PRODUT_'] + df['nova_0096-GAT'] + df['nova_0097-GEEF-AMC'] + df['nova_0318-GE AMC'] + df['nova_0133-HR.EXTR.INCO'] + df['0223-VP'] + df['0248-VPNI HEI'] + df['0001-G.F.INC-DNI1'] + df['0004-G.R.INC.DAS1'] + df['0005-G.R.INC.DAS2'] + df['0006-G.R.INC.DAS3'] + df['0007-G.R.INC.DNS1'] + df['0008-G.R.INC.DNS2'] + df['0009-G.R.INC.DNS3'] + df['0026-GR INC AT1'] + df['0027-GR INC AT2'] + df['0308-DIF.AJ.PCCS'] 
    df['nova_IPM PREVFOR-PATRONAL'] = df['nova_0801-IPM PREVFOR'] * 0.28
    df['nova_IPM PREVFOR-SERVIDOR'] = df['nova_0801-IPM PREVFOR'] * 0.14
    df['nova_base_IRPF'] = df['novo_0996-TOT.PROVENTO'] -  df['nova_IPM PREVFOR-SERVIDOR']            
    df['nova_IRPF'] = df['nova_base_IRPF'].apply(calcular_irpf)
    
    nova_ipm_previfor = df['nova_IPM PREVFOR-PATRONAL'].sum()    
    resumo_cargos.loc[len(resumo_cargos)] = ['IPM – PREVIFOR-FIN (28%)', '', ipm_previfor_anterior, nova_ipm_previfor, provisao_ferias_impacto]
    
    impacto_mensal_ant = total_vencimento_base + provisao_ferias_rem_anterior + provisao_decimo_rem_anterior + provisao_ipm_rem_anterior + ipm_previfor_anterior
    impacto_mensal_novo = total_novo_salario+provisao_ferias_nova + provisao_decimo_nova + provisao_ipm_nova + nova_ipm_previfor
    impacto_mensal_impacto = total_impacto + provisao_ferias_impacto + provisao_decimo_impacto + provisao_ipm_impacto + provisao_ferias_impacto
    resumo_cargos.loc[len(resumo_cargos)] = ['IMPACTO MENSAL', '', impacto_mensal_ant, impacto_mensal_novo, impacto_mensal_impacto]
    resumo_cargos.loc[len(resumo_cargos)] = ['IMPACTO ANUAL', '', impacto_mensal_ant*12, impacto_mensal_novo*12, impacto_mensal_impacto*12]
    
    
    # Exibir a tabela de resumo de cargos
    st.header("Impacto da Reestruturação do PCCS da Gestão do Trânsito:")
    st.dataframe(resumo_cargos.applymap(lambda x: locale.currency(x, grouping=True).format(x) if isinstance(x, (int, float)) else x))
        
    # Calcular imposto de renda para a Remuneração Anterior e Nova
    imposto_renda_anterior = df['IRPF'].sum()
    imposto_renda_novo = df['nova_IRPF'].sum()
    impacto_imposto_renda = imposto_renda_novo - imposto_renda_anterior

    # Calcular IPM-PREVIFOR (Patronal) para a Remuneração Anterior e Nova
    ipm_previfor_patronal_anterior = df['IPM PREVFOR-PATRONAL'].sum()
    ipm_previfor_patronal_novo = df['nova_IPM PREVFOR-PATRONAL'].sum()
    impacto_ipm_previfor_patronal = ipm_previfor_patronal_novo - ipm_previfor_patronal_anterior

    # Calcular IPM PREVFOR-SERVIDOR para a Remuneração Anterior e Nova
    ipm_previfor_servidor_anterior = df['IPM PREVFOR-SERVIDOR'].sum()
    ipm_previfor_servidor_novo = df['nova_IPM PREVFOR-SERVIDOR'].sum()
    impacto_ipm_previfor_servidor = ipm_previfor_servidor_novo - ipm_previfor_servidor_anterior

    # Calcular valores totais
    valor_mensal_anterior = imposto_renda_anterior + ipm_previfor_patronal_anterior + ipm_previfor_servidor_anterior
    valor_mensal_novo = imposto_renda_novo + ipm_previfor_patronal_novo + ipm_previfor_servidor_novo
    impacto_mensal = valor_mensal_novo - valor_mensal_anterior

    valor_anual_anterior = valor_mensal_anterior * 12
    valor_anual_novo = valor_mensal_novo * 12
    impacto_anual = valor_anual_novo - valor_anual_anterior

    # Criar DataFrame com os resultados
    dados = {
        'Item': ['IMPOSTO DE RENDA', 'IPM-PREVIFOR (Patronal)', 'IPM-PREVIFOR (Servidor)', 'VALOR MENSAL', 'VALOR ANUAL'],
        'Remuneração Anterior': [imposto_renda_anterior, ipm_previfor_patronal_anterior, ipm_previfor_servidor_anterior, valor_mensal_anterior, valor_anual_anterior],
        'Remuneração Nova': [imposto_renda_novo, ipm_previfor_patronal_novo, ipm_previfor_servidor_novo, valor_mensal_novo, valor_anual_novo],
        'Impacto': [impacto_imposto_renda, impacto_ipm_previfor_patronal, impacto_ipm_previfor_servidor, impacto_mensal, impacto_anual]
    }

    tabela = pd.DataFrame(dados)

    # Formatando valores para exibição
    tabela['Remuneração Anterior'] = tabela['Remuneração Anterior'].apply(lambda x: locale.currency(x, grouping=True))
    tabela['Remuneração Nova'] = tabela['Remuneração Nova'].apply(lambda x: locale.currency(x, grouping=True))
    tabela['Impacto'] = tabela['Impacto'].apply(lambda x: locale.currency(x, grouping=True))
    
    styled_table = tabela.style.apply(lambda s: ['background-color: #dcdcdc; font-weight: bold' if s.name == 3 or s.name == 4 else '' for i in s], axis=1)

    
    st.header("Suavizações:")
    st.dataframe(styled_table)
    
    
    # Criar DataFrame com os totais
    dados_totais = {
        'Item': ['Impacto Líquido Mensal', 'Impacto Líquido Anual'],
        'Remuneração Anterior': [valor_mensal_anterior + impacto_mensal_ant, valor_anual_anterior + (impacto_mensal_ant*12)   ],
        'Remuneração Nova': [valor_mensal_novo + impacto_mensal_novo, valor_anual_novo + (impacto_mensal_novo*12) ],
        'Impacto': [impacto_mensal + impacto_mensal_impacto,  impacto_anual + (impacto_mensal_impacto*12)]
    }
    
    tabela_dados_totais = pd.DataFrame(dados_totais)

    # Formatando valores para exibição
    tabela_dados_totais['Remuneração Anterior'] = tabela_dados_totais['Remuneração Anterior'].apply(lambda x: locale.currency(x, grouping=True))
    tabela_dados_totais['Remuneração Nova'] = tabela_dados_totais['Remuneração Nova'].apply(lambda x: locale.currency(x, grouping=True))
    tabela_dados_totais['Impacto'] = tabela_dados_totais['Impacto'].apply(lambda x: locale.currency(x, grouping=True))
    
    st.header("Totais:")
    st.dataframe(tabela_dados_totais)
    
if __name__ == '__main__':
    main()