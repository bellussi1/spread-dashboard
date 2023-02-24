# Importação das bibliotecas utilizadas
from dash import dcc, html, Input, Output, State, Dash, dash_table
from dash.exceptions import PreventUpdate
import dash
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go

bank_colors = {  # Dicionario de cores para os principais Bancos
    "BB": "#F9DD16",
    "ITAU": "#FF9641",
    "BRADESCO": "#633280",
    "SANTANDER": "#ec0000",
    "Outros": "gray",
    "MERCADO": "#06548a",
}

def read_csv(csv_file_path):
    """
    Carrega um dataFrame e faz alterações nas colunas
    """
    # Carrega o dataframe a partir do arquivo CSV
    df = pd.read_csv(csv_file_path)

    # Cria o dicionário de substituições para o trimestre
    quarter_replace = {1: "03", 2: "06", 3: "09", 4: "12"}

    # Aplica a substituição na coluna de trimestre
    df["TRIMESTRE"] = df["TRIMESTRE"].replace(quarter_replace)

    # Concatena o ano e o trimestre em uma coluna
    df["ANO-TRIMESTRE"] = df["ANO"].astype(str) + "-" + df["TRIMESTRE"]

    # Para visualização no DataTable
    df['ANO_TRIMESTRE'] = df["ANO"].astype(str) + "-" + df["TRIMESTRE"]

    # Formata os valores da coluna ANO-TRIMESTRE para o tipo Date
    df["ANO-TRIMESTRE"] = pd.to_datetime(df["ANO-TRIMESTRE"], format="%Y-%m")

    # Cria a coluna TOTAL_VOL com a soma dos valores de VOLUME_OP e VOLUME_INTERBANK
    df["TOTAL_VOL"] = df["VOLUME_OP"] + df["VOLUME_INTERBANK"]

    # Cria a coluna TOTAL_OP com a soma dos valores de RESULT_OP e DESPESA_OP
    df["TOTAL_OP"] = df["RESULT_OP"] + df["DESPESA_OP"]

    # Cria a coluna TOTAL_N com a soma dos valores de NUMERO_OP e NUMERO_INTERBANK
    df["TOTAL_N"] = df["NUMERO_OP"] + df["NUMERO_INTERBANK"]

    # Cria a coluna SPREAD com a relação entre a soma dos volumes de operações e
    # a soma dos resultados e despesas das operações, arredondado para duas casas decimais
    df["SPREAD"] = (df["VOLUME_OP"] + df["VOLUME_INTERBANK"]) / \
        (df["RESULT_OP"] + df["DESPESA_OP"]) / 100
    df["SPREAD"] = df["SPREAD"].round(decimals=2)

    return df


# Carregar o arquivo csv chamado "spread.csv" na variável df
df = read_csv("data/spread.csv")

years = df["ANO"].unique()  # Anos unicos para o filtro
banks = df["NOME_BANCO"].unique()  # Bancos unicos para o filtro
quarters = df["TRIMESTRE"].unique()  # Trimestres unicos para o filtro

app = Dash(__name__,
           title="Movimentação de Câmbio",
           update_title=None)


def data_table(df):

    # Armazena as colunas relevantes do dataframe df em uma nova variável 'table'
    table = df[['NOME_BANCO', 'ANO_TRIMESTRE', 'VOLUME_OP',
                'VOLUME_INTERBANK', 'RESULT_OP']].copy()

    return table

# Criando a visulização Table baseada no DataFrame
table = data_table(df)


def table_cols(table):
    # Cria uma lista 'cols' com dicionários, onde cada dicionário tem as chaves "name" e "id",
    # relacionando o nome de cada coluna com sua identificação
    cols = [{"name": i, "id": i} for i in table.columns]

    # Sobrescreve 'cols' com uma nova lista, agora especificando o nome que cada coluna deve ter na exibição
    cols = [{"name": ["", "Banco"], "id": "NOME_BANCO"},
            {"name": ["", "Ano"], "id": "ANO_TRIMESTRE"},
            {"name": ["(USD)", "Vol. Prim."], "id": "VOLUME_OP"},
            {"name": ["(USD)", "Vol. Inter."], "id": "VOLUME_INTERBANK"},
            {"name": ["(BRL)", "Result. Op."], "id": "RESULT_OP"}]

    return cols

# Colunas que serão usadas do Table
cols = table_cols(table)

# Definindo estilo para a tabela como um todo
table_style = {
    'font-size': '14px',  # tamanho da fonte
    'text-align': 'center',  # alinhamento centralizado dos dados na tabela
    'margin-left': 'auto',  # alinhamento centralizado horizontalmente
    'margin-right': 'auto',  # alinhamento centralizado horizontalmente
    'table-layout': 'fixed',  # layout fixo da tabela
    'font-family': 'BancoDoBrasil Textos'
}

# Definindo estilo para o cabeçalho da tabela
header_style = {
    'background-color': 'rgb(230, 230, 230)',  # cor de fundo dos cabeçalhos
    'font-weight': 'bold',  # negrito para os cabeçalhos
    'text-align': 'center',  # alinhamento à esquerda dos nomes das colunas
    'font-family': 'BancoDoBrasil Textos'
}

