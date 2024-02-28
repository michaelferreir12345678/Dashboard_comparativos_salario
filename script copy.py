from powerbiclient import Report, models
import pandas as pd


# Definindo os parâmetros
TC = 1.05  # Taxa de Classe
TR = 1.02  # Taxa de Referência
num_classes = 5
num_referencias = 6
salario_base = 1160.66  # Salário base inicial da Classe 1 e Referência 1

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
    # tabela.loc[num_referencias, j] *= TR

# Renomeando índices e colunas
tabela.index.name = 'Referência'
tabela.columns.name = 'Classe'

# Exibindo a tabela
print(tabela)

def calcular_salario(classe, referencia, salario_base, TC, TR):
    salario = salario_base * (TC ** (classe - 1)) * (TR ** (referencia - 1))
    return salario

def powerbi_connect_and_run():
    # Define o caminho do relatório do Power BI
    report = Report("Dashboard_Projetos.pbix")

    # Define o parâmetro e seu valor a ser passado para o script Python
    parametro_powerbi = models.Parameter(name='tc2', data_type=models.ParameterDataType.String, value='valor')

    # Executa o script Python e passa o parâmetro
    result = report.run_python_script('C:\sepog_powerBI\script copy.py', parametro_powerbi)

    # Printa o resultado retornado pelo script Python
    print(result)

# Chama a função principal
powerbi_connect_and_run()

# Exemplo de uso:
classe = 3
referencia = 3
salario_base = 1160.66
TC = 1.05
TR = 1.02

salario = calcular_salario(classe, referencia, salario_base, TC, TR)
print("Salário para a classe {} e referência {}: {:.6f}".format(classe, referencia, salario))
