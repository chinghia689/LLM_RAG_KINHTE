from langchain_core.prompts import ChatPromptTemplate  # noqa: I001
from pydantic import BaseModel, Field
from chatbot.utils.custom_prompt import CustomPrompt
from langchain_core.runnables import RunnableSequence


# Data model
class GradeDocumentModel(BaseModel):
    """Điểm nhị phân để kiểm tra mức độ liên quan trên các tài liệu được truy xuất."""

    binary_score: str = Field(description="Các tài liệu có liên quan đến câu hỏi., 'yes' or 'no'")


class DocumentGrader:
    """
    - Lớp kiểm tra xem các documents có liên quan tới câu đầu vào không-.\n
    """

    def __init__(self, llm) -> None:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CustomPrompt.GRADE_DOCUMENT_PROMPT),
                ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
            ]
        )
        self.chain = prompt | llm  # KHÔNG ép structured output

    def get_chain(self) -> RunnableSequence:
        return self.chain