# Definindo estilo para as células da tabela
cell_style = {
    'text-align': 'center',  # alinhamento centralizado dos valores
    'min-width': '75px',  # tamanho mínimo das células
    'font-family': 'BancoDoBrasil Textos',
    'whiteSpace': 'normal',
}

# Criando o Layout para o Dashboard
app.layout = html.Div(
    [
        html.Div(  # Div Layout
            [
                html.Img(src="assets/uce_logo.png",
                         className="logo"),  # Logo UNI
                html.H1(
                    "Movimentação de Câmbio",  # Titulo
                    className="layout-title",
                ),
            ],
            className="layout",
        ),
        html.Div(  # Div esquerdo
            [
                html.Div(  # Div dos Dropdowns
                    [
                        html.Br(),
                        html.H2(  # Titulo
                            "Selecione o filtro desejado",
                            className="title-dropdown"
                        ),
                        html.Label("Ano",
                                   className="dropdown-labels"),
                        dcc.Dropdown(  # Filtro do Ano, retornando os 4 trimestres como padrão
                            id="year-dropdown",
                            options=[  # Valores unicos a filtrar
                                {"label": year, "value": year} for year in years
                            ],
                            value=years,  # Valores iniciais
                            multi=True,  # Permitindo selecionar mais que um valor
                            className="dropdown",
                            optionHeight=50,  # Altura das opções (Estetica)
                        ),
                        # Nome acima do dropdown
                        html.Label("Trimestre",
                                   className="dropdown-labels"),
                        dcc.Dropdown(  # Filtro do Trimestre, retornando os 4 trimestres como padrão
                            id="quarter-dropdown",
                            options=[  # Valores unicos a filtrar
                                {"label": quarter, "value": quarter}
                                for quarter in quarters
                            ],
                            value=["03", "06", "09", "12"],  # Valores iniciais
                            multi=True,  # Permitindo selecionar mais que um valor
                            className="dropdown",
                            optionHeight=50,  # Altura das opções (Estetica)
                        ),
                        html.Label(
                            "Instituição Bancária",
                            className="dropdown-labels"
                        ),  # Nome acima do dropdown
                        dcc.Dropdown(  # Filtro do Banco, retornando os 4 principais como padrão
                            id="bank-dropdown",
                            options=[  # Valores unicos a filtrar
                                {"label": bank, "value": bank} for bank in banks
                            ],
                            value=[
                                "BB",
                                "ITAU",
                                "BRADESCO",
                                "SANTANDER",
                            ],  # Valores iniciais (Principais Bancos)
                            multi=True,  # Permitindo selecionar mais que um valor
                            className="dropdown",
                            optionHeight=50,  # Altura das opções (Estetica)
                        ),
                        html.Button(
                            'Todos os Bancos',
                            id='select_all',
                            n_clicks=0,
                            className="button-dropdown"
                        ),
                    ],
                    className="dropdown-container",
                ),
                html.Div(  # Pieplot
                    [dcc.Graph(id="operations-result-pieplot",
                               className="pieplot")],
                    className="pieplot-container",
                ),
                html.Div(
                    [dash_table.DataTable(id='table',
                                          columns=cols,
                                          data=table.to_dict("records"),
                                          style_data=cell_style,
                                          style_cell={
                                              'textAlign': 'center'
                                          },
                                          style_header=header_style,
                                          style_table=table_style,
                                          sort_action="native",
                                          sort_mode="multi",
                                          sort_by=[{"column_id": "ANO_TRIMESTRE", "direction": "desc"},
                                                   {"column_id": "RESULT_OP", "direction": "desc"}],
                                          merge_duplicate_headers=True,
                                          page_size=14
                                          )],
                    className='table'
                ),
            ],
            className="left-container",
        ),
        html.Div(  # Div dos Graficos
            [
                html.Div(  # Div dos botoes
                    [
                        html.Button(
                            "Trimestral",
                            id="trimestral-button",
                            n_clicks=0,
                            className="button",
                        ),
                        html.Button(
                            "Por ano",
                            id="ano-button",
                            n_clicks=0,
                            className="button"
                        ),
                    ],
                    className="button-container",
                ),
                html.Div(  # Gráfico de Barras numero de operações
                    [
                        dcc.Graph(id="bar-lineplot",
                                  className="bar-lineplot"),
                    ],
                    className="bar-lineplot-container",
                ),
                html.Div(  # Gráfico de Linha Spread
                    [dcc.Graph(id="spread-lineplot",
                               className="spreadlineplot")],
                    className="spreadlineplot-container",
                ),
                html.Div(  # Grafico de Linha Resultados
                    [dcc.Graph(id="operations-result-lineplot",
                               className="lineplot")],
                    className="lineplot-container",
                ),
            ],
            className="graph-container",
        ),
    ],
    className="main-container",
)


