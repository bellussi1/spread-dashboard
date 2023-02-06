# Importação das bibliotecas utilizadas
from dash import dcc, html, Input, Output, Dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
"""
Este código é um aplicativo Dash que cria um painel de operações bancárias.
Ele carrega os dados de um arquivo CSV e os armazena em um dataframe do pandas.
Ele cria uma lista única de anos, bancos e trimestres para as opções de filtro.
A estrutura do painel é criada usando o dash e inclui três seleções dropdown para selecionar o ano, trimestre
e banco desejado, e um gráfico para exibir os resultados das operações. O gráfico é atualizado dinamicamente
com base nas opções de filtro selecionadas, usando o callback.
"""
# Carregando o arquivo CSV para um dataframe
df = pd.read_csv("data/spread.csv")

bank_colors = {  # Dicionario de cores para os principais Bancos
    "BB": "#F9DD16",
    "ITAU": "#FF9641",
    "BRADESCO": "#633280",
    "SANTANDER": "#ec0000",
    "Outros": "gray",
    "MERCADO": '#0038A8'
}
# Criando o dicionário de substituições
quarter_replace = {1: "03", 2: "06", 3: "09", 4: "12"}

# aplicando a substituição na coluna TRIMESTRE
df["TRIMESTRE"] = df["TRIMESTRE"].replace(quarter_replace)

# 'Somando' o Ano - Trimestre para uma unica coluna
df["ANO-TRIMESTRE"] = df.apply(lambda x: str(x["ANO"]) +
                               "-" + x["TRIMESTRE"], axis=1)

# Formatando os valores para o tipo Date
df["ANO-TRIMESTRE"] = pd.to_datetime(df["ANO-TRIMESTRE"], format="%Y-%m")

# Criando a coluna total
df["TOTAL_OP"] = df.apply(lambda x: int(
    x["RESULT_OP"]) + x["DESPESA_OP"], axis=1)
df["TOTAL_N"] = df.apply(lambda x: int(
    x["NUMERO_OP"]) + x["NUMERO_INTERBANK"], axis=1)

# Criando a coluna de spread
df["SPREAD"] = df.apply(
    lambda x: (x["VOLUME_OP"] + x["VOLUME_INTERBANK"])
    / (int(x["RESULT_OP"]) + x["DESPESA_OP"])
    / 100,
    axis=1,
)
# Limitando a duas casas após a virgula
df["SPREAD"] = df["SPREAD"].round(decimals=2)
# Adicionando % nos valores
# df['SPREAD'] = df['SPREAD'].astype(str) + '%'  VER SE IRÁ UTLIZAR

years = df["ANO"].unique()  # Anos unicos para o filtro
banks = df["NOME_BANCO"].unique()  # Bancos unicos para o filtro
quarters = df["TRIMESTRE"].unique()  # Trimestres unicos para o filtro

# Criando a aplicação Dash
app = Dash(__name__)

