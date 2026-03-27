from app.rbac.permissions import get_role_display_name


def build_rag_prompt(
    query: str,
    context_chunks: list[dict],
    role: str,
) -> str:
    """
    Builds the final prompt sent to the LLM.

    Structure:
    1. System instruction — tells LLM who it is and what rules to follow
    2. Context — the retrieved document chunks (the RAG part)
    3. Question — the user's actual query

    Why this structure?
    - System instruction sets strict boundaries (no hallucination)
    - Context gives the LLM real data to answer from
    - Question is always at the end so LLM focuses on it last
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

    prompt = f"""You are a secure internal AI assistant for FoodChow Technologies.
You are currently serving a user with the role: {role_display}

STRICT RULES YOU MUST FOLLOW:
1. Answer ONLY using the information provided in the context below
2. If the answer is not in the context, say exactly: "I could not find this information in the documents available to your role."
3. Never reveal information about other departments not shown in context
4. Always mention which document(s) you used to answer
5. Be precise and professional — this is a financial technology company

CONTEXT FROM DOCUMENTS:
{context_block}

USER QUESTION: {query}

Provide a clear, accurate answer based strictly on the context above. 
At the end, list the source documents you used under "Sources:".
"""
    return prompt


def build_no_results_prompt(query: str, role: str) -> str:
    """
    Prompt used when vector search returns zero results.
    This happens when no documents match the query + role filter.
    """
    role_display = get_role_display_name(role)

    prompt = f"""You are a secure internal AI assistant for FoodChow Technologies.
A user with role '{role_display}' asked: "{query}"

No relevant documents were found in the database for this query within their access level.

Respond politely that:
1. You could not find relevant information for their query
2. They may want to rephrase their question
3. If they believe they should have access, contact IT support
4. Keep response brief and professional
"""
    return prompt