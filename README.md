# Dashboard

Este código é um aplicativo Dash que cria um painel de operações bancárias. 
Ele carrega os dados de um arquivo CSV e os armazena em um dataframe do pandas. 
Ele cria uma lista única de anos, bancos e trimestres para as opções de filtro. 
A estrutura do painel é criada usando o dash e inclui três seleções dropdown para selecionar o ano, trimestre 
e banco desejado, e um gráfico para exibir os resultados das operações. O gráfico é atualizado dinamicamente
com base nas opções de filtro selecionadas, usando o callback.
