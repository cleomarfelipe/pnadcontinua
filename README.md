# pnadcontinua

**Descrição**

Essa biblioteca foi criada para facilitar a análise de microdados da PNAD Contínua, fornecendo uma interface simplificada para acessar, processar e baixar agregações desses dados.

## Índice
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Como Rodar](#como-rodar)
- [Como Utilizar](#como-utilizar)
- [Exemplos de Uso](#exemplos-de-uso)
- [Contribuições](#contribuições)

---

### Funcionalidades

- **Seleção Personalizada de Dados:** Permite ao usuário escolher quais variáveis e trimestres da PNAD Contínua deseja baixar e utilizar no sistema, facilitando o foco nas informações relevantes para a análise.
- **Obtenção Automática de Anos Disponíveis:** O programa realiza uma requisição ao site do IBGE para obter automaticamente a lista de anos disponíveis, garantindo acesso aos dados mais recentes.
- **Filtros Customizados:** Oferece a possibilidade de aplicar filtros nas colunas categóricas e numéricas antes de realizar agregações, o que ajuda a segmentar e preparar os dados com precisão.
- **Agrupamento Flexível:** Possibilita o agrupamento dos dados por uma quantidade ilimitada de colunas categóricas, fornecendo uma visão detalhada e personalizada da segmentação dos dados.
- **Contagem de Pessoas em Grupos:** Permite obter a quantidade de pessoas em cada grupo definido, proporcionando uma análise descritiva das distribuições populacionais nos grupos.
- **Cálculo de Médias por Grupo:** Possibilita obter a média de variáveis numéricas em cada grupo, como horas trabalhadas e rendimentos.
- **Cálculo de Somatórios por Grupo:** Permite calcular a soma de variáveis numéricas em cada grupo, como horas trabalhadas e rendimentos.
- **Deflacionamento de Rendimento:** Possibilita realizar o ajuste de variáveis relacionadas aos rendimentos habitual e efetivo, para corrigir os valores conforme a inflação.
- **Exportação de Agregações:** Permite baixar os dados agregados em formato CSV.
- **Ponderação de indivíduos:** Todos os resultados são calculados considerando o peso dos indivíduos da pesquisa, indicado na variável V1028.

### Instalação

Para instalar a biblioteca, execute o seguinte comando no terminal:

```bash
pip install pnadcontinua
```

### Como Rodar
Após a instalação, basta executar o seguinte comando para iniciar o programa:

```bash
pnadcontinua
```

### Como Utilizar

#### Tela Inicial

A tela inicial da interface gráfica oferece quatro opções principais:

- **Microdados:** Para baixar os microdados que serão utilizados pelo programa na computação das agregações.
- **Baixar Agregações:** Para selecionar os grupos, filtros e totais para gerar as agregações dos microdados.
- **Descrição de Variáveis:** Para acessar o código e a descrição de cada variável disponível na PNAD Contínua.
- **Tutorial:** Para exibir instruções sobre como acessar o tutorial da ferramenta (este README).

#### Primeiro Acesso: Baixar Microdados

Para o primeiro acesso, siga os passos abaixo na seção **Microdados**:

1. **Selecionar Variáveis:** Use os botões na parte superior para escolher as variáveis desejadas para análise. Por padrão, as variáveis **Ano**, **Trimestre**, **UF** e **V1028** (peso do indivíduo) já estão selecionadas e serão necessariamente baixadas. As opções de seleção de variáveis são:
   - **Tudo:** Exibe todas as variáveis disponíveis.
   - **Principais:** Exibe variáveis com código que começam com "VD", as quais derivam das respostas dos moradores.
   - **Trabalho:** Exibe variáveis relacionadas ao trabalho.
   - **Educação:** Exibe variáveis relacionadas à educação.

2. **Selecionar Trimestres:** Abaixo da seleção de variáveis, escolha os trimestres de interesse para a análise.

3. **Baixar Microdados:** Após definir as variáveis e trimestres, clique no botão **Baixar** para iniciar o download dos microdados. Este processo pode levar cerca de 1 hora e utilizar aproximadamente 1 GB de armazenamento ao baixar todas as variáveis e trimestres. Para acessos posteriores, o processo é significativamente mais rápido, pois será necessário selecionar apenas o trimestre referente à nova divulgação da PNAD Contínua, caso tenha sido lançada uma atualização.


#### Gerenciamento de Dados Baixados

Na parte inferior da página de **Microdados**, você encontra:

- **Informações dos Dados Baixados:** A interface exibe botões para acessar as variáveis e trimestres já baixados, além do total de armazenamento utilizado.
- **Apagar Dados Baixados:** Um botão para remover todos os dados baixados, caso necessário. **Atenção:** Se os dados forem apagados, será necessário baixá-los novamente para usar a ferramenta.

#### Página "Baixar Agregações"

Com os microdados baixados, acesse a página **Baixar Agregações** para definir os parâmetros de agregação. Nessa página, há três funcionalidades principais:

- **Selecionar Filtros**
- **Selecionar Grupos**
- **Selecionar Totais**

**1. Selecionar Filtros**  
Clicando em **Selecionar** na parte de filtros, uma nova janela é aberta com duas abas: **Variáveis categóricas** e **Variáveis numéricas**. Esses filtros são aplicados antes da computação das agregações.

   - **Variáveis categóricas:** Permite selecionar a variável e as categorias que devem ser filtradas dessa variável (por meio de checkboxes).
   - **Variáveis numéricas:** Permite selecionar a variável, a operação (como `>` ou `<`), e o valor. Para valores decimais, utilize ponto (ex.: `10.5`).

   - Para adicionar um filtro, clique no botão **Adicionar** na parte inferior. Para remover um filtro, clique no `X` à direita do filtro desejado. Após configurar os filtros, clique em **Voltar** para salvar.

**2. Selecionar Grupos**  
Clicando em **Selecionar Grupos**, uma página com checkboxes é exibida, onde o usuário pode selecionar as variáveis para agrupar os dados. Por padrão já estão selecionadas as variáveis "Ano" e "Trimestre", mas o usuário pode desmarcar essas opções caso não queira agrupar os resultados por essas variáveis.

**3. Selecionar Totais**  
O botão **Selecionar Totais** abre uma janela com duas abas:

   - **Contagem:** Permite incluir ou não a quantidade de pessoas em cada grupo selecionado.
   - **Soma e Média:** Permite calcular somas e médias de variáveis numéricas para cada grupo. Ao selecionar variáveis de rendimento Habitual ou Efetivo, uma opção adicional (checkbox) aparece para escolher se o valor deve ser deflacionado (o deflacionamento é feito a nível de indivíduo antes das agregações).

Para salvar a configuração dos totais, clique em **Voltar**.

#### Baixar o CSV de Agregações

Após configurar os filtros, grupos e totais, clique no botão **Baixar** na parte inferior da página para baixar o arquivo CSV com as agregações. No CSV resultante, as colunas com sufixo "def" indica que a variável foi deflacionada, o sufixo "media" indica que foi calculada a média da variável e o sufixo "soma" indica que foi calculada a soma da variável.

### Exemplos de Uso

Nestes exemplos, vamos assumir que as variáveis e trimestres de interesse já foram baixados.

#### Exemplo 1: Rendimento Médio e Quantidade de Pessoas Ocupadas por Sexo

Neste exemplo, vamos gerar um CSV contendo informações sobre as pessoas ocupadas, segmentadas por ano, trimestre e sexo, incluindo a média de uma variável de rendimento com e sem deflacionamento.

1. **Aplicar Filtro Categórico:**  
   Na parte de filtros, clique no botão **Selecionar**, abra a aba de **Variáveis Categóricas** e selecione a variável **VD4002**, e depois, na seleção dos valores, deixe marcado apenas o checkbox referente a **Pessoas ocupadas**.

2. **Selecionar Grupos:**  
   Na parte de agrupamentos, clique em **Selecionar** e selecione as variáveis **Ano**, **Trimestre** e **[V2007] Sexo**.

3. **Configurar Totais:**  
   - Na aba **Contagem** na seleção de totais, deixe a opção selecionada com **Incluir** para incluir a quantidade de pessoas em cada grupo.
   - Na aba **Soma e Média**, adicione duas agregações para a variável **VD4017**:
     - Uma agregação para a média de **VD4017** sem deflacionamento.
     - Uma agregação para a média de **VD4017** com deflacionamento.

4. **Baixar o CSV:**  
   Após configurar os filtros, grupos e totais, clique no botão **Baixar**. O resultado será um arquivo CSV com as seguintes colunas:
   - **Ano**
   - **Trimestre**
   - **V2007** (Sexo)
   - **VD4017_media** (média da variável de rendimento sem deflacionamento)
   - **VD4017_def_media** (média da variável de rendimento com deflacionamento)
   - **qnt_pessoas** (quantidade de pessoas em cada grupo)

#### Exemplo 2: Média de Horas Trabalhadas na Semana por Pessoas do Centro-Oeste

Neste exemplo, vamos calcular a média de horas trabalhadas pelas pessoas que residem na região Centro-Oeste do Brasil, segmentada por ano e trimestre.

1. **Aplicar Filtro Categórico:**  
   No botão **Selecionar** na parte de filtros, abra a aba de **Variáveis Categóricas** e selecione a variável **UF**. 
   - Marque apenas os estados de **Mato Grosso**, **Mato Grosso do Sul**, **Brasília** e **Goiás** para filtrar as pessoas que residem na região Centro-Oeste.

2. **Selecionar Grupos:**  
   Na parte de agrupamentos, clique **Selecionar** e selecione as variáveis **Ano** e **Trimestre**.

3. **Configurar Totais:**
  - Na aba **Contagem** na seleção de totais, deixe a opção selecionada com **Não incluir** para não incluir no CSV a quantidade de pessoas em cada grupo.
  - Na aba **Soma e Média**, adicione a agregação para calcular a média de **V4039** (horas trabalhadas).

4. **Baixar o CSV:**  
   Após configurar os filtros, grupos e totais, clique no botão **Baixar**. O resultado será um arquivo CSV com as seguintes colunas:
   - **Ano**
   - **Trimestre**
   - **V4039_media** (média das horas trabalhadas)

### Contribuições

Contribuições para o desenvolvimento e aprimoramento desta biblioteca são bem-vindas! Se você deseja ajudar, considere as seguintes formas de contribuir:

- **Relatar Problemas:** Caso encontre algum problema ou bug, por favor, abra um *issue* detalhado na página do projeto, descrevendo o comportamento esperado e o comportamento atual.
- **Enviar *Pull Requests*:** Se você deseja contribuir com o código, faça um *fork* do projeto, implemente a mudança em uma nova branch, e envie um *pull request*.
- **Melhorar a Documentação:** Se você perceber que alguma parte da documentação pode ser melhorada, sua ajuda é muito apreciada! Atualizações de documentação também podem ser enviadas via *pull requests*.

Agradecemos por contribuir para o desenvolvimento desta biblioteca e por ajudar a torná-la mais robusta e acessível a todos!
