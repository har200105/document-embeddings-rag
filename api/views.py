from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from .helpers import (prepare_success_response, prepare_failure_response, Errors,extract_text_from_file)
import uuid
import logging
import asyncio
from asgiref.sync import sync_to_async
import httpx
import json
from langchain.vectorstores import FAISS
from .models import (Chat,Conversation,Document,)
from .serializers import (AssetsSerializer,ChatDetailSerializer,)
from .tasks import (generate_document_embeddings,)
from django.http import StreamingHttpResponse
from .embeddings import (DocumentEmbedding,)
from .constants import (ASSET_DIR,OLLAMA_GENERATE_MODEL,OLLAMA_GENERATE_URL,)


logger = logging.getLogger(__name__)




@api_view(['POST'])
@parser_classes([MultiPartParser])
def process_document(request):
    try:
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return prepare_failure_response(Errors.SOMETHING_WENT_WRONG)

        text = extract_text_from_file(uploaded_file)
        if not text:
            return prepare_failure_response(Errors.SOMETHING_WENT_WRONG)

        asset_id = str(uuid.uuid4())
        
        Document.objects.create(
            asset_id=asset_id,
            file_name=uploaded_file.name,
            processed=False 
        )

        generate_document_embeddings.delay(asset_id, text)

        return prepare_success_response({"asset_id": asset_id})
    except Exception as e:
        logger.error(f"Something went wrong : {str(e)}")
        return prepare_failure_response(Errors.SOMETHING_WENT_WRONG, {str(e)})


@api_view(['GET'])
def get_all_asset_ids(request):
    
    try:
        
        assets = Document.objects.all()
        serializer = AssetsSerializer(assets,many=True)
        return prepare_success_response({"assets": serializer.data})

    except Exception as e:
        logger.error(f"Something went wrong : {str(e)}")
        return prepare_failure_response(Errors.SOMETHING_WENT_WRONG, f"Something went wrong: {str(e)}")
    

@api_view(['POST'])
def start_chat(request):
    try:
        asset_id = request.data.get('asset_id')
        if not asset_id:
            return prepare_failure_response("Asset ID is required")

        document = Document.objects.filter(asset_id=asset_id).first()
        if not document or not document.processed:
            return prepare_failure_response(Errors.OBJECT_NOT_FOUND,"Asset not found or not processed yet")

        chat = Chat.objects.create(asset=document)

        response_data = {"chat_id": str(chat.chat_id)}
        return prepare_success_response(response_data)

    except Exception as e:
        logger.error(f"Something went wrong : {str(e)}")
        return prepare_failure_response(Errors.SOMETHING_WENT_WRONG, f"Something went wrong: {str(e)}")




async def async_stream_llm_response(prompt: str):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", OLLAMA_GENERATE_URL, json={
                "model": OLLAMA_GENERATE_MODEL,
                "prompt": prompt,
                "stream": True
            }) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            content = data.get("response", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        yield "[ERROR: LLM stream failed]"


@api_view(['GET', 'POST'])
def chat_message(request):
    try:
        if request.method == 'GET':
            chat_id = request.GET.get("chat_id")
            user_query = request.GET.get("user_query")
        else: 
            chat_id = request.data.get("chat_id")
            user_query = request.data.get("user_query")

        if not chat_id or not user_query:
            return prepare_failure_response(Errors.SOMETHING_WENT_WRONG, "chat_id and user_query are required.")

        chat = Chat.objects.filter(chat_id=chat_id, is_active=True).first()
        if not chat:
            return prepare_failure_response(Errors.OBJECT_NOT_FOUND, "Chat not found.")

        asset_id = chat.asset.asset_id
        faiss_index_path = f"{ASSET_DIR}/{asset_id}"

        vector_store = FAISS.load_local(
            faiss_index_path, DocumentEmbedding(), allow_dangerous_deserialization=True
        )

        relevant_docs = vector_store.similarity_search(user_query, k=5)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        prompt = f"""You are a helpful assistant. Use the context below to answer the user's question.

                Context:
                {context}

                User Question:
                {user_query}

                Answer:"""

        def response_stream():
            async def gather_response():
                answer = ""
                async for token in async_stream_llm_response(prompt):
                    answer += token
                    yield token
                await sync_to_async(Conversation.objects.create)(
                    chat=chat, user_query=user_query, bot_response=answer
                )

            async def consume_and_yield():
                async for chunk in gather_response():
                    yield chunk

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async_gen = consume_and_yield()

            try:
                while True:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    yield chunk
            except StopAsyncIteration:
                pass
            finally:
                loop.close()

        response = StreamingHttpResponse(response_stream(), content_type="text/event-stream")
        response['X-Accel-Buffering'] = 'no'
        response['Cache-Control'] = 'no-cache'
        return response

    except Exception as e:
        logger.error(f"Something went wrong : {str(e)}")
        return prepare_failure_response(Errors.SOMETHING_WENT_WRONG, f"Something went wrong: {str(e)}")

    

@api_view(['GET'])
def chat_history(request):
    try:
        chats = Chat.objects.filter(is_active=True)
        serializer = ChatDetailSerializer(chats,many=True)
        return prepare_success_response({"chats":serializer.data})
    except Exception as e:
        logger.error(f"Something went wrong : {str(e)}")
        return prepare_failure_response(Errors.SOMETHING_WENT_WRONG, f"Something went wrong: {str(e)}")
    

@api_view(['GET'])
def chat_history_by_id(request,id):
    try:
        try:
            chat = Chat.objects.get(chat_id=id,is_active=True)
        except Exception as e:
            return prepare_failure_response(Errors.OBJECT_NOT_FOUND,"Chat with given id not found")
        serializer = ChatDetailSerializer(chat)
        return prepare_success_response({"chat":serializer.data})
    except Exception as e:
        logger.error(f"Something went wrong : {str(e)}")
        return prepare_failure_response(Errors.SOMETHING_WENT_WRONG, f"Something went wrong: {str(e)}")