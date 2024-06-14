import os

from typing import List, Optional, Union

from langchain.callbacks import FileCallbackHandler
from langchain.retrievers import ContextualCompressionRetriever, ParentDocumentRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader, JSONLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS , Chroma
# from langchain_chroma import Chroma
from langchain_core.documents import Document
from loguru import logger
from rich import print
from sentence_transformers import CrossEncoder


from unstructured.cleaners.core import clean_extra_whitespace, group_broken_paragraphs

logfile = "log/output.log"
logger.add(logfile, colorize=True, enqueue=True)
handler = FileCallbackHandler(logfile)


persist_directory = None


VIETNAMWORKS = ['_id', 'url', 'job_name', 'company_name', 'salary', 'end_date',
       'address', 'posted_date', 'job_function', 'job_industry', 'job_level',
       'skill', 'preferred_language', 'job_description'] # job_requirements

TOPCV = ['_id', 'urls', 'job_name', 'company_name', 'address', 'salary',
       'remaining', 'job_description', 'benefits',
       'application_method', 'level', 'experience', 'number_of_recruitment',
       'work_form', 'gender', 'working_time'] # job_requirements

class RAGException(Exception):
    """
    Custom exception class for RAG (Retriever, Answerer, Generator) module.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def load_pdf(
    files: Union[str, List[str]] = "../data/cv/Bui Tien Phat resume (1).pdf"
) -> List[Document]:
    """
    Load PDF files and return a list of Document objects.

    Args:
        files (Union[str, List[str]], optional): Path(s) to the PDF file(s) to be loaded. Defaults to "../data/cv/Bui Tien Phat resume (1).pdf".

    Returns:
        List[Document]: A list of Document objects representing the loaded PDF files.
    """
    if isinstance(files, str):
        loader = UnstructuredFileLoader(
            files,
            post_processors=[clean_extra_whitespace, group_broken_paragraphs],
        )
        return loader.load()

    loaders = [
        UnstructuredFileLoader(
            file,
            post_processors=[clean_extra_whitespace, group_broken_paragraphs],
        )
        for file in files
    ]
    docs = []
    for loader in loaders:
        docs.extend(
            loader.load(),
        )
    return docs


# Define the metadata extraction function.
def metadata_func(record: dict, metadata: dict) -> dict:
    """
    Process the record dictionary and update the metadata dictionary with the relevant values.

    Args:
        record (dict): The record dictionary containing the data to be processed.
        metadata (dict): The metadata dictionary to be updated.

    Returns:
        dict: The updated metadata dictionary.
    """
    
    # metadata["urls"] = record.get("urls")
    # metadata["job_name"] = record.get("job_name")
    # metadata["company_name"] = record.get("company_name")
    # metadata["address"] = record.get("address")
    # metadata["salary"] = record.get("salary")
    # metadata["remaining"] = record.get("remaining")
    # # metadata[""] = record.get("Mô tả công việc")
    # metadata["Yêu cầu ứng viên"] = record.get("Yêu cầu ứng viên")
    # metadata["Quyền lợi"] = record.get("Quyền lợi")
    # metadata["Địa điểm làm việc"] = record.get("Địa điểm làm việc")
    # metadata["Cách thức ứng tuyển"] = record.get("Cách thức ứng tuyển")
    # metadata["Cấp bậc"] = record.get("Cấp bậc")
    # metadata["Kinh nghiệm"] = record.get("Kinh nghiệm")
    # metadata["Số lượng tuyển"] = record.get("Số lượng tuyển")
    # metadata["Hình thức làm việc"] = record.get("Hình thức làm việc")
    # metadata["Giới tính"] = record.get("Giới tính")
    
    for key in VIETNAMWORKS:
        metadata[key] = record.get(key)
    
    metadata = {key: f'{" ".join(val[0]) if isinstance(val, list) else val}' for key, val in metadata.items()}

    

    return metadata


def load_jsonl(
    files: Union[str, List[str]] = "../data/crawl/train_test.jsonl"
) -> List[Document]:
    """
    Load JSONL files and return a list of documents.

    Args:
        files (Union[str, List[str]], optional): Path or list of paths to the JSONL files. 
            Defaults to "../data/crawl/train_test.jsonl".

    Returns:
        List[Document]: A list of Document objects.

    """
    if isinstance(files, str):
        loader = JSONLoader(
            files,
            json_lines=True,
            jq_schema='.',
            content_key="job_requirements", 
            text_content=False,
            metadata_func=metadata_func
        )
        return loader.load()

    loaders = [
        JSONLoader(
            file,
            json_lines=True,
            jq_schema='.messages[]',
            content_key="content",
            metadata_func=metadata_func
        )
        for file in files
    ]
    docs = []
    for loader in loaders:
        docs.extend(
            loader.load(),
        )
    return docs

def rerank_docs(reranker_model, query, retrieved_docs):
    """
    Reranks the retrieved documents based on a given reranker model and query.

    Args:
        reranker_model: The reranker model used for scoring the documents.
        query: The query used for reranking the documents.
        retrieved_docs: A list of retrieved documents.

    Returns:
        A list of tuples containing the retrieved documents and their corresponding scores,
        sorted in descending order of scores.
    """
    query_and_docs = [(query, r.page_content) for r in retrieved_docs]
    scores = reranker_model.predict(query_and_docs)
    return sorted(list(zip(retrieved_docs, scores)), key=lambda x: x[1], reverse=True)

def create_parent_retriever(
    docs: List[Document], embeddings_model: HuggingFaceBgeEmbeddings()
):
    """
    Creates a parent document retriever using the given list of documents and embeddings model.

    Args:
        docs (List[Document]): A list of documents to be added to the retriever.
        embeddings_model (HuggingFaceBgeEmbeddings): The embeddings model to be used for indexing.

    Returns:
        ParentDocumentRetriever: The created parent document retriever.

    """
    parent_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n\n", "\n\n"],
        chunk_size=2000,
        length_function=len,
        is_separator_regex=False,
    )

    # This text splitter is used to create the child documents
    child_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n\n", "\n\n"],
        chunk_size=500,#1000,
        chunk_overlap=150,#300,
        length_function=len,
        is_separator_regex=False,
    )
    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(
        collection_name="split_documents",
        embedding_function=embeddings_model,
        persist_directory=persist_directory,
    )#.as_retriever()
    
    print("vectorstore: ", vectorstore)
    # The storage layer for the parent documents
    store = InMemoryStore()
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
        k=10,
    )
    retriever.add_documents(docs)
    return retriever


def retrieve_context(query, retriever, reranker_model):
    """
    Retrieves relevant documents based on the given query using a retriever and reranks them using a reranker model.

    Args:
        query (str): The query to retrieve relevant documents for.
        retriever: The retriever object used to retrieve relevant documents.
        reranker_model: The reranker model used to rerank the retrieved documents.

    Returns:
        list: A list of reranked documents.

    Raises:
        RAGException: If no relevant documents are retrieved with the given query.
    """
    retrieved_docs = retriever.get_relevant_documents(query)

    if len(retrieved_docs) == 0:
        raise RAGException(
            f"Couldn't retrieve any relevant document with the query `{query}`. Try modifying your question!"
        )
    reranked_docs = rerank_docs(
        query=query, retrieved_docs=retrieved_docs, reranker_model=reranker_model
    )
    return reranked_docs

# https://github.com/FlagOpen/FlagEmbedding/tree/master/FlagEmbedding/BGE_M3
def load_embedding_model(
    model_name: str = "BAAI/bge-large-en-v1.5", device: str = "cuda"
) -> HuggingFaceBgeEmbeddings:
    """
    Load the embedding model for text encoding.

    Args:
        model_name (str): The name of the pre-trained model to load. Defaults to "BAAI/bge-large-en-v1.5".
        device (str): The device to use for model inference. Defaults to "cuda".

    Returns:
        HuggingFaceBgeEmbeddings: The loaded embedding model.

    """
    model_kwargs = {"device": device}
    encode_kwargs = {
        "normalize_embeddings": True
    }  # set True to compute cosine similarity
    embedding_model = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    return embedding_model

# https://github.com/FlagOpen/FlagEmbedding/tree/master/FlagEmbedding/llm_reranker
def load_reranker_model(
    reranker_model_name: str = "BAAI/bge-reranker-large", device: str = "cuda"
) -> CrossEncoder:
    """
    Loads a reranker model for ranking search results.

    Args:
        reranker_model_name (str): The name or path of the reranker model to be loaded.
        device (str): The device to be used for running the model (default: "cuda").

    Returns:
        CrossEncoder: The loaded reranker model.
    """
    reranker_model = CrossEncoder(
        model_name=reranker_model_name, max_length=512, device=device, 
    )
    return reranker_model


# def main(
#     file: str = "../data/crawl/train_test.jsonl",
#     query: Optional[str] = None,
#     llm_name="mistral",
# ):
#     # docs = load_pdf(files=file)
#     docs = load_jsonl("../data/crawl/vnw.jsonl")
#     # print(docs)

#     embedding_model = load_embedding_model()
#     retriever = create_parent_retriever(docs, embedding_model)
#     reranker_model = load_reranker_model()

#     context = retrieve_context(
#         query, retriever=retriever, reranker_model=reranker_model
#     )[0]
#     print("context:\n", context, "\n", "=" * 50, "\n")


# if __name__ == "__main__":
#     # from jsonargparse import CLI

#     # CLI(main)
#     # main(query="What is the job description for Network Engineer?")
#     main(query="What is job description in Da Nang ?")
    