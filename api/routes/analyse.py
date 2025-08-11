"""
Analyse API endpoints for analysing the documents
"""

# Got all the necessary information and understanding about AI agents and tools from this video:
# https://www.youtube.com/watch?v=bTMPwUgLZf0

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool

# Elevenlabs imports
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os
from fastapi.responses import StreamingResponse
import io


router = APIRouter()


class AnalyzeRequest(BaseModel):
    document_content: str


@router.post(
    "/api/analyse",
    response_description="Start async analyse of the document",
    response_model=dict,
    tags=["Analyse"],
)
async def analyse_document(request: AnalyzeRequest):
    """
    Start async LLM analysis of the document content using job-based processing.
    """
    if not request.document_content:
        raise HTTPException(
            status_code=400,
            detail="the document content must be provided for the analysis",
        )

    # TODO: Implement actual analysis logic here
    load_dotenv()

    class ResearchResponse(BaseModel):
        topic: str
        summary: str
        sources: list[str]
        tools_used: list[str]

    llm = ChatOpenAI(model="gpt-4o-mini")
    parser = PydanticOutputParser(pydantic_object=ResearchResponse)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are an assistant designed to help people who have difficulty reading or understanding documents and images, especially if they don’t understand the language. Your task is to:
                1. Carefully analyze the content of the picture or document provided.
                2. Summarize the main information in simple, clear language.
                3. Identify if there is any danger, warning, or something that seems wrong or suspicious.
                4. Explain clearly what the user should do or be aware of regarding the content.
                5. Use easy-to-understand words suitable for people who struggle to read or understand the original language.

                Wrap the output in this format and provide no other text \n{format_instructions}
                """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{query}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    tools = [search_tool, wiki_tool, save_tool]

    agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Update the query to fit our purpose
    raw_response = agent_executor.invoke(
        {"query": "What is the capital of France? and save the result to a file"}
    )

    structured_response = parser.parse(raw_response.get("output"))

    # ##### Practice elevenlabs ###################### #

    elevenlabs = ElevenLabs(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
    )

    audio = elevenlabs.text_to_speech.convert(
        text="The first move is what sets everything in motion.",
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    # Convert generator to bytes
    audio_bytes = b"".join(audio)

    # play(audio)

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=speech.mp3"},
    )
