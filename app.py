from dash import dcc, html, Input, Output, Dash  # Importação das bibliotecas utilizadas
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

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
    "ITAU": "#140083",
    "BRADESCO": "#CC092F",
    "SANTANDER": "#8B0000",
}
# Criando o dicionário de substituições
quarter_replace = {1: "03", 2: "06", 3: "09", 4: "12"}

# aplicando a substituição na coluna TRIMESTRE
df["TRIMESTRE"] = df["TRIMESTRE"].replace(quarter_replace)

# 'Somando' o Ano - Trimestre para uma unica coluna
df["ANO-TRIMESTRE"] = df.apply(lambda x: str(x["ANO"]) + "-" + x["TRIMESTRE"], axis=1)

# Formatando os valores para o tipo Date
df["ANO-TRIMESTRE"] = pd.to_datetime(df["ANO-TRIMESTRE"], format="%Y-%m")

# Criando a coluna total resultado (despesas + lucro)
df["TOTAL_OP"] = df.apply(lambda x: int(x["RESULT_OP"]) + x["DESPESA_OP"], axis=1)
df["TOTAL_N"] = df.apply(lambda x: int(x["NUMERO_OP"]) + x["NUMERO_INTERBANK"], axis=1)
years = df["ANO"].unique()  # Anos unicos para o filtro
banks = df["NOME_BANCO"].unique()  # Bancos unicos para o filtro
quarters = df["TRIMESTRE"].unique()  # Trimestres unicos para o filtro

# Criando a aplicação Dash
app = Dash(__name__)

# Criando o Layout para o Dashboard
app.layout = html.Div(
    [
        html.Div(  # Div dos Dropdowns
            [
                html.H1("Dashboard Test", className="title"), # Titulo
                html.Label("Ano", className="dropdown-labels"),
                dcc.Dropdown(  # Filtro do Ano, retornando os 4 trimestres como padrão
                    id="year-dropdown",
                    options=[  # Valores unicos a filtrar
                        {"label": year, "value": year} for year in years
                    ],
                    value=years,  # Valores iniciais
                    multi=True,  # Permitindo selecionar mais que um valor
                    className="dropdown",
                    style=dict(color="black"),
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
                html.Label("Instituição Bancária", className="dropdown-labels"),
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
        html.Div(
            [  # Div do Grafico
                html.Div(
                    [dcc.Graph(id="operations-result-lineplot", className="lineplot")],
                    className="lineplot-container",
                ),
                html.Div(
                    [dcc.Graph(id="operations-result-pieplot", className="pieplot")],
                    className="pieplot-container",
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
            "ANO-TRIMESTRE": "Trimestre e Ano",
            "TOTAL_OP": "Resultado das Operações",
        },
        title="Resultado das Operações por Banco e Trimestre",  # Titulo
        markers=True,  # Marcação nos pontos no gráfico
        symbol="NOME_BANCO",  # Por qual coluna haverá diferenciação no simbolo dos marcadores
        color_discrete_map=bank_colors,  # Paleta de cores pré-definidas para cada Banco
    )

    fig.update_traces(line=dict(width=1.8))  # Atualizando o traço do LinePlot
    fig.update_layout(  # Estilizando a Visualização
        paper_bgcolor="white",  # Cor em volta do Plot
        # plot_bgcolor="#0D214F", # Cor no fundo do Plot
        title=dict(  # Titulo
            font=dict(
                size=20,  # Tamanho da fonte
                color="#0D214F",  # Cor da fonte
                family="Arial",  # Familia da fonte
            ),
            x=0.46,  # Posição no eixo X
            y=.95,  # Posição no eixo y
        ),
        xaxis=dict(  # Valor em X
            title=dict(
                font=dict(
                    size=14,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="Arial",  # Familia da fonte
                ),
            )
        ),
        yaxis=dict(
            title=dict(
                font=dict(
                    size=14,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="Arial",  # Familia da fonte
                ),
            )
        ),
        legend=dict(
            font=dict(  # Fonte da Legenda
                size=11,  # Tamanho da fonte
                color="#0D214F",  # Cor da fonte
                family="Arial",  # Familia da fonte
            ),
            title=dict(  # Titulo da Legenda
                text="INSTITUIÇÕES BANCÁRIAS",  # String
                font=dict(  # Fonte do Titulo da Leganda
                    size=13,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="Arial",  # Familia da fonte
                ),
            ),
        ),
        margin=dict(l=1, r=1, t=50, b=5),
        transition_duration=1000,  # Tempo de transição na atulização do gráfico
    )
    return fig


def update_pieplot(filtered_df):
    fig = px.pie(
        filtered_df,
        values="TOTAL_N",
        names="NOME_BANCO",
        title="Participação do Banco em (%) no periodo",
        color="NOME_BANCO",
        color_discrete_map=bank_colors,
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(  # Estilizando a Visualização
        paper_bgcolor="white",  # Cor em volta do Plot
        # plot_bgcolor="#0D214F", # Cor no fundo do Plot
        title=dict(  # Titulo
            font=dict(
                size=20,  # Tamanho da fonte
                color="#0D214F",  # Cor da fonte
                family="Arial",  # Familia da fonte
            ),
            x=0.46,  # Posição no eixo X
            y=0.95,  # Posição no eixo y
        ),
        xaxis=dict(  # Valor em X
            title=dict(
                font=dict(
                    size=14,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="Arial",  # Familia da fonte
                ),
            )
        ),
        yaxis=dict(
            title=dict(
                font=dict(
                    size=14,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="Arial",  # Familia da fonte
                ),
            )
        ),
        legend=dict(
            font=dict(  # Fonte da Legenda
                size=11,  # Tamanho da fonte
                color="#0D214F",  # Cor da fonte
                family="Arial",  # Familia da fonte
            ),
            title=dict(  # Titulo da Legenda
                text="INSTITUIÇÕES BANCÁRIAS",  # String
                font=dict(  # Fonte do Titulo da Leganda
                    size=13,  # Tamanho da fonte
                    color="#0D214F",  # Cor da fonte
                    family="Arial",  # Familia da fonte
                ),
            ),
        ),
        transition = dict(duration = 1500),  # Tempo de transição na atulização do gráfico
    )
    return fig


@app.callback(
    Output("operations-result-lineplot", "figure"),
    Output("operations-result-pieplot", "figure"),
    # Output("operations-interbank-primary-barplot", "figure"),
    # Output da figure
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
    return line_plot, pie_plot
    # Retorna a figura


if __name__ == "__main__":  # Iniciando o o Dashboard
    app.run_server(debug=True)  # Ativando o debugmode
