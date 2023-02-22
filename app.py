# Importação das bibliotecas utilizadas
from dash import dcc, html, Input, Output, Dash, dash_table
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

# Carregando e Modificando o arquivo CSV em um DataFrame
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
    
    #Para visualização no DataTable
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

# Armazena as colunas relevantes do dataframe df em uma nova variável 'table'
table = df[['NOME_BANCO', 'ANO_TRIMESTRE', 'VOLUME_OP',
             'VOLUME_INTERBANK', 'RESULT_OP']]

# Cria uma lista 'cols' com dicionários, onde cada dicionário tem as chaves "name" e "id", 
# relacionando o nome de cada coluna com sua identificação
cols = [{"name": i, "id": i} for i in table.columns]

# Sobrescreve 'cols' com uma nova lista, agora especificando o nome que cada coluna deve ter na exibição
cols = [{"name": "Banco", "id": "NOME_BANCO"},
        {"name": "Ano", "id": "ANO_TRIMESTRE"},
        {"name": "Vol. Op.", "id": "VOLUME_OP"},
        {"name": "Vol. Op. Inter", "id": "VOLUME_INTERBANK"},
        {"name": "Result. Op.", "id": "RESULT_OP"}]

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
                                          sort_by=[ {"column_id": "ANO_TRIMESTRE", "direction": "desc"},{"column_id": "RESULT_OP", "direction": "desc"}],
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
    if not isinstance(selected_year, list):
        selected_year = [selected_year]
    if not isinstance(selected_quarter, list):
        selected_quarter = [selected_quarter]
    if not isinstance(selected_bank, list):
        selected_bank = [selected_bank]

    filtered_df = df[
        (df["ANO"].isin(selected_year))
        & (df["TRIMESTRE"].isin(selected_quarter))
        & (df["NOME_BANCO"].isin(selected_bank))
    ]

    if "ANO-TRIMESTRE" not in filtered_df.columns:
        filtered_df["ANO-TRIMESTRE"] = filtered_df.apply(
            lambda x: str(x["ANO"]) + "-" + x["TRIMESTRE"], axis=1
        )

        filtered_df["ANO-TRIMESTRE"] = pd.to_datetime(
            filtered_df["ANO-TRIMESTRE"], format="%Y-%m"
        )

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
    filtered_df = filter_data(selected_year, selected_quarter, selected_bank)\

    return filtered_df.to_dict("records")


def update_lineplot(filtered_df):
    """Função que cria um lineplot com os filtros selecionados"""

    fig = px.line(  # Criando a figura de Visualização
        filtered_df,  # Dataframe filtrado pelo dropdown
        x="ANO-TRIMESTRE",  # Valor em X
        y="TOTAL_OP",  # Valor em y
        color="NOME_BANCO",  # Por qual coluna haverá diferenciação de cores
        labels={  # Nome das colunas na legenda
            "ANO-TRIMESTRE": "Ano e Trimestre",
            "TOTAL_OP": "Resultado das Operações",
        },
        custom_data=["NOME_BANCO"],
        title="Resultado das Operações",
        text=filtered_df["TOTAL_OP"] / 1000000,  # Info text
        markers=True,  # Marcação nos pontos no gráfico
        symbol="NOME_BANCO",  # Por qual coluna haverá diferenciação no simbolo dos marcadores
        color_discrete_map=bank_colors,  # Paleta de cores pré-definidas para cada Banco
    )

    fig.update_traces(
        line=dict(width=1.8),  # Expressura da Linha
        textposition="bottom right",  # Onde o infotext ficaria
        texttemplate="%{text:.2f} Bi",
        hovertemplate="<br>".join(
            [  # Quais informacoes serão apresentadas
                # "Instituição: %{customdata[0]}",
                # "Ano e Trimestre: %{x}",
                "<br> Resultado das Operações: %{text:.2f} Bilhões (R$)",
            ]
        ),
    )  # Atualizando o traço do LinePlot
    fig.update_layout(  # Estilizando a Visualização
        height=480,  # Altura
        paper_bgcolor="white",
        # plot_bgcolor="#0D214F", # Cor no fundo do Plot
        font=dict(
            family="BancoDoBrasil Textos",
            color='#002D4B',
        ),
        # Cor em volta do Plot

        hoverlabel=dict(
            bordercolor='#002D4B',
            font=dict(
                color='#002D4B',
                size=12,
                family="BancoDoBrasil Textos"
            ),
            bgcolor="white",
        ),
        hovermode="x unified",
        title=dict(  # Titulo
            font=dict(
                size=20,  # Tamanho da fonte
                color="#0D214F",  # Cor da fonte
                family="BancoDoBrasil Textos",  # Familia da fonte
            ),
            x=0.5,  # Posição no eixo X
            y=0.95,  # Posição no eixo y
        ),
        xaxis=dict(  # Escala de X
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",  # Familia da fonte
                ),
            )
        ),
        yaxis=dict(  # Escala de Y
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",  # Familia da fonte
                ),
            )
        ),
        legend=dict(  # Legenda
            bgcolor="rgba(0,0,0,0)",  # Cor de fundo
            yanchor="top",  # Ancora Y
            y=0.99,  # Posição Y
            xanchor="left",  # Ancora X
            x=1,  # Posicao X
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
            maior_95,
            pd.DataFrame(
                {"TOTAL_N": [por_banco[menor_5].sum()], "NOME_BANCO": [
                    "Outros"]}
            ),
        ]
    )

    fig = px.pie(
        com_outros,  # Dataframe feito acima
        values="TOTAL_N",  # Valores
        names="NOME_BANCO",  # Nome das fatias
        title="Total de Operações",  # Titulo
        color="NOME_BANCO",  # Por qual coluna mudara as cores
        color_discrete_map=bank_colors,  # Padrão de Cores
        custom_data=["NOME_BANCO"],  # Dado para Infotext
    )

    fig.update_traces(
        textposition="inside",  # Posição do Infotext
        textinfo="percent+label",  # O que sera apresentado no Infotext
        hovertemplate="<br>".join(
            [  # Formatação do Hovertext
                "Instituição: %{customdata[0]}",
                "Numero de Operações: %{value} ",
            ]
        ),
    )
    fig.update_layout(
        width=460,  # Largura
        height=480,  # Altura
        font=dict(
            family="BancoDoBrasil Textos",
            color='#002D4B',
        ),
        # Cor em volta do Plot

        hoverlabel=dict(
            bordercolor='#002D4B',
            font=dict(
                color='#002D4B',
                size=12,
                family="BancoDoBrasil Textos"
            ),
            bgcolor="white",
        ),
        paper_bgcolor="white",  # Cor em volta do Plot
        # plot_bgcolor="#0D214F", # Cor no fundo do Plot
        title=dict(  # Titulo
            font=dict(
                size=20,  # Tamanho da fonte
                color="#0D214F",  # Cor da fonte
                family="Arial",  # Familia da fonte
            ),
            x=0.5,  # Posição no eixo X
            y=0.95,  # Posição no eixo y
        ),
        xaxis=dict(  # Valor em X
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="Arial",  # Familia da fonte
                ),
            )
        ),
        yaxis=dict(
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="Arial",  # Familia da fonte
                ),
            )
        ),
        legend=dict(
            orientation="h",
            yanchor="middle",
            y=-0.2,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
        ),
        # Tempo de transição na atulização do gráfico
        transition=dict(duration=1500),
    )
    return fig