def filter_data(selected_year, selected_quarter, selected_bank, df=df):
    """Função de filtrar quais valores selecionados do dataframe"""
    # Verifica se os valores selecionados para ano, trimestre e banco são listas, caso contrário converte para listas
    if not isinstance(selected_year, list):
        selected_year = [selected_year]
    if not isinstance(selected_quarter, list):
        selected_quarter = [selected_quarter]
    if not isinstance(selected_bank, list):
        selected_bank = [selected_bank]

    # Filtra o dataframe com base nos valores selecionados
    filtered_df = df[
        (df["ANO"].isin(selected_year))
        & (df["TRIMESTRE"].isin(selected_quarter))
        & (df["NOME_BANCO"].isin(selected_bank))
    ]

    # Adiciona uma coluna 'ANO-TRIMESTRE' ao dataframe se ela não existir
    # A coluna é criada a partir das colunas 'ANO' e 'TRIMESTRE' com formato de string
    # Essa coluna é convertida para um objeto datetime
    if "ANO-TRIMESTRE" not in filtered_df.columns:
        filtered_df["ANO-TRIMESTRE"] = filtered_df.apply(
            lambda x: str(x["ANO"]) + "-" + x["TRIMESTRE"], axis=1
        )
        filtered_df["ANO-TRIMESTRE"] = pd.to_datetime(
            filtered_df["ANO-TRIMESTRE"], format="%Y-%m"
        )

    # Retorna o dataframe filtrado
    return filtered_df


@app.callback(
    Output('table', 'data'),
    [  # Parametros de inputs (Ano, Trimestre e Banco)
        Input("year-dropdown", "value"),
        Input("quarter-dropdown", "value"),
        Input("bank-dropdown", "value"),
    ],
)
def update_table(selected_year, selected_quarter, selected_bank):
    """Atualiza os gráficos baseados nos filtros escolhidos no dropdown"""

    # Filtra os dados com base nos parâmetros selecionados
    filtered_df = filter_data(selected_year, selected_quarter, selected_bank)\

    # Divide os valores numéricos por 1 milhão para que sejam exibidos em unidades bilionárias
    filtered_df['VOLUME_OP'] = filtered_df['VOLUME_OP'] / 1000000
    filtered_df['VOLUME_INTERBANK'] = filtered_df['VOLUME_INTERBANK'] / 1000000
    filtered_df['RESULT_OP'] = filtered_df['RESULT_OP'] / 1000000

    # Converte os valores numéricos em strings com duas casas decimais e os concatena com a unidade bilhão (Bi)
    filtered_df['VOLUME_OP'] = filtered_df['VOLUME_OP'].apply(
        lambda x: f"{x:.2f}Bi ")
    filtered_df['VOLUME_INTERBANK'] = filtered_df['VOLUME_INTERBANK'].apply(
        lambda x: f"{x:.2f}Bi ")

    # Verifica se RESULT_OP é diferente de zero antes de fazer a divisão e a concatenação
    filtered_df.loc[filtered_df['RESULT_OP'] != 0, 'RESULT_OP']\
        = filtered_df['RESULT_OP'][filtered_df['RESULT_OP'] != 0].apply(lambda x: f"{x:.2f}Bi ")

    # Converte o dataframe em um dicionário de registros para exibição na página da web
    return filtered_df.to_dict("records")