# Criando o Layout para o Dashboard
app.layout = html.Div([
    html.Div(
        [
            html.Img(src="assets/uce_logo.png", className="logo"),
            html.H1(
                "Movimentação de Câmbio",
                className="layout-title",
            ),
        ],  # Div Layout
        className="layout",
    ),
    html.Div([
        html.Div(
            [  # Div dos Dropdowns
                html.H2(
                    "Selecione o filtro desejado", className="title-dropdown"
                ),  # Titulo
                html.Label("Ano", className="dropdown-labels"),
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
                html.Label("Trimestre", className="dropdown-labels"),
                dcc.Dropdown(  # Filtro do Trimestre, retornando os 4 trimestres como padrão
                    id="quarter-dropdown",
                    options=[  # Valores unicos a filtrar
                        {"label": quarter, "value": quarter} for quarter in quarters
                    ],
                    value=["03", "06", "09", "12"],
                    multi=True,  # Permitindo selecionar mais que um valor
                    className="dropdown",
                    optionHeight=50,  # Altura das opções (Estetica)
                ),
                html.Label("Instituição Bancária",
                           className="dropdown-labels"),
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
            className="dropdown-container"
        ),
        html.Div(
            [dcc.Graph(id="operations-result-pieplot",
                       className="pieplot")],
            className="pieplot-container",
        )
    ],
        className='left-container'),
    html.Div(
        [  # Div do Grafico
            html.Div(
                [dcc.Graph(id="operations-result-lineplot",
                           className="lineplot")],
                className="lineplot-container",
            ),
            html.Div(
                [dcc.Graph(id="spread-lineplot",
                           className="spreadlineplot")],
                className="spreadlineplot-container",
            ),
            html.Div(
                [dcc.Graph(id="bar-lineplot",
                           className="bar-lineplot")],
                className="bar-lineplot-container",
            ),
        ],
        className="graph-container",
    ),
],
    className="main-container",
)


def filter_data(selected_year, selected_quarter, selected_bank, df=df):
    """
    Função de filtrar quais valores selecionados do dataframe
    """
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


def update_lineplot(filtered_df):
    """
    Função que cria um lineplot com os filtros selecionados
    """

    fig = px.line(  # Criando a figura de Visualização
        filtered_df,  # Dataframe filtrado pelo dropdown
        x="ANO-TRIMESTRE",  # Valor em X
        y="TOTAL_OP",  # Valor em y
        color="NOME_BANCO",  # Por qual coluna haverá diferenciação de cores
        labels={  # Nome das colunas na legenda
            "ANO-TRIMESTRE": "Ano e Trimestre",
            "TOTAL_OP": "Resultado das Operações",
        },
        title="Resultado das Operações",
        text=filtered_df['TOTAL_OP']/1000000,  # Titulo
        markers=True,  # Marcação nos pontos no gráfico
        symbol="NOME_BANCO",  # Por qual coluna haverá diferenciação no simbolo dos marcadores
        color_discrete_map=bank_colors,  # Paleta de cores pré-definidas para cada Banco
    )

    fig.update_traces(line=dict(width=1.8),
                      textposition="bottom right",
                      texttemplate="%{text:.2f}B")  # Atualizando o traço do LinePlot
    fig.update_layout(  # Estilizando a Visualização
        height=480,
        paper_bgcolor="white",  # Cor em volta do Plot
        # plot_bgcolor="#0D214F", # Cor no fundo do Plot
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


def update_pieplot(filtered_df):

    # Soma de todas as operações dos bancos filtrado
    total = filtered_df["TOTAL_N"].sum()
    # Somando todas as operações dos bancos filtrados
    por_banco = filtered_df.groupby("NOME_BANCO")["TOTAL_N"].sum()
    # Selecionando os bancos com operações menores a 5% do filtrado
    menor_5 = (por_banco / total) < 0.05
    # Dropando os bancos filtrados na linha acima
    maior_95 = filtered_df[filtered_df["NOME_BANCO"].isin(
        por_banco[~menor_5].index)]
    # Somando os bancos menores que % e adicionando como uma linha chamada 'Outros'
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
        com_outros,
        values="TOTAL_N",
        names="NOME_BANCO",
        title="Total de Operações",
        color="NOME_BANCO",
        color_discrete_map=bank_colors,
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        width=460,
        height=480,
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
    """
    Função que cria um lineplot do spread com os filtros selecionados
    """

    fig = px.line(  # Criando a figura de Visualização
        filtered_df,  # Dataframe filtrado pelo dropdown
        x="ANO-TRIMESTRE",  # Valor em X
        y="SPREAD",  # Valor em y
        color="NOME_BANCO",  # Por qual coluna haverá diferenciação de cores
        labels={  # Nome das colunas na legenda
            "ANO-TRIMESTRE": "Ano e Trimestre",
            "SPREAD": "Spread",
        },
        text="SPREAD",
        title="Spread Cambial (%)",  # Titulo
        markers=True,  # Marcação nos pontos no gráfico
        color_discrete_map=bank_colors,  # Paleta de cores pré-definidas para cada Banco
    )

    fig.update_traces(
        line=dict(width=1.8),
        textposition="bottom right",
        texttemplate="%{y}%"
        # hovertemplate='Banco:%{z}<br>Ano e Trimestre: %{x}<br>Spread: %{y}%'
    )  # Atualizando o traço do LinePlot

    fig.update_layout(  # Estilizando a Visualização
        height=480,
        paper_bgcolor="white",
        # Cor em volta do Plot
        # plot_bgcolor="#0D214F", # Cor no fundo do Plot
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
        showlegend=False,
        margin=dict(l=1, r=30, t=50, b=5),
        transition_duration=1000,  # Tempo de transição na atulização do gráfico
    )
    return fig


def update_bar_lineplot(filtered_df):
    """
    Função que cria um lineplot do spread com os filtros selecionados
    """
    bb = filtered_df[filtered_df['NOME_BANCO'] == 'BB']
    filtered_df = filtered_df.groupby('ANO-TRIMESTRE').sum().reset_index()
    filtered_df['NOME_BANCO'] = 'MERCADO'
    final_df = pd.concat([bb, filtered_df])
    final_df['TOTAL_N'] = final_df['TOTAL_N']/1000
    total = final_df['TOTAL_N'].sum()
    final_df['PORCENTAGEM'] = (
        final_df[final_df['NOME_BANCO'] == 'BB']['TOTAL_N'] / total) * 1000

    fig = px.bar(  # Criando a figura de Visualização
        final_df,  # Dataframe filtrado pelo dropdown
        x="ANO-TRIMESTRE",  # Valor em X
        y="TOTAL_N",  # Valor em y
        color="NOME_BANCO",
        barmode="group",  # Por qual coluna haverá diferenciação de cores
        labels={  # Nome das colunas na legenda
            "ANO-TRIMESTRE": "Ano e Trimestre",
            "TOTAL_N": "Resultado das Operações",
        },
        text="TOTAL_N",
        title="Resultado do BB relativo ao Mercado",  # Titulo
        # Marcação nos pontos no gráfico
        color_discrete_map=bank_colors,  # Paleta de cores pré-definidas para cada Banco
    )
    fig.update_traces(
        texttemplate="%{y}M"
    )

    fig.update_yaxes(secondary_y=False,
                     title_text='Resultado das Operações (em milhões)')

    fig.add_trace(
        go.Scatter(
            x=final_df['ANO-TRIMESTRE'], y=final_df['PORCENTAGEM'],
            mode='lines+markers+text', line_width=1.8, line_color='white', name='Relação BB em %',
            yaxis='y2', texttemplate="%{y:.2f}%", textfont=dict(
                family="BancoDoBrasil Textos",
                color='white'
            ), textposition='top center'

        ))

    fig.update_yaxes(title_text='Relação BB em %', secondary_y=True, title=dict(
        font=dict(
            size=16,  # Tamanho da fonte
            color="#0D214F",  # Cor da fonte
            family="BancoDoBrasil Textos",  # Familia da fonte
        ),
    ),)

  # Atualizando o traço do LinePlot

    fig.update_layout(  # Estilizando a Visualização
        height=480,
        paper_bgcolor="white",
        # Cor em volta do Plot
        # plot_bgcolor="#0D214F", # Cor no fundo do Plot
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
            title="Relação BB em %",
            title_font=dict(size=16,  # Tamanho da fonte
                            color="#0D214F",  # Cor da fonte
                            family="BancoDoBrasil Textos",),
            type='linear',
            linecolor='rgb(0,0,0)',
            linewidth=2,
            overlaying='y',
            side='right',
            range=[0, 50],
            
        ),
        margin=dict(l=1, r=30, t=50, b=5),
        transition_duration=1500,  # Tempo de transição na atulização do gráfico
    )
    return fig


@ app.callback(
    [Output("operations-result-lineplot", "figure"),
     Output("operations-result-pieplot", "figure"),
     Output("spread-lineplot", "figure"),
     Output('bar-lineplot', 'figure')],
    [  # Parametros de inputs (Ano, Trimestre e Banco)
        Input("year-dropdown", "value"),
        Input("quarter-dropdown", "value"),
        Input("bank-dropdown", "value"),
    ],
)
def update_plots(selected_year, selected_quarter, selected_bank):
    """
    Atualiza os valores para os gráficos
    """
    filtered_df = filter_data(selected_year, selected_quarter, selected_bank)

    line_plot = update_lineplot(filtered_df)
    pie_plot = update_pieplot(filtered_df)
    spread_line_plot = update_spread_lineplot(filtered_df)
    bar_lineplot = update_bar_lineplot(filtered_df)
    return line_plot, pie_plot, spread_line_plot, bar_lineplot
    # Retorna a figura


if __name__ == "__main__":  # Iniciando o o Dashboard
    app.run_server(debug=True)  # Ativando o debugmode