def update_spread_lineplot(filtered_df):
    """Função que cria um lineplot do spread com os filtros selecionados"""

    fig = px.line(  # Criando a figura de Visualização
        filtered_df,  # Dataframe filtrado pelo dropdown
        x="ANO-TRIMESTRE",  # Valor em X
        y="SPREAD",  # Valor em y
        color="NOME_BANCO",  # Por qual coluna haverá diferenciação de cores
        labels={  # Nome das colunas na legenda
            "ANO-TRIMESTRE": "Ano e Trimestre",
            "SPREAD": "Spread",
        },
        custom_data=["NOME_BANCO"],
        text="SPREAD",
        title="Spread Cambial (%)",  # Titulo
        markers=True,  # Marcação nos pontos no gráfico
        color_discrete_map=bank_colors,  # Paleta de cores pré-definidas para cada Banco
    )

    fig.update_traces(
        line=dict(width=1.8),
        textposition="bottom right",
        texttemplate="%{y:.2f} %",
        hovertemplate="<br>".join(
            [
                # "Instituição: %{customdata[0]}",
                # "Ano e Trimestre: %{x}",
                "Spread: %{y}%",
            ]
        )
    )  # Atualizando o traço do LinePlot

    fig.update_layout(  # Estilizando a Visualização
        height=480,
        font=dict(
            family="BancoDoBrasil Textos",
            color='#002D4B',
        ),
        paper_bgcolor="white",  # Cor em volta do Plot
        # plot_bgcolor="#0D214F", # Cor no fundo do Plot
        hoverlabel=dict(
            bordercolor='#002D4B',
            font=dict(
                color='#002D4B',
                size=12,
                family="BancoDoBrasil Textos"
            ),
            bgcolor="white",
        ),
        hovermode="x unified",
        title=dict(  # Titulo
            font=dict(
                size=20,  # Tamanho da fonte
                color="#0D214F",  # Cor da fonte
                family="BancoDoBrasil Textos",  # Familia da fonte
            ),
            x=0.5,  # Posição no eixo X
            y=0.95,  # Posição no eixo y
        ),
        xaxis=dict(  # Valor em X
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",  # Familia da fonte
                ),
            )
        ),
        yaxis=dict(
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",  # Familia da fonte
                ),
            )
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1,
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

        fig = px.bar(  # Criando a figura de Visualização
            df,  # Dataframe filtrado pelo dropdown
            x=periodo,  # Valor em X
            y="TOTAL_VOL",  # Valor em y
            color="NOME_BANCO",
            barmode="group",  # Por qual coluna haverá diferenciação de cores
            labels={  # Nome das colunas na legenda
                periodo: "Ano e Trimestre",
                "TOTAL_VOL": "Volume",
            },
            custom_data=["NOME_BANCO"],
            text="TOTAL_VOL",
            title="Volume de câmbio BB x Mercado",  # Titulo
            # Marcação nos pontos no gráfico
            color_discrete_map=bank_colors,  # Paleta de cores pré-definidas para cada Banco
        )
        fig.update_traces(
            hovertemplate="<br>".join(
                [
                    "Instituição: %{customdata[0]}",
                    "Ano e Trimestre: %{x}",
                    "Volume de Câmbio: %{y:.2f} Bilhoes (USD) ",
                ]
            ),
            texttemplate="%{y:.2f} Bi USD",
            textfont=dict(
                family="BancoDoBrasil Textos",
                color="white"),
        )

        fig.update_yaxes(
            secondary_y=False, title_text="Volume de Câmbio"
        )

        fig.add_trace(
            go.Scatter(
                x=df[periodo],
                y=df["PORCENTAGEM"],
                mode="lines+markers+text",
                line_width=1.8,
                line_color="#a1b2da",
                name="Participação BB %",
                yaxis="y2",
                texttemplate="%{y:.2f}%",
                hovertemplate="<br>".join(
                    ["Participação do BB: %{y:.2f}%", "Ano e Trimestre: %{x}"]
                ),
                textfont=dict(
                    family="BancoDoBrasil Textos",
                    color="#8694B5"),
                textposition="top left",
            )
        )

        fig.update_yaxes(
            title_text="Participação BB em %",
            secondary_y=True,
            title=dict(
                font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",  # Familia da fonte
                ),
            ),
        )

        fig.update_layout(  # Estilizando a Visualização
            height=480,
            paper_bgcolor="white",
            # Cor em volta do Plot
            # plot_bgcolor="#0D214F", # Cor no fundo do Plot
            hoverlabel=dict(
                bordercolor='#002D4B',
                font=dict(
                    color='#002D4B',
                    size=12,
                    family="BancoDoBrasil Textos"
                ),
                bgcolor="white",
            ),
            title=dict(  # Titulo
                font=dict(
                    size=20,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",  # Familia da fonte
                ),
                x=0.5,  # Posição no eixo X
                y=0.95,  # Posição no eixo y
            ),
            xaxis=dict(  # Valor em X
                title=dict(
                    font=dict(
                        size=16,  # Tamanho da fonte
                        color="#0D214F",  # Cor da fonte
                        family="BancoDoBrasil Textos",  # Familia da fonte
                    ),
                )
            ),
            yaxis=dict(
                title=dict(
                    font=dict(
                        size=16,  # Tamanho da fonte
                        color="#0D214F",  # Cor da fonte
                        family="BancoDoBrasil Textos",  # Familia da fonte
                    ),
                )
            ),
            yaxis2=dict(
                title="Participação BB em %",
                title_font=dict(
                    size=16,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",
                ),
                type="linear",
                linewidth=2,
                overlaying="y",
                side="right",
                range=[0, 30],
            ),
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1,
                font=dict(  # Fonte da Legenda
                    size=11,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="BancoDoBrasil Textos",  # Familia da fonte
                ),
                title=dict(  # Titulo da Legenda
                    # String
                    font=dict(  # Fonte do Titulo da Leganda
                        size=13,  # Tamanho da fonte
                        color="#0D214F",  # Cor da fonte
                        family="BancoDoBrasil Textos",  # Familia da fonte
                    ),
                ),
            ),
            margin=dict(l=1, r=90, t=50, b=5),
            transition_duration=1000,  # Tempo de transição na atulização do gráfico
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
        Output("operations-result-pieplot", "figure"),
        Output("spread-lineplot", "figure"),
        Output("operations-result-lineplot", "figure"),
    ],
    [  # Parametros de inputs (Ano, Trimestre e Banco)
        Input("year-dropdown", "value"),
        Input("quarter-dropdown", "value"),
        Input("bank-dropdown", "value"),
    ],
)
def update_plots(selected_year, selected_quarter, selected_bank):
    """
    Atualiza os gráficos baseados nos filtros escolhidos no dropdown
    """

    # Filtra o DataFrame com base nas opções selecionadas
    filtered_df = filter_data(selected_year, selected_quarter, selected_bank)

    # Atualiza o gráfico de linha
    line_plot = update_lineplot(filtered_df)

    # Atualiza o gráfico de pizza
    pie_plot = update_pieplot(filtered_df)

    # Atualiza o gráfico de linha de espalhamento
    spread_line_plot = update_spread_lineplot(filtered_df)

    # Retorna as figuras dos gráficos
    return pie_plot, spread_line_plot, line_plot


if __name__ == "__main__":  # Iniciando o o Dashboard
    app.run_server(debug=True)  # Ativando o debugmode
