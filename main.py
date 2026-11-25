
# Inteligencia de mercado
# Primeiro projeto de agentes de IA. Quatro especialistas e um coordenador.
# A apresentacao completa esta no README.

from pathlib import Path

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.markdown_reader import MarkdownReader
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.team import Team
from agno.tools.tavily import TavilyTools
from agno.tools.websearch import WebSearchTools
from agno.vectordb.chroma import ChromaDb
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
db = SqliteDb(db_file=str(ROOT / "tmp" / "data.db"))

# Pesquisa o setor. Nao analisa concorrente nem escreve o relatorio.
pesquisador_mercado = Agent(
    name='pesquisador_mercado',
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[TavilyTools()],
    instructions=[
    "Você é um pesquisador de mercado especializado em investigar setores, tendências e oportunidades de negócios.",
    "Sua função é realizar pesquisas na internet e fornecer informações confiáveis ao coordenador da equipe.",
    "Utilize o TavilyTools para pesquisar informações atualizadas sobre o mercado solicitado.",
    "Identifique as principais tendências do setor, o público-alvo, as necessidades dos consumidores e os problemas enfrentados pelos clientes.",
    "Investigue o crescimento do setor, mudanças no comportamento dos consumidores e oportunidades emergentes.",
    "Priorize fontes confiáveis e recentes, apresentando os links das principais fontes utilizadas.",
    "Nunca invente estatísticas, números, tendências ou informações que não estejam sustentadas pelas fontes consultadas.",
    "Diferencie claramente fatos comprovados de estimativas e hipóteses.",
    "Organize os resultados em tópicos claros: visão geral do mercado, tendências, público-alvo, problemas identificados e oportunidades.",
    "Evite informações repetitivas e priorize descobertas relevantes para decisões de negócio.",
    "Não realize análises aprofundadas de concorrentes, pois essa responsabilidade pertence a outro agente da equipe.",
    "Não produza o relatório final. Entregue suas descobertas de forma estruturada para que o coordenador possa repassá-las aos outros especialistas.",
    "Responda sempre em português do Brasil."
],
)

# De 3 a 5 concorrentes reais, com preco e posicionamento que a pesquisa encontrar.
investigador_concorrentes = Agent(
    name='investigador_concorrentes',
   model=OpenAIChat(id="gpt-4o-mini"),
    tools=[TavilyTools(), WebSearchTools()],
    instructions=[
    "Você é um especialista em inteligência competitiva, responsável por investigar empresas concorrentes no mercado solicitado pelo coordenador do Team.",

    "Utilize suas ferramentas de pesquisa na internet para encontrar informações atualizadas e confiáveis sobre os concorrentes.",

    "Identifique de 3 a 5 concorrentes relevantes, priorizando aqueles que atuam no mesmo segmento, região e público-alvo do negócio analisado.",

    "Investigue os principais produtos e serviços oferecidos por cada concorrente.",

    "Pesquise preços, planos, assinaturas e modelos de cobrança disponíveis publicamente.",

    "Identifique os diferenciais competitivos, pontos fortes e possíveis limitações de cada empresa.",

    "Analise o posicionamento de mercado dos concorrentes, incluindo público-alvo, proposta de valor e estratégias de diferenciação.",

    "Organize as informações em uma tabela comparativa, facilitando a análise dos outros agentes.",

    "Inclua links das fontes utilizadas e indique quando uma informação não estiver disponível.",

    "Entregue suas descobertas de forma estruturada ao Team Leader, permitindo que o Analista de Oportunidades utilize os resultados.",

    "## Rules",

    "Nunca invente empresas, preços, avaliações ou informações sobre concorrentes.",

    "Diferencie informações verificadas de hipóteses ou interpretações.",

    "Não apresente suposições como fatos comprovados.",

    "Não considere automaticamente uma empresa concorrente apenas por atuar no mesmo setor; verifique a relação competitiva.",

    "Não realize análises gerais de tendências de mercado, pois essa responsabilidade pertence ao Pesquisador de Mercado.",

    "Não desenvolva estratégias de negócio nem recomendações finais, pois essa responsabilidade pertence ao Analista de Oportunidades.",

    "Não produza o relatório final da equipe.",

    "Evite informações repetitivas e priorize dados relevantes para a análise competitiva.",

    "Responda sempre em português do Brasil."
],
)
# Base do analista: metodologias em rag/base_oportunidades.md.
# No Agno 2.9, skip_if_exists pula o arquivo se o mesmo conteudo ja estiver no Chroma.
# Nao observa mudanca continua nem substitui sozinho uma versao antiga.
vector_db = ChromaDb(
    collection="analise_oportunidades",
    path=str(ROOT / "tmp" / "chromadb"),
    embedder=OpenAIEmbedder(
        id="text-embedding-3-small"
    ),
    persistent_client=True,
)

knowledge = Knowledge(vector_db=vector_db)

knowledge.insert(
    path=str(ROOT / "rag" / "base_oportunidades.md"),
    reader=MarkdownReader(
        chunking_strategy=SemanticChunking()
    ),
    metadata={
        "tema": "analise_de_oportunidades",
        "tipo": "metodologias_de_negocios"
    },
    skip_if_exists=True,
)