def update_lineplot(filtered_df):
    """Função que cria um lineplot com os filtros selecionados"""

    # Criando a figura de Visualização
    fig = px.line(
        filtered_df,  # Dataframe filtrado pelo dropdown
        x="ANO-TRIMESTRE",  # Valor em X
        y="TOTAL_OP",  # Valor em y
        color="NOME_BANCO",  # Por qual coluna haverá diferenciação de cores
        labels={
            "ANO-TRIMESTRE": "Ano e Trimestre",  # Nome da coluna no eixo X
            "TOTAL_OP": "Resultado das Operações",  # Nome da coluna no eixo Y
        },
        custom_data=["NOME_BANCO"],  # Dados customizados
        title="Resultado das Operações",  # Título do gráfico
        text=filtered_df["TOTAL_OP"] / 1000000,  # Informações de texto
        markers=True,  # Marcadores nos pontos do gráfico
        symbol="NOME_BANCO",  # Coluna usada para diferenciação de marcadores
        color_discrete_map=bank_colors,  # Paleta de cores pré-definidas para cada Banco
    )

    fig.update_traces(  # Atualizando o traço do LinePlot
        line=dict(width=1.8),  # Largura da linha
        textposition="bottom right",  # Posição do infotext
        texttemplate="%{text:.2f} Bi",  # Template do infotext
        hovertemplate="<br>".join([  # Template do hoverinfo
            "<br>Resultado das Operações: %{text:.2f} Bilhões (R$)",
        ]),
    )

    fig.update_layout(  # Atualizando as propriedades do Layout do Gráfico
        height=480,  # Altura da figura
        paper_bgcolor="white",  # Cor de fundo da figura
        font=dict(
                        family="BancoDoBrasil Textos",  # Fonte do texto
                        color='#002D4B',  # Cor do texto
        ),
        hoverlabel=dict(  # Propriedades do hoverlabel
            bordercolor='#002D4B',  # Cor da borda do hoverlabel
            font=dict(
                color='#002D4B',  # Cor do texto
                size=12,  # Tamanho do texto
                family="BancoDoBrasil Textos",  # Fonte do texto
            ),
            bgcolor="white",  # Cor de fundo do hoverlabel
        ),
        hovermode="x unified",  # Modo de exibição do hoverinfo
        title=dict(  # Propriedades do título do gráfico
            font=dict(
                size=20,  # Tamanho da fonte
                color="#0D214F",  # Cor do texto
                family="BancoDoBrasil Textos",  # Fonte do texto
            ),
            x=0.5,  # Posição do título no eixo X
            y=0.95,  # Posição do título no eixo Y
        ),
        xaxis=dict(  # Propriedades do eixo X
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor do texto
                    family="BancoDoBrasil Textos",  # Fonte do texto
                ),
            )
        ),
        yaxis=dict(  # Propriedades do eixo Y
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor do texto
                    family="BancoDoBrasil Textos",  # Fonte do texto
                ),
            )
        ),
        legend=dict(  # Propriedades da legenda
            bgcolor="rgba(0,0,0,0)",  # Cor de fundo da legenda
            yanchor="top",  # Posição da legenda no eixo Y
            y=0.99,  # Posição da legenda no eixo Y
            xanchor="left",  # Posição da legenda no eixo X
            x=1,  # Posição da legenda no eixo X
            font=dict(  # Propriedades do texto da legenda
                            size=11,  # Tamanho da fonte
                            color="#0D214F",  # Cor do texto
                            family="BancoDoBrasil Textos",  # Fonte do texto
            ),
            title=dict(  # Propriedades do título da legenda
                text="INSTITUIÇÕES BANCÁRIAS",  # Texto do título
                font=dict(  # Propriedades do texto do título
                    size=13,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",  # Familia da fonte
                ),
            ),
        ),
        margin=dict(l=1,
                    r=30,
                    t=50,
                    b=5),  # Margem do Plot
        transition_duration=1000,  # Tempo de transição na atulização do gráfico
    )
    return fig


def update_pieplot(filtered_df):
    """
    Atualiza o plot de pizza com os dados filtrados.
    """
    # Somar todas as operações dos bancos filtrados
    total = filtered_df["TOTAL_N"].sum()

    # Agrupar as operações por nome do banco
    por_banco = filtered_df.groupby("NOME_BANCO")["TOTAL_N"].sum()

    # Selecionar bancos com operações menores que 5% do total
    menor_5 = (por_banco / total) < 0.05

    # Remover bancos com operações menores que 5% do total
    maior_95 = filtered_df[filtered_df["NOME_BANCO"].isin(
        por_banco[~menor_5].index)]

    # Adicionar soma dos bancos com operações menores que 5% ao DataFrame como "Outros"
    com_outros = pd.concat(
        [
            maior_95,  # DataFrame com bancos com operações maiores que 5% do total
            pd.DataFrame(  # DataFrame com o total das operações dos bancos com menos de 5%
                {
                    # Soma das operações dos bancos com menos de 5%
                    "TOTAL_N": [por_banco[menor_5].sum()],
                    "NOME_BANCO": ["Outros"]  # Nome para o novo grupo
                }
            ),
        ]
    )

    # Cria uma figura com o tipo de gráfico pie chart a partir do dataframe com_outros
    fig = px.pie(
        com_outros,  # Dataframe feito acima
        values="TOTAL_N",  # Coluna com os valores das fatias
        names="NOME_BANCO",  # Coluna com os nomes das fatias
        title="Total de Operações",  # Título do gráfico
        color="NOME_BANCO",  # Coluna que determina as cores das fatias
        # Dicionário com as cores padrão para cada valor da coluna color
        color_discrete_map=bank_colors,
        # Lista com as colunas extras que serão exibidas ao passar o mouse sobre as fatias (info text)
        custom_data=["NOME_BANCO"],
    )

    # Define algumas configurações das fatias do gráfico
    fig.update_traces(
        textposition="inside",  # Posição do texto dentro das fatias
        # Informações que serão exibidas no texto das fatias (percentual e rótulo)
        textinfo="percent+label",
        hovertemplate="<br>".join(  # Formato do texto que aparece quando o mouse é posicionado sobre as fatias
            [
                # Coluna extra que será exibida no info text
                "Instituição: %{customdata[0]}",
                "Numero de Operações: %{value} ",  # Valor numérico da fatia
            ]
        ),
    )
    # Define algumas configurações gerais do layout do gráfico
    fig.update_layout(
        width=460,  # Largura da figura
        height=480,  # Altura da figura
        font=dict(  # Configurações da fonte
            family="BancoDoBrasil Textos",  # Nome da fonte
            color='#002D4B',  # Cor da fonte
        ),
        hoverlabel=dict(  # Configurações da caixa de texto que aparece ao passar o mouse sobre as fatias
            bordercolor='#002D4B',  # Cor da borda da caixa
            font=dict(  # Configurações da fonte da caixa
                color='#002D4B',  # Cor da fonte
                size=12,  # Tamanho da fonte
                family="BancoDoBrasil Textos",  # Nome da fonte
            ),
            bgcolor="white",  # Cor de fundo da caixa
        ),
        paper_bgcolor="white",  # Cor de fundo da figura
        title=dict(  # Configurações do título do gráfico
            font=dict(
                size=20,  # Tamanho da fonte
                color="#0D214F",  # Cor da fonte
                family="Arial",  # Nome da fonte
            ),
            x=0.5,  # Posição do título no eixo x (0 = esquerda, 1 = direita)
            y=0.95,  # Posição do título no eixo y (0 = baixo, 1 = topo)
        ),
        xaxis=dict(  # Configuração para o eixo X
            title=dict(  # Configuração para o título do eixo X
                font=dict(  # Configuração para a fonte do título do eixo X
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte em código hexadecimal
                    family="Arial",  # Família da fonte
                ),
            )
        ),
        yaxis=dict(  # Configuração para o eixo Y
            title=dict(  # Configuração para o título do eixo Y
                font=dict(  # Configuração para a fonte do título do eixo Y
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte em código hexadecimal
                    family="Arial",  # Família da fonte
                ),
            )
        ),
        legend=dict(  # Configuração para a legenda
            orientation="h",  # Orientação horizontal
            yanchor="middle",  # Âncora vertical no meio
            y=-0.2,  # Posição vertical relativa à âncora
            xanchor="center",  # Âncora horizontal no centro
            x=0.5,  # Posição horizontal relativa à âncora
            bgcolor="rgba(0,0,0,0)",  # Cor de fundo da legenda
        ),
        # Duração da transição na atualização do gráfico em milissegundos
        transition=dict(duration=1500),
    )
    return fig


