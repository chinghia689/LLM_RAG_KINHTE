from chatbot.utils.llm import LLM
from ingestion.retriever import Retriever
from chatbot.utils.document_grader import DocumentGrader
from chatbot.utils.answer_generator import AnswerGenerator
from chatbot.utils.no_answer_handler import NoAnswerHandler
from langgraph.graph import END, StateGraph, START
from chatbot.utils.graph_state import GraphState
from typing import Dict, Any
import os
from api.config import settings


class ChatAgent:
    def __init__(self, path_vector_store) -> None:
        # Lớp khởi tạo embedding_model và lấy documents
        self.retriever = Retriever(settings.LLM_NAME).set_retriever(path_vector_store)
        #  Lớp khởi tạo LLM
        self.llm = LLM().get_llm(settings.LLM_NAME)
        #  Lớp kiểm tra xem các documents có liên quan tới câu đầu vào không
        self.document_grader = DocumentGrader(self.llm)
        # Lớp tạo câu trả lời từ câu đầu vào
        self.answer_generator = AnswerGenerator(self.llm)
        # Lớp trả về yêu cầu người dùng nhập lại câu đâu vào
        self.no_answer_handler = NoAnswerHandler(self.llm)

    def retrieve(self, state: GraphState) -> Dict[str, Any]:
        """
        Nhận vào câu hỏi, trả về danh sách văn bản (documents) và câu đầu vào (question).
        Args:
            state (GraphState): _description_

        Returns:
            Dict[str, Any]: _description_
        """
        question = state["question"]
        # Retrieval
        documents = self.retriever.get_documents(
            question, int(settings.NUM_DOC)
        )  # os.environ["NUM_DOC"]
        return {"documents": documents, "question": question}

    def grade_documents(self, state: GraphState) -> Dict[str, Any]:
        """
        Nhận vào danh sách văn bản và câu hỏi danh giá xem danh sách văn bản có phù hợp không.\n
        Trả lời dạng yes or no.\n
        Tạo mới 1 ["documents"] trong GraphState .\n
        Nếu yes thì add data vào ["documents"] .\n

        Args:
            state (GraphState): _description_

        Returns:
            Dict[str, Any]: _description_
        """
        question = state["question"]
        documents = state["documents"]

        # Score each doc
        filtered_docs = []
        for d in documents:
            score = self.document_grader.get_chain().invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score.binary_score
            if grade == "yes":
                print("---GRADE: TÀI LIỆU LIÊN QUAN---")
                filtered_docs.append(d)
            else:
                print("---GRADE: TÀI LIỆU KHÔNG LIÊN QUAN---")
                continue
        return {"documents": filtered_docs, "question": question}

    def decide_to_generate(self, state: GraphState) -> str:
        """
        Kiểm tra xem ["documents"] mới được tạo trong GraphState từ hàm grade_documents có tồn tại không.\n
        Nếu tồn tại thì đến hàm tạo câu hỏi từ từ câu hỏi đầu vào và  ["documents"] mới đã được check.\n

        Args:
            state (GraphState): _description_

        Returns:
            str: _description_
        """
        filtered_documents = state["documents"]

        if not filtered_documents:
            print(
                "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
            )
            return "no_document"
        else:
            print("---DECISION: GENERATE---")
            return "generate"

    def handle_no_answer(self, state: GraphState) -> Dict[str, Any]:
        """
        Đây là hàm nếu tìm ko thấy documents trong GraphState
        Trả về yêu cầu người dùng nhập lại câu hỏi.
        Args:
            state (GraphState): _description_

        Returns:
            Dict[str, Any]: _description_
        """
        question = state["question"]
        # Post-processing
        generation = self.no_answer_handler.get_chain().invoke({"question": question})
        return {"generation": generation}

    def generate(self, state: GraphState) -> Dict[str, Any]:
        """
        Tạo câu tra lời từ question đầu vào và documents đã được kiểm duyệt

        Args:
            state (GraphState): _description_

        Returns:
            Dict[str, Any]: _description_
        """
        question = state["question"]
        documents = state["documents"]
        # Post-processing
        context = "\n\n".join(doc.page_content for doc in documents)
        generation = self.answer_generator.get_chain().invoke(
            {"question": question, "context": context}
        )
        return {"generation": generation}

    def get_workflow(self):
        workflow = StateGraph(GraphState)

        # Define the nodes
        workflow.add_node("retrieve", self.retrieve)  # retrieve
        # grade documents
        workflow.add_node("grade_documents", self.grade_documents)
        workflow.add_node("generate", self.generate)  # generate
        # no_answer_handler
        workflow.add_node("handle_no_answer", self.handle_no_answer)

        # Build graph
        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "grade_documents")

        workflow.add_conditional_edges(
            "grade_documents",
            self.decide_to_generate,
            {
                "no_document": "handle_no_answer",
                "generate": "generate",
            },
        )

        workflow.add_edge("generate", END)
        workflow.add_edge("handle_no_answer", END)

        return workflow