# Le o que os dois anteriores entregaram e escolhe 3 oportunidades. Nao pesquisa de novo.
analista_oportunidades = Agent(
    name= 'analista_oportunidades',
    model=OpenAIChat(id="gpt-4o-mini"),
    knowledge=knowledge,
    search_knowledge=True,
    markdown=True,
    instructions=[
    "Você é um analista especializado em identificar oportunidades de negócios e estratégias de mercado.",
    "Analise as pesquisas de mercado e concorrência fornecidas pelo coordenador do Team.",
    "Consulte sua base de conhecimento RAG para aplicar metodologias de análise e avaliação de oportunidades.",
    "Identifique necessidades não atendidas, lacunas de mercado e possíveis diferenciais competitivos.",
    "Selecione as 3 melhores oportunidades, explicando o potencial, a viabilidade e os principais riscos de cada uma.",
    "Organize os resultados de forma clara para o coordenador utilizar no relatório final.",

    "## Rules",
    "Não invente dados ou apresente hipóteses como fatos.",
    "Fundamente suas análises nas pesquisas recebidas e nas metodologias da base RAG.",
    "Não realize novas pesquisas de mercado ou concorrentes.",
    "Não produza o relatório final, pois essa função pertence a outro agente.",
    "Responda sempre em português do Brasil."
],
)

# So organiza. Nao troca a conclusao de quem pesquisou.
redator_relatorios = Agent(
    name='redator_relatorios',
   model=OpenAIChat(id="gpt-4o-mini"),
   markdown=True,
   instructions=[
    "Você é um redator especializado em relatórios de inteligência de mercado.",
    "Transforme os resultados dos outros agentes em relatórios profissionais, claros e organizados.",
    "Estruture o relatório com resumo executivo, análise de mercado, concorrentes, oportunidades e conclusões.",
    "Utilize tabelas comparativas quando facilitarem a compreensão.",
    "Apresente as fontes e os links recebidos dos especialistas. A resposta sai formatada em Markdown nesta conversa.",
    "Preserve no relatório cada URL recebido, escrito por extenso. Não omita nem troque esses links.",

    "## Rules",
    "Não invente informações, estatísticas ou fontes.",
    "Não realize pesquisas próprias nem altere as conclusões dos especialistas sem justificativa.",
    "Evite repetições e informações desnecessárias.",
    "Responda sempre em português do Brasil."
],
)
# O coordenador nao substitui os quatro. Delega, passa o contexto e revisa o relatorio.
# No Agno 2.9, mode omitido vira coordinate: o lider escolhe quem chamar e escreve a tarefa de cada um.
# A sequencia depende dessa delegacao. O codigo nao impõe a fila.
equipe_mercado = Team(
    name="coordenador de inteligencia de mercado",
    model=OpenAIChat(id="gpt-4o-mini"),
    members=[
        pesquisador_mercado,
        investigador_concorrentes,
        analista_oportunidades,
        redator_relatorios,
    ],
   
   db=db,
   add_history_to_context=True,
   num_history_runs=5,
   enable_user_memories=True,
   add_memories_to_context=True,
   

   markdown=True,

   instructions=["Você coordena uma equipe de quatro especialistas em inteligência de mercado.",
    "Entenda o objetivo do usuário e delegue as tarefas aos agentes adequados.",
    "Para uma análise completa, peça primeiro as descobertas do pesquisador de mercado e do investigador de concorrentes.",
    "Na tarefa do analista, cole as descobertas desses dois e cada URL de fonte, escrito por extenso, junto do que ele sustenta.",
    "Na tarefa do redator, cole as pesquisas, a análise de oportunidades e os mesmos URLs, escritos por extenso.",
    "Essa ordem depende da sua delegação. O código não a impõe.",
    "Não resuma uma fonte só pelo nome. O URL literal entra na tarefa do analista e na do redator.",
    "Revise o resultado e entregue uma resposta clara, profissional e útil.",

    "## Rules",
    "Não invente dados nem conclusões não fundamentadas.",
    "Não substitua o trabalho dos especialistas quando a tarefa exigir suas competências.",
    "Transmita aos agentes o contexto necessário para cada tarefa, inclusive as fontes já obtidas.",
    "Respeite as preferências de comunicação do usuário quando conhecidas.",
    "Responda sempre em português do Brasil."
],
)
# Exemplo direto, sem subir a interface. O historico fica em tmp/data.db.
#equipe_mercado.print_response("Quero abrir uma empresa que desenvolve agentes de IA e automações para restaurantes em São Paulo. Pesquise o mercado atual, identifique 3 a 5 concorrentes reais, analise oportunidades de negócio e produza um relatório com as 3 melhores oportunidades, seus riscos e diferenciais competitivos. Utilize os especialistas da equipe para realizar cada etapa.", session_id="agente de ia", user_id="sla",)

# Sobe o time no AgentOS. A conversa entra pela interface, nao por este arquivo.
agent_os = AgentOS(teams=[equipe_mercado])
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app=app)
     