def update_spread_lineplot(filtered_df):
    """Função que cria um lineplot do spread com os filtros selecionados"""

    # Criando a figura de Visualização com a biblioteca Plotly Express
    fig = px.line(
        filtered_df,  # Dataframe filtrado pelo dropdown
        x="ANO-TRIMESTRE",  # Coluna com os valores do eixo X
        y="SPREAD",  # Coluna com os valores do eixo Y
        color="NOME_BANCO",  # Coluna com valores distintos para diferenciar as cores das linhas
        labels={  # Renomeando as colunas do gráfico
            "ANO-TRIMESTRE": "Ano e Trimestre",
            "SPREAD": "Spread",
        },
        # Selecionando quais dados extras serão mostrados em hover
        custom_data=["NOME_BANCO"],
        text="SPREAD",  # Selecionando quais valores aparecerão ao passar o mouse sobre as linhas
        title="Spread Cambial (%)",  # Título do gráfico
        markers=True,  # Habilitando marcadores nos pontos da linha
        # Definindo uma paleta de cores pré-definida para cada banco
        color_discrete_map=bank_colors,
    )

    fig.update_traces(  # Atualizando o traço do LinePlot
        line=dict(width=1.8),  # Largura da linha do lineplot
        textposition="bottom right",  # Posição do texto nos pontos do lineplot
        texttemplate="%{y:.2f} %",  # Formato do texto nos pontos do lineplot
        hovertemplate="<br>".join(
            [
                "Spread: %{y}%",  # Texto do hover nos pontos do lineplot
            ]
        )
    )

    fig.update_layout(  # Estilizando a Visualização
        height=480,  # Altura da figura
        font=dict(
            family="BancoDoBrasil Textos",  # Fonte do texto
            color='#002D4B',  # Cor do texto
        ),
        paper_bgcolor="white",  # Cor do fundo da figura
        # plot_bgcolor="#0D214F", # Cor no fundo do Plot
        hoverlabel=dict(
            bordercolor='#002D4B',  # Cor da borda do hover
            font=dict(
                color='#002D4B',  # Cor do texto do hover
                size=12,  # Tamanho da fonte do hover
                family="BancoDoBrasil Textos"  # Fonte do texto do hover
            ),
            bgcolor="white",  # Cor do fundo do hover
        ),
        hovermode="x unified",  # Modo do hover
        title=dict(  # Titulo
            font=dict(
                size=20,  # Tamanho da fonte do titulo
                color="#0D214F",  # Cor do titulo
                family="BancoDoBrasil Textos",  # Fonte do titulo
            ),
            x=0.5,  # Posição do titulo no eixo X
            y=0.95,  # Posição do titulo no eixo Y
        ),
        xaxis=dict(  # Eixo X
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte do titulo do eixo X
                    color="#0D214F",  # Cor do titulo do eixo X
                    family="BancoDoBrasil Textos",  # Fonte do titulo do eixo X
                ),
            )
        ),
        yaxis=dict(  # Eixo Y
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte do titulo do eixo Y
                    color="#0D214F",  # Cor do titulo do eixo Y
                    family="BancoDoBrasil Textos",  # Fonte do titulo do eixo Y
                ),
            )
        ),
        legend=dict(  # Legenda
            bgcolor="rgba(0,0,0,0)",  # Cor de fundo da legenda
            yanchor="top",  # Âncora da legenda no eixo Y
            y=0.99,  # Posição da legenda no eixo Y
            xanchor="left",  # Âncora da legenda no eixo X
            x=1,  # Posição da legenda no eixo X
            font=dict(  # Fonte da Legenda
                size=11,  # Tamanho da fonte
                color="#0D214F",  # Cor da fonte
                family="BancoDoBrasil Textos",  # Familia da fonte
            ),
            title=dict(  # Titulo da Legenda
                text="INSTITUIÇÕES BANCÁRIAS",  # String
                font=dict(  # Fonte do Titulo da Leganda
                    size=13,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",  # Familia da fonte
                ),
            ),
        ),
        margin=dict(l=1, r=30, t=50, b=5),
        transition_duration=1000,  # Tempo de transição na atulização do gráfico
    )
    return fig


