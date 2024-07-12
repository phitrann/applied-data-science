from langchain.callbacks import FileCallbackHandler
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from ollama import Client 
import os

os.environ["NO_PROXY"] = "172.16.87.75"

HTTP_PROXY = os.environ.get("HTTP_PROXY")

from retriever import (
    RAGException,
    create_parent_retriever,
    load_embedding_model,
    load_pdf,
    load_jsonl,
    load_reranker_model,
    retrieve_context,
)


class RAGClient:
    embedding_model = load_embedding_model()
    reranker_model = load_reranker_model()

    def __init__(self, files, model="mistral"):
        self.user_cv = load_pdf(files=files)
        self.docs = load_jsonl('/space/hotel/phit/personal/applied-data-science/data/preprocessed/preprocessed_vnw.jsonl')
        self.retriever = create_parent_retriever(self.docs, self.embedding_model)
        

        # llm = ChatOllama(model=model, base_url=HTTP_PROXY)
        # prompt_template = ChatPromptTemplate.from_template(
        #     (
        #         "Please answer the following question based on the provided `context` that follows the question.\n"
        #         "Think step by step before coming to answer. If you do not know the answer then just say 'I do not know'\n"
        #         "question: {question}\n"
        #         "context: ```{context}```\n"
        #     )
        # )
        # self.chain = prompt_template | llm | StrOutputParser()
        

    def stream(self, query: str, rulebase=False) -> dict:
        try:
            logger.info(self.user_cv)
            output = self.retrieve_context(self.user_cv[0].page_content)
            contexts, similarity_score = [out[0] for out in output], [out[1] for out in output]
            
            context = contexts[0].page_content
            for sim in similarity_score:
                if sim < 0.005:
                    context = "This context is not confident. " + context
        except RAGException as e:
            contexts, similarity_score = [e.args[0]], 0
        logger.info(len(contexts))
        # for r in self.chain.stream({"context": context, "question": query}):
        #     yield r
        
        # for context in contexts[:3]:
        #     for r in self.chain.stream({"context": context.page_content + self.user_cv[0].page_content, "question": query}):
        #         yield r
        
        for i, context in enumerate(contexts):
            yield {
                "image_url": "https://images.nightcafe.studio/jobs/entODB9RZWd9sm7F6mvz/entODB9RZWd9sm7F6mvz--1--kw649.jpg",
                "name": context.metadata.get("job_name", ""),
                "company_name": context.metadata.get("company_name", ""),
                "job_level": context.metadata.get("job_level", ""),
                "url": context.metadata.get("url", ""),
                "description": context.page_content,
                "salary": context.metadata.get("salary", ""),
                "job_description": context.metadata.get("job_description", ""),
                "similarity_score": similarity_score[i],
            }
        
    def retrieve_context(self, query: str):
        return retrieve_context(
            query, retriever=self.retriever, reranker_model=self.reranker_model
        )

    # def generate(self, query: str) -> dict:
    #     contexts = self.retrieve_context(query)

    #     return {
    #         "contexts": contexts,
    #         "response": self.chain.invoke(
    #             {"context": contexts[0][0].page_content, "question": query}
    #         ),
    #     }