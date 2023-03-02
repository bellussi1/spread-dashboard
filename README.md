# Dashboard de Análise de Dados Bancários
Este é um projeto em Python que utiliza o framework Dash e a biblioteca Pandas para criar um dashboard interativo que permite a seleção dinâmica de bancos, anos e trimestres para analisar dados bancários específicos.

O dashboard possui quatro gráficos: spread, número de operações, resultado de operações e participação em porcentagem do Banco do Brasil no mercado total. Os gráficos são atualizados automaticamente de acordo com as seleções feitas pelos usuários.

## Como usar
Para executar o dashboard, é necessário ter o Python instalado e as bibliotecas Dash e Pandas. Após a instalação das dependências, execute o arquivo app.py no terminal. Isso iniciará o servidor local que hospeda o dashboard.

🔗[Live Demo](https://raw.githack.com/bellussi1/spread-dashboard/master/app.py)

No dashboard, selecione o banco, o ano e o trimestre que deseja analisar. Os gráficos serão atualizados automaticamente com os dados selecionados.

## Arquivos do repositório
- app.py: arquivo principal que executa o servidor local e hospeda o dashboard
- data/: pasta que contém os dados bancários utilizados no dashboard
- assets/: pasta que contém os arquivos de estilo CSS  para o dashboard
- README.md: arquivo que contém informações sobre o projeto e como usá-lo

## Contribuindo
Se você deseja contribuir para este projeto, sinta-se à vontade para enviar um pull request com suas alterações. Certifique-se de testar suas alterações antes de enviá-las e de documentar quaisquer novos recursos ou alterações em sua solicitação de pull.

Fonte dos dados utilizados: https://www3.bcb.gov.br/ifdata/
