from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from chatbot.utils.custom_prompt import CustomPrompt


class DocumentGrader:
    """
    Lớp kiểm tra xem các documents có liên quan tới câu đầu vào không.
    Output là string thuần ("yes" hoặc "no") nhờ StrOutputParser.
    """

    def __init__(self, llm) -> None:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CustomPrompt.GRADE_DOCUMENT_PROMPT),
                ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
            ]
        )
        self.chain = prompt | llm | StrOutputParser()

    def get_chain(self) -> RunnableSequence:
        return self.chain