def create_barplot(filtered_df):
    """Cria um barplot dos valores trimestrais ou anuais usando os filtros"""

    # Linhas onde o banco é o BB
    bb = filtered_df[filtered_df["NOME_BANCO"] == "BB"]

    # Somando os valores por Trimestre e ano
    filtered_df = filtered_df.groupby("ANO-TRIMESTRE").sum().reset_index()

    # Aplicando o nome mercado para o total
    filtered_df["NOME_BANCO"] = "MERCADO"

    # Juntanto o BB com o Mercado
    final_df = pd.concat([bb, filtered_df])

    # Valor total do Mercado
    total = final_df["TOTAL_VOL"].sum()

    # Pegando a porcentagem que o BB representa do Total
    final_df.loc[final_df["NOME_BANCO"] == "BB", "PORCENTAGEM"] = (
        final_df[final_df["NOME_BANCO"] == "BB"]["TOTAL_VOL"] / total
    ) * 1000

    final_df["TOTAL_VOL"] = final_df["TOTAL_VOL"] / 1000000

    def acumulado_ano(df):
        # Adicionar coluna ANO ao DataFrame df

        df["ANO"] = pd.to_datetime(df["ANO-TRIMESTRE"], format="%Y-%m").dt.year

        # Agrupa os valores do "TOTAL_N" pela coluna "ANO" para o banco "BB"
        bb_total = df[df["NOME_BANCO"] == "BB"].groupby(
            "ANO").agg({"TOTAL_VOL": "sum"})
        # Agrupa os valores do "TOTAL_N" pela coluna "ANO" para o mercado
        market_total = df[df["NOME_BANCO"] == "MERCADO"].groupby(
            "ANO").agg({"TOTAL_VOL": "sum"})

        # Cria um novo DataFrame com os totais do banco "BB"
        bb_total_df = bb_total.reset_index().rename(
            columns={"TOTAL_VOL": "TOTAL_VOL"}).assign(NOME_BANCO="BB")
        # Cria um novo DataFrame com os totais do mercado
        market_total_df = market_total.reset_index().rename(
            columns={"TOTAL_VOL": "TOTAL_VOL"}).assign(NOME_BANCO="MERCADO")

        # Concatena os dois novos DataFrames em um único DataFrame "total_df"
        total_df = pd.concat([bb_total_df, market_total_df])
        # Calcula o total acumulado a cada ano
        total_acumulado = total_df.groupby(
            "ANO")["TOTAL_VOL"].sum().reset_index()
        # Calcula a porcentagem do BB do total de cada ano
        total_df.loc[total_df["NOME_BANCO"] == "BB", "PORCENTAGEM"] = (
            total_df[total_df["NOME_BANCO"] == "BB"]["TOTAL_VOL"] /
            total_acumulado["TOTAL_VOL"]
        ) * 100

        # Converte a coluna "ANO" para o tipo "Datetime"
        total_df["ANO"] = pd.to_datetime(total_df["ANO"], format="%Y")

        return total_df

    def fig(df, periodo):

        fig = px.bar(  # Cria uma figura de barras
            df,  # Dataframe filtrado pelo dropdown
            x=periodo,  # Define o eixo x como o período (ano e trimestre)
            y="TOTAL_VOL",  # Define o eixo y como o volume total de câmbio
            color="NOME_BANCO",  # Define a coluna que diferencia as cores como o nome do banco
            # Define o modo das barras como "group" (barras agrupadas)
            barmode="group",
            labels={  # Define os rótulos dos eixos
                periodo: "Ano e Trimestre",
                "TOTAL_VOL": "Volume",
            },
            # Define quais dados personalizados serão exibidos ao passar o mouse sobre as barras
            custom_data=["NOME_BANCO"],
            text="TOTAL_VOL",  # Define o texto exibido sobre as barras como o volume total de câmbio
            title="Volume de câmbio BB x Mercado",  # Define o título da figura
            color_discrete_map=bank_colors,  # Define a paleta de cores para cada banco
        )
        fig.update_traces(  # Atualiza as propriedades das barras
            hovertemplate="<br>".join(  # Define o formato de exibição ao passar o mouse sobre as barras
                [
                    # Nome da instituição (BB ou Mercado)
                    "Instituição: %{customdata[0]}",
                    "Ano e Trimestre: %{x}",  # Período (ano e trimestre)
                    # Volume de câmbio formatado em bilhões de dólares
                    "Volume de Câmbio: %{y:.2f} Bilhoes (USD) ",
                ]
            ),
            # Define o formato do texto exibido sobre as barras como bilhões de dólares
            texttemplate="%{y:.2f} Bi USD",
            textfont=dict(  # Define a fonte do texto exibido sobre as barras
                # Define a família da fonte como "BancoDoBrasil Textos"
                family="BancoDoBrasil Textos",
                color="white"),  # Define a cor do texto como branco
        )

        fig.update_yaxes(  # Define o título e alinha o eixo y principal
            secondary_y=False,
            title_text="Volume de Câmbio"
        )

        # Adiciona um gráfico de linhas para a participação do BB
        fig.add_trace(
            go.Scatter(
                x=df[periodo],  # Define o eixo x com base no dropdown selecionado
                # Define a participação do BB como valor de y
                y=df["PORCENTAGEM"],
                mode="lines+markers+text",  # Define o tipo de visualização
                line_width=1.8,  # Define a largura da linha
                line_color="#a1b2da",  # Define a cor da linha
                name="Participação BB %",  # Define o nome da linha na legenda
                yaxis="y2",  # Define que a linha será plotada no eixo y secundário
                # Define o template para o texto que será exibido nos marcadores
                texttemplate="%{y:.2f}%",
                hovertemplate="<br>".join(
                    ["Participação do BB: %{y:.2f}%", "Ano e Trimestre: %{x}"]
                ),  # Define o texto exibido no hover
                textfont=dict(
                    family="BancoDoBrasil Textos",
                    color="#8694B5"
                ),  # Define a fonte e a cor do texto
                textposition="top left",  # Define a posição do texto
            )
        )

        fig.update_yaxes(
            title_text="Participação BB em %",  # Define o título do eixo secundário
            secondary_y=True,  # Define o eixo secundário como True
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",  # Familia da fonte
                ),
            ),
        )

        fig.update_layout(  # Atualizando o layout da figura
            height=480,  # Definindo a altura da figura
            paper_bgcolor="white",  # Definindo a cor de fundo da figura
            hoverlabel=dict(  # Definindo a caixa de texto ao passar o mouse
                bordercolor='#002D4B',  # Cor da borda da caixa
                font=dict(  # Definindo a fonte da caixa
                            color='#002D4B',  # Cor do texto da caixa
                            size=12,  # Tamanho do texto da caixa
                            family="BancoDoBrasil Textos"  # Fonte do texto da caixa
                ),
                bgcolor="white",  # Cor de fundo da caixa
            ),
            title=dict(  # Configurando o título
                font=dict(
                    size=20,  # Tamanho da fonte do título
                    color="#0D214F",  # Cor do título
                    family="BancoDoBrasil Textos",  # Fonte do título
                ),
                x=0.5,  # Posição do título no eixo X
                y=0.95,  # Posição do título no eixo y
            ),
            xaxis=dict(  # Configurando o eixo X
                title=dict(
                    font=dict(
                        size=16,  # Tamanho da fonte do título do eixo X
                        color="#0D214F",  # Cor do título do eixo X
                        family="BancoDoBrasil Textos",  # Fonte do título do eixo X
                    ),
                )
            ),
            yaxis=dict(  # Configurando o eixo Y principal
                title=dict(
                    font=dict(
                        size=16,  # Tamanho da fonte do título do eixo Y
                        color="#0D214F",  # Cor do título do eixo Y
                        family="BancoDoBrasil Textos",  # Fonte do título do eixo Y
                    ),
                )
            ),
            yaxis2=dict(  # Configurando o eixo Y secundário
                title="Participação BB em %",  # Título do eixo Y secundário
                title_font=dict(
                    size=16,  # Tamanho da fonte do título do eixo Y secundário
                    color="#0D214F",  # Cor do título do eixo Y secundário
                    family="BancoDoBrasil Textos",  # Fonte do título do eixo Y secundário
                ),
                type="linear",  # Tipo do eixo Y secundário
                linewidth=2,  # Largura da linha do eixo Y secundário
                overlaying="y",  # Sobrepõe o eixo Y principal
                side="right",  # Posiciona o eixo Y secundário à direita
                # Define o intervalo do eixo Y secundário
                range=[0, 30],
            ),
            legend=dict(  # Configurando a legenda
                bgcolor="rgba(0,0,0,0)",  # Cor de fundo da legenda
                yanchor="top",  # Âncora vertical da legenda
                y=0.99,  # Posição vertical da legenda
                xanchor="left",  # Âncora horizontal da legenda
                x=1,  # Posição horizontal da legenda
                font=dict(  # Fonte da Legenda
                            size=11,  # Tamanho da fonte
                            color="#0D214F",  # Cor da fonte
                            family="BancoDoBrasil Textos",  # Familia da fonte
                ),
                title=dict(  # Titulo da Legenda
                    font=dict(  # Fonte do Titulo da Leganda
                                size=13,  # Tamanho da fonte
                                color="#0D214F",  # Cor da fonte
                                family="BancoDoBrasil Textos",  # Familia da fonte
                    ),
                ),
            ),
            # Configurando as margens do gráfico
            margin=dict(l=1, r=90, t=50, b=5),
            transition_duration=1000,  # Tempo de transição na atualização do gráfico
        )
        return fig

    # Criando o dataFrame do acumulado por ano
    total_df = acumulado_ano(final_df)

    # Grafico trimestral
    fig1 = fig(final_df, "ANO-TRIMESTRE")
    # Grafico Anual
    fig2 = fig(total_df, "ANO")

    return fig1, fig2


