from app.rbac.permissions import get_role_display_name


def build_rag_prompt(
    query: str,
    context_chunks: list[dict],
    role: str,
    chat_history: list[dict] | None = None,
) -> str:
    """
    Builds the final prompt sent to the LLM.

    Structure:
    1. System instruction
    2. Conversation history (NEW — gives LLM memory)
    3. Retrieved context (RAG documents)
    4. Current question
    """
    role_display = get_role_display_name(role)

    # Build context block from retrieved chunks
    context_block = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_block += f"""
[Document {i}]
Source: {chunk['source']}
Department: {chunk['department']}
Content: {chunk['content']}
---"""

    # Build conversation history block
    history_block = ""
    if chat_history:
        history_block = "\nCONVERSATION HISTORY:\n"
        for msg in chat_history[-6:]:  # last 6 messages = 3 exchanges
            role_label = "User" if msg["role"] == "user" else "Assistant"
            history_block += f"{role_label}: {msg['content']}\n"
        history_block += "\n"

    prompt = f"""You are a secure internal AI assistant for FoodChow.
You are currently serving a user with the role: {role_display}

STRICT RULES YOU MUST FOLLOW:
1. Answer ONLY using the information provided in the context below
2. You may use conversation history to understand follow-up questions
3. If the answer is not in the context, say exactly: "I could not find this information in the documents available to your role."
4. Never reveal information about other departments not shown in context
5. Always mention which document(s) you used to answer
6. Be precise and professional
{history_block}
CONTEXT FROM DOCUMENTS:
{context_block}

CURRENT QUESTION: {query}

Provide a clear, accurate answer based strictly on the context above.
At the end, list the source documents you used under "Sources:".
"""
    return prompt


def build_no_results_prompt(
    query: str,
    role: str,
    chat_history: list[dict] | None = None,
) -> str:
    """Prompt used when vector search returns zero results."""
    role_display = get_role_display_name(role)

    history_block = ""
    if chat_history:
        history_block = "\nCONVERSATION HISTORY:\n"
        for msg in chat_history[-6:]:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            history_block += f"{role_label}: {msg['content']}\n"
        history_block += "\n"

    prompt = f"""You are a secure internal AI assistant for FoodChow.
A user with role '{role_display}' asked: "{query}"
{history_block}
No relevant documents were found in the database for this query within their access level.

Respond politely that:
1. You could not find relevant information for their query
2. They may want to rephrase their question
3. If they believe they should have access, contact IT support
4. Keep response brief and professional
"""
    return prompt