# Olist Data Warehouse — Arquitetura Medallion

Projeto de estudo de Engenharia de Dados que transforma o dataset público de e-commerce da Olist em um Data Warehouse no PostgreSQL. O processamento é organizado nas camadas **Bronze, Silver e Gold**, utilizando Python, pandas, Parquet e SQL.

> **Objetivo:** praticar ingestão, armazenamento em camadas, exploração e qualidade de dados, transformações, modelagem dimensional e consultas analíticas orientadas a perguntas de negócio.
>
> Este é um projeto educacional executado localmente. Não é uma arquitetura de produção e não utiliza orquestrador, processamento distribuído ou cargas incrementais.

---

## 1. Visão geral

O projeto utiliza os nove arquivos CSV do [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Os dados representam pedidos realizados entre setembro de 2016 e outubro de 2018.

O pipeline organiza os dados em três camadas:

```text
CSV (data/raw)
      |
      v
BRONZE — leitura dos CSVs e gravação em Parquet
      |
      v
SILVER — tipagem, padronização, agregações e validações
      |
      v
GOLD — dimensões e fatos carregados no PostgreSQL
      |
      v
Consultas SQL para responder perguntas de negócio
```

Os resultados apresentados neste repositório descrevem exclusivamente o dataset histórico utilizado. Eles não representam a operação atual da Olist.

## 2. Perguntas de negócio

O modelo dimensional foi desenvolvido para apoiar três análises:

1. **Receita e ticket médio por categoria e ano:** quanto foi vendido em cada categoria e qual foi a receita média por pedido que continha itens daquela categoria?
2. **Pedidos e frete por estado do cliente:** quantos pedidos foram realizados em cada estado e qual foi o valor total e médio do frete?
3. **Desempenho de entrega por vendedor:** qual é o tempo médio de entrega, o percentual de entregas no prazo e a nota média das avaliações associadas aos pedidos de cada vendedor?

A terceira análise possui também uma consulta complementar que compara as avaliações de pedidos entregues no prazo e fora do prazo, contando cada `order_id` uma única vez.

---

## 3. Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| Python 3.14 | Linguagem utilizada nos scripts do pipeline |
| pandas | Leitura, exploração e transformação dos dados |
| PyArrow / Parquet | Armazenamento intermediário em formato colunar |
| PostgreSQL 18 | Banco de dados do Data Warehouse |
| SQL | Criação do esquema dimensional e consultas analíticas |
| psycopg2 | Conexão entre Python e PostgreSQL |
| python-dotenv | Leitura das configurações armazenadas no `.env` |
| Git / GitHub | Versionamento do projeto |

As dependências Python estão declaradas em `requirements.txt`. O pacote `python-dotenv` é necessário porque os scripts da camada Gold utilizam `load_dotenv()` e deve estar incluído nesse arquivo.

---

## 4. Estrutura do projeto

```text
olist-dw-medallion/
├── data/
│   ├── raw/                         # CSVs originais (não versionados)
│   ├── bronze/                      # Parquet da Bronze (gerado; não versionado)
│   └── silver/                      # Parquet da Silver (gerado; não versionado)
├── src/
│   ├── bronze/
│   │   └── bronze.py                # CSV -> Parquet
│   ├── silver/
│   │   ├── explorar_*.py             # Exploração dos dados
│   │   ├── transform_*.py            # Transformações individuais
│   │   └── validar_silver.py         # Verificações de integridade
│   └── gold/
│       ├── testar_conexao.py         # Teste de conexão com PostgreSQL
│       ├── criar_tabelas.py          # Execução do DDL da Gold
│       ├── carregar_dimensoes.py     # Carga das dimensões
│       └── carregar_fatos.py         # Carga das tabelas de fatos
├── sql/
│   ├── criar_tabelas.sql             # DDL do modelo dimensional
│   └── perguntas_de_negocio.sql      # Consultas analíticas
├── docs/                             # Espaço reservado para documentação adicional
├── .env.example                      # Modelo das variáveis de conexão
├── .gitignore
├── requirements.txt
└── README.md
```

Os arquivos CSV e os Parquets são gerados localmente e não precisam ser enviados ao GitHub. O `.gitignore` exclui `data/raw`, `data/bronze`, `data/silver`, o ambiente virtual e o arquivo `.env`.

---

## 5. Camadas do pipeline

### 5.1 Bronze — dados de origem em Parquet

Arquivo principal: `src/bronze/bronze.py`.

O script percorre os nove nomes de arquivos definidos na lista `tabelas`, lê cada CSV com `pandas.read_csv(..., dtype=str)` e grava um arquivo Parquet correspondente em `data/bronze`.

```python
for tabela in tabelas:
    df = pd.read_csv(f"data/raw/{tabela}.csv", dtype=str)
    df.to_parquet(f"data/bronze/{tabela}.parquet", index=False)
```

A intenção é manter as colunas como texto na primeira camada e deixar a conversão explícita de tipos para a Silver. Isso ajuda a evitar inferências automáticas inadequadas, por exemplo, tratar prefixos de CEP como números e perder zeros à esquerda.

**Observação sobre fidelidade:** o `read_csv()` utiliza o reconhecimento padrão de valores ausentes do pandas. Portanto, campos vazios ou tokens reconhecidos como nulos podem ser representados como valores ausentes no DataFrame. A Bronze mantém as colunas como texto, mas não é uma cópia byte a byte dos CSVs originais.

### 5.2 Silver — tipagem, padronização e qualidade

A Silver lê os Parquets da Bronze, aplica transformações específicas por tabela e grava os resultados em `data/silver`.

Principais transformações implementadas:

| Conjunto de dados | Transformação |
|---|---|
| Customers | Padronização do prefixo de CEP com cinco caracteres (`zfill(5)`) |
| Sellers | Padronização do prefixo de CEP com cinco caracteres (`zfill(5)`) |
| Orders | Conversão das colunas de data para `datetime` |
| Order items | Conversão de identificador do item para inteiro, data para `datetime` e preço/frete para decimal em ponto flutuante |
| Order payments | Conversão de sequência e parcelas para inteiro e valor do pagamento para ponto flutuante |
| Order reviews | Conversão da nota para inteiro e das datas para `datetime` |
| Products | Conversão das colunas numéricas para ponto flutuante |
| Geolocation | Conversão de latitude/longitude para ponto flutuante e agregação por prefixo de CEP |
| Category translation | Regravação do arquivo em Parquet, mantendo os valores de origem |

#### Agregação da geolocalização

A tabela original de geolocalização possui 1.000.163 registros e 19.015 prefixos de CEP distintos. O script `transform_geolocation.py` agrupa os registros por CEP e calcula a média de latitude e longitude, mantendo o primeiro valor encontrado para cidade e estado.

Essa agregação reduz a tabela para uma linha por prefixo de CEP e evita que um relacionamento com clientes ou vendedores multiplique registros por causa de várias coordenadas associadas ao mesmo CEP.

A média das coordenadas é uma aproximação geográfica do CEP, não a localização exata de cada cliente ou vendedor. Os campos de cidade e estado dessa tabela agregada não são usados para substituir os dados cadastrais de clientes no modelo Gold.

#### Validação da Silver

O script `src/silver/validar_silver.py` verifica, entre outros pontos:

- unicidade de identificadores principais, como `customer_id`, `seller_id`, `product_id` e `order_id`;
- unicidade dos prefixos de CEP após a agregação da geolocalização;
- ausência de duplicidade nas chaves compostas de itens e pagamentos;
- existência das referências entre pedidos, clientes, itens, produtos, vendedores, pagamentos e avaliações.

As verificações atuais utilizam `assert`. Elas são úteis para a validação deste projeto, mas podem ser desativadas quando o Python é executado com otimizações (`python -O`). Em uma evolução do pipeline, essas verificações podem ser substituídas por validações explícitas que levantem exceções com mensagens descritivas.

### 5.3 Gold — Data Warehouse no PostgreSQL

A Gold transforma os dados tratados em um modelo dimensional do tipo **esquema estrela**, com quatro dimensões e duas tabelas de fatos.

As chaves substitutas (`*_key`) são geradas pelo PostgreSQL por meio de colunas `SERIAL`. Os valores monetários são armazenados como `DECIMAL(10, 2)`.

#### Dimensões

| Tabela | Granularidade | Principais atributos |
|---|---|---|
| `dim_produto` | Um registro por produto | `product_id`, categoria em português e inglês |
| `dim_cliente` | Um registro por `customer_id` | CEP, cidade, estado, latitude e longitude |
| `dim_vendedor` | Um registro por vendedor | `seller_id` |
| `dim_data` | Um registro por dia | Data completa, dia, mês, ano e dia da semana |

A `dim_cliente` utiliza os dados cadastrais de cidade e estado da tabela de clientes e associa latitude/longitude por meio do prefixo de CEP. Quando não há correspondência na geolocalização, as coordenadas permanecem nulas.

A `dim_data` é criada para todos os dias entre a menor e a maior data de compra identificadas nos pedidos.

#### Tabelas de fatos

| Tabela | Granularidade | Medidas e atributos principais |
|---|---|---|
| `fato_pedidos_itens` | Um registro por item de pedido (`order_id` + `order_item_id`) | Status, preço, frete e chaves das dimensões de produto, cliente, vendedor e data |
| `fato_pedidos` | Um registro por combinação de pedido e vendedor (`order_id` + vendedor) | Status, tempo de entrega, indicador de entrega no prazo e nota da avaliação |

**Atenção à granularidade de `fato_pedidos`:** um mesmo pedido pode possuir itens de mais de um vendedor. Nesses casos, o pedido aparece uma vez para cada vendedor associado. Essa granularidade é intencional para permitir análises por vendedor, mas exige cuidado em consultas gerais: para contar pedidos únicos, agrupe ou utilize `COUNT(DISTINCT order_id)`.

A nota da avaliação pertence ao pedido, não ao item. Por isso, ela é armazenada em `fato_pedidos`, e não repetida em cada linha de `fato_pedidos_itens`. Quando existe mais de uma avaliação para o mesmo pedido, o carregamento seleciona a mais recente de acordo com `review_answer_timestamp`.

---

## 6. Resultados e análises

Os resultados abaixo foram calculados a partir do dataset público utilizado no projeto. Eles não devem ser interpretados como indicadores atuais da empresa.

### 6.1 Pedidos e frete por estado do cliente

Pedidos com status `canceled` e `unavailable` ficam fora desta consulta. Os cinco estados com maior quantidade de pedidos são:

| Estado | Pedidos distintos | Frete total (R$) | Frete médio por pedido (R$) |
|---|---:|---:|---:|
| SP | 41.125 | 714.264,84 | 17,37 |
| RJ | 12.697 | 304.044,14 | 23,95 |
| MG | 11.496 | 269.566,23 | 23,45 |
| RS | 5.415 | 134.730,81 | 24,88 |
| PR | 4.982 | 117.313,55 | 23,55 |

O frete médio por pedido varia de R$ 17,37 em SP a aproximadamente R$ 49,10 em RR. A consulta soma o frete dos itens e divide pelo número de pedidos distintos de cada estado.

### 6.2 Avaliação por prazo de entrega — pedidos únicos

Como `fato_pedidos` possui uma linha por pedido-vendedor, a comparação geral por prazo precisa consolidar cada `order_id` uma única vez. Com essa consolidação, os resultados são:

| Entrega no prazo | Pedidos distintos | Nota média |
|---|---:|---:|
| Não | 6.534 | 2,27 |
| Sim | 89.936 | 4,29 |

No conjunto analisado, pedidos entregues fora do prazo apresentam nota média inferior à dos pedidos entregues no prazo. Isso indica uma associação nos dados, mas não demonstra, por si só, que o atraso causou a avaliação mais baixa.


A consulta complementar consolida as linhas por `order_id` antes de agrupar por prazo. Como as linhas de um mesmo pedido repetem o mesmo indicador de prazo e a mesma nota para cada vendedor associado, o `SELECT DISTINCT` deixa uma única linha por pedido:

```sql
WITH pedidos_unicos AS (
    SELECT DISTINCT
        order_id,
        entregue_no_prazo,
        review_score
    FROM fato_pedidos
    WHERE entregue_no_prazo IS NOT NULL
)
SELECT
    entregue_no_prazo,
    COUNT(*) AS pedidos,
    ROUND(AVG(review_score), 2) AS nota_media
FROM pedidos_unicos
GROUP BY entregue_no_prazo
ORDER BY entregue_no_prazo;
```

---

## 7. Achados de qualidade de dados

Durante a exploração e validação, foram identificadas as seguintes características no conjunto de dados:

- 8 pedidos com status `delivered` sem data de entrega ao cliente;
- 775 pedidos sem itens associados;
- 610 produtos sem categoria informada;
- 2 produtos com pelo menos uma dimensão física ausente;
- 789 identificadores `review_id` associados a mais de um pedido; considerando as linhas repetidas além da primeira ocorrência, há 814 ocorrências duplicadas de `review_id`;
- 9 pagamentos com valor igual a zero e 3 pagamentos com tipo `not_defined`;
- 278 clientes com prefixo de CEP sem correspondência na tabela de geolocalização;
- 1.278 pedidos (aproximadamente 1,3% dos pedidos com itens) associados a mais de um vendedor.

Esses casos não foram tratados como se fossem necessariamente erros que deveriam ser removidos. As decisões foram tomadas conforme a finalidade da análise: por exemplo, produtos sem categoria recebem o rótulo `sem_categoria`, enquanto coordenadas ausentes permanecem nulas.

### Limitações conhecidas dos dados e do modelo

- `customer_id` identifica o registro de cliente associado ao pedido, não necessariamente uma pessoa única ao longo de todo o dataset. `customer_unique_id` é o identificador usado para relacionar a mesma pessoa entre diferentes registros e não foi incluído no modelo Gold.
- 775 pedidos sem itens não entram nas tabelas de fatos, pois a construção de `fato_pedidos` parte das combinações de pedido e vendedor presentes em `order_items`.
- Pedidos associados a mais de um vendedor geram uma linha por vendedor em `fato_pedidos`. Para indicadores globais por pedido, é necessário consolidar por `order_id`.
- Quando há avaliações repetidas para um pedido, é selecionada a avaliação mais recente por `review_answer_timestamp`.
- As coordenadas da dimensão cliente são médias por prefixo de CEP. Elas são aproximadas e não representam o endereço exato do cliente.
- A inspeção das coordenadas agregadas identificou 11 prefixos com valores fora de limites geográficos aproximados do Brasil; esses casos podem exigir curadoria caso sejam utilizados em mapas ou análises espaciais.
- 610 produtos sem categoria são classificados como `sem_categoria`. Quando não existe tradução para inglês, o nome original da categoria é utilizado como fallback.
- A tabela de pagamentos e o texto das avaliações são tratados e mantidos na Silver, mas não entram diretamente nas tabelas de fatos da Gold.

---

## 8. Como executar o projeto

### 8.1 Pré-requisitos

- Python 3.14;
- PostgreSQL 18 instalado e em execução;
- acesso aos nove arquivos CSV do dataset Olist;
- Git, caso queira clonar o repositório.

### 8.2 Obter os dados

Baixe o [Brazilian E-Commerce Public Dataset by Olist no Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) e coloque os nove CSVs em `data/raw/`:

```text
data/raw/
├── olist_customers_dataset.csv
├── olist_geolocation_dataset.csv
├── olist_orders_dataset.csv
├── olist_order_items_dataset.csv
├── olist_order_payments_dataset.csv
├── olist_order_reviews_dataset.csv
├── olist_products_dataset.csv
├── olist_sellers_dataset.csv
└── product_category_name_translation.csv
```

Os arquivos de dados não são versionados neste repositório. As pastas `data/bronze` e `data/silver` recebem arquivos gerados durante a execução.

### 8.3 Criar e ativar o ambiente virtual

Execute os comandos a partir da raiz do projeto.

No Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 8.4 Configurar o PostgreSQL

1. Crie um banco de dados chamado `olist_dw` no PostgreSQL.
2. Copie `.env.example` para um arquivo chamado `.env`.
3. Preencha as variáveis com os dados da sua instância local:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=olist_dw
DB_USER=postgres
DB_PASSWORD=sua_senha_local
```

O arquivo `.env` contém credenciais e não deve ser enviado ao GitHub. O repositório mantém apenas `.env.example`, sem senha real.

### 8.5 Executar o pipeline

Execute os comandos abaixo **a partir da raiz do projeto**, na ordem apresentada.

**1. Bronze**

```bash
python src/bronze/bronze.py
```

**2. Transformações Silver**

No Windows PowerShell:

```powershell
Get-ChildItem src\silver\transform_*.py | ForEach-Object { python $_.FullName }
```

No Linux/macOS:

```bash
for arquivo in src/silver/transform_*.py; do
    python "$arquivo"
done
```

**3. Validar a Silver**

```bash
python src/silver/validar_silver.py
```

**4. Testar a conexão com PostgreSQL**

```bash
python src/gold/testar_conexao.py
```

**5. Criar as tabelas da Gold**

```bash
python src/gold/criar_tabelas.py
```

**6. Carregar as dimensões**

```bash
python src/gold/carregar_dimensoes.py
```

**7. Carregar as tabelas de fatos**

```bash
python src/gold/carregar_fatos.py
```

**8. Executar as consultas analíticas**

Abra `sql/perguntas_de_negocio.sql` no pgAdmin ou execute o arquivo pelo `psql` conectado ao banco `olist_dw`.

### 8.6 Atenção ao comportamento de recarga

O script `sql/criar_tabelas.sql` começa com comandos `DROP TABLE IF EXISTS` e recria o esquema. Portanto, executá-lo remove as tabelas existentes e seus dados.

O script `carregar_dimensoes.py` utiliza `TRUNCATE ... RESTART IDENTITY CASCADE` nas dimensões; por causa das chaves estrangeiras, as tabelas de fatos dependentes também podem ser truncadas. Em seguida, `carregar_fatos.py` limpa e recarrega as tabelas de fatos.

O pipeline implementa uma **carga completa**, não incremental. Execute os scripts na ordem indicada e somente em um banco destinado a este projeto.

---

## 9. Decisões de projeto

- **Bronze com colunas textuais:** evita inferência automática prematura de tipos. A conversão é feita explicitamente na Silver.
- **Geolocalização agregada por CEP:** calcula uma coordenada média para reduzir várias linhas por CEP a uma linha e evitar multiplicação de registros em relacionamentos.
- **Dois fatos com granularidades diferentes:** a fato de itens representa um item de pedido; a fato de pedidos representa um pedido por vendedor. A separação evita misturar atributos de item e de pedido, como a nota da avaliação.
- **Chaves substitutas nas dimensões:** cada dimensão utiliza uma chave técnica gerada pelo PostgreSQL, mantendo também o identificador de origem como coluna única.
- **Categoria ausente:** produtos sem categoria recebem `sem_categoria`, para que continuem disponíveis nas análises.
- **Valores ausentes:** datas, coordenadas e atributos sem informação não são inventados; permanecem nulos quando aplicável.
- **Avaliação mais recente:** quando há mais de uma avaliação associada a um pedido, é selecionada a última resposta registrada.

---

## 10. Limitações e próximos passos

Este projeto foi desenvolvido para aprendizado e possui limitações conhecidas:

- execução manual dos scripts, sem orquestrador;
- ausência de testes automatizados dedicados; a validação atual está concentrada em `validar_silver.py`;
- carga completa da Gold, sem processamento incremental;
- execução em um único computador, sem teste de escalabilidade;
- ausência de monitoramento, alertas e logging estruturado do pipeline;
- dependência de uma instância PostgreSQL configurada localmente;
- ausência de uma camada de visualização/BI neste escopo.

Possíveis evoluções incluem adicionar testes automatizados, substituir `assert` por validações explícitas, implementar uma rotina única de orquestração, adicionar cargas incrementais e construir uma camada de visualização com uma ferramenta de BI.

---

## 11. Autor

**Gabriel Ferrari**  
Estudante de Engenharia de Software — UNIMAR  
GitHub: [gabriel-ferrari7](https://github.com/gabriel-ferrari7)  
LinkedIn: [gabriel-ferrari7](https://www.linkedin.com/in/gabriel-ferrari7/)
