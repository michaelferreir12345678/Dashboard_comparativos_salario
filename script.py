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