@app.callback(
    # identificador da saída e o tipo de dado esperado
    Output("bar-lineplot", "figure"),
    [
        # identificador do ano selecionado pelo usuário
        Input("year-dropdown", "value"),
        # identificador do trimestre selecionado pelo usuário
        Input("quarter-dropdown", "value"),
        # identificador do banco selecionado pelo usuário
        Input("bank-dropdown", "value"),
        # identificador do número de cliques no botão trimestral
        Input("trimestral-button", "n_clicks"),
        # identificador do número de cliques no botão anual
        Input("ano-button", "n_clicks"),
    ],
)
def update_barplot(
        selected_year, selected_quarter, selected_bank, trimestral_clicks, ano_clicks):
    """
    Função que retorna Anual ou Trimestral dependendo de qual botão for clicado
    Recebe como entrada as opções selecionadas pelo usuário no dropdown
    """

    # Filtra os dados de acordo com as opções selecionadas pelo usuário
    filtered_df = filter_data(selected_year, selected_quarter, selected_bank)

    # Cria os gráficos de barra
    fig1, fig2 = create_barplot(filtered_df)

    # Obtém o contexto da chamada da função de callback
    ctx = dash.callback_context

    # Verifica qual botão foi clicado e retorna o gráfico apropriado
    if ctx.triggered[0]["prop_id"] == "trimestral-button.n_clicks":
        return fig1
    elif ctx.triggered[0]["prop_id"] == "ano-button.n_clicks":
        return fig2
    return fig1


