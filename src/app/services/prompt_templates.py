from llama_index.core import PromptTemplate

QA_TEMPLATE = PromptTemplate(
    template=(
        "You are provided with relevant context information below. Please use this to help answer the question accurately. \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "Based on the context above, please answer the following question as clearly and precisely as possible: {query_str}\n"
        "If the information provided does not fully answer the question, respond with 'I don't know'."
    )
)