@app.callback(
    [
        # Saída 1: gráfico de pizza
        Output("operations-result-pieplot", "figure"),
        # Saída 2: gráfico de linha
        Output("spread-lineplot", "figure"),
        # Saída 3: gráfico de linha
        Output("operations-result-lineplot", "figure"),
    ],
    [
        # Entrada 1: dropdown com seleção do ano
        Input("year-dropdown", "value"),
        # Entrada 2: dropdown com seleção do trimestre
        Input("quarter-dropdown", "value"),
        # Entrada 3: dropdown com seleção do banco
        Input("bank-dropdown", "value"),
    ],
)
def update_plots(selected_year, selected_quarter, selected_bank):
    """
    Atualiza os gráficos baseados nos filtros escolhidos no dropdown
    """

    # Filtra o DataFrame com base nas opções selecionadas
    filtered_df = filter_data(selected_year, selected_quarter, selected_bank)

    # Atualiza o gráfico de linha de resultados
    line_plot = update_lineplot(filtered_df)

    # Atualiza o gráfico de pizza de número de operações
    pie_plot = update_pieplot(filtered_df)

    # Atualiza o gráfico de linha de spread
    spread_line_plot = update_spread_lineplot(filtered_df)

    # Retorna as figuras dos gráficos
    return pie_plot, spread_line_plot, line_plot


@app.callback(
    # Saída da função, atualiza o valor do dropdown
    Output('bank-dropdown', 'value'),
    # Entrada da função, cliques no botão "Selecionar Todos"
    [Input('select_all', 'n_clicks')],
    # Estado da função, opções do dropdown
    [State('bank-dropdown', 'options')]
)
def update_dropdown(n_clicks, feature_options):

    ctx = dash.callback_context  # Obtém o contexto da chamada da callback

    # Verifica se a callback foi disparada
    if not ctx.triggered:
        raise PreventUpdate()
    else:
        trigged_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Verifica se o botão "Selecionar Todos" foi clicado
        if trigged_id == 'select_all':

            # Não atualiza o dropdown no início da aplicação
            if n_clicks == 0:
                raise PreventUpdate()

            # Limpa todas as opções do dropdown nos cliques pares
            if n_clicks % 2 == 0:
                return []
            else:  # Seleciona todas as opções do dropdown nos cliques ímpares
                return [i['value'] for i in feature_options]
        else:
            raise PreventUpdate()  # Não atualiza o dropdown em caso de outras entradas


if __name__ == "__main__":  # Iniciando o o Dashboard
    app.run_server(debug=True)  # Ativando o debugmode
