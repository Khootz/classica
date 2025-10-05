"""
Multi-Query RAG System
Decomposes complex questions into sub-queries, retrieves context for each,
and synthesizes comprehensive answers with citations
"""

import json
from typing import List, Dict, Any
from services import gemini_client, pathway_rag

async def decompose_query(user_question: str) -> List[str]:
    """
    Use Gemini to break down complex question into specific sub-queries
    """
    prompt = f"""You are a financial analyst assistant. Break down this question into 3-5 specific sub-questions that would help answer it comprehensively for M&A due diligence.

User Question: {user_question}

Requirements:
- Each sub-question should focus on a specific aspect (financial, operational, risk, etc.)
- Sub-questions should be self-contained and specific
- Return ONLY a JSON array of strings, nothing else
- Example format: ["What is the revenue trend?", "What are the key risks?"]

Sub-questions:"""

    try:
        response = gemini_client.ask_gemini([{
            "role": "user",
            "content": prompt
        }])
        
        # Clean response and parse JSON
        response_text = response.strip()
        if response_text.startswith("```"):
            # Remove code blocks if present
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        sub_queries = json.loads(response_text)
        
        # Validate it's a list
        if not isinstance(sub_queries, list):
            return [user_question]  # Fallback to original
        
        return sub_queries[:5]  # Limit to 5 max
        
    except Exception as e:
        print(f"⚠️ Query decomposition failed: {e}")
        return [user_question]  # Fallback to original question


async def multi_query_rag(user_question: str, task_id: str, structured_data: dict = None, metrics: dict = None, insights: list = None) -> Dict[str, Any]:
    """
    Multi-query RAG pipeline:
    1. Decompose question into sub-queries
    2. Retrieve context for each sub-query
    3. Synthesize comprehensive answer with all citations
    
    Args:
        user_question: Original user question
        task_id: Task ID for document retrieval
        structured_data: Extracted financial fields (optional)
        metrics: Computed financial metrics (optional)
        insights: Generated insights (optional)
    
    Returns:
        dict with answer, sub_queries, citations, reasoning
    """
    
    # Step 1: Decompose into sub-queries
    print(f"🔍 Decomposing query: {user_question}")
    sub_queries = await decompose_query(user_question)
    print(f"📋 Generated {len(sub_queries)} sub-queries: {sub_queries}")
    
    # Step 2: Retrieve context for each sub-query
    all_contexts = []
    all_citations = []
    seen_sources = set()
    
    for idx, sub_q in enumerate(sub_queries):
        try:
            rag_result = pathway_rag.get_rag_context(task_id, sub_q)
            
            context_text = rag_result.get("context", "")
            sources = rag_result.get("sources", [])
            
            if context_text:
                all_contexts.append({
                    "sub_query": sub_q,
                    "context": context_text,
                    "index": idx + 1
                })
            
            # Collect unique citations
            for source in sources:
                source_key = f"{source['filename']}_{source.get('chunk_index', '')}"
                if source_key not in seen_sources:
                    all_citations.append({
                        "document": source["filename"],
                        "page": f"Chunk {source.get('chunk_index', 0)}",
                        "sub_query": sub_q,
                        "sub_query_index": idx + 1
                    })
                    seen_sources.add(source_key)
            
            print(f"✅ Sub-query {idx+1}: Found {len(sources)} sources")
            
        except Exception as e:
            print(f"⚠️ RAG failed for sub-query '{sub_q}': {e}")
            continue
    
    # If no contexts found, add placeholder
    if not all_contexts:
        all_contexts = [{"sub_query": "No relevant documents", "context": "No relevant excerpts found.", "index": 0}]
    
    # Step 3: Build comprehensive synthesis prompt
    contexts_formatted = "\n\n".join([
        f"[Sub-Question {ctx['index']}]: {ctx['sub_query']}\n{ctx['context']}"
        for ctx in all_contexts
    ])
    
    structured_section = ""
    if structured_data:
        structured_section = f"\n\nStructured Financial Data:\n{json.dumps(structured_data, indent=2)}"
    
    metrics_section = ""
    if metrics:
        metrics_section = f"\n\nComputed Metrics:\n{json.dumps(metrics, indent=2)}"
    
    insights_section = ""
    if insights and any(i for i in insights if i):
        insights_section = f"\n\nKey Insights:\n{json.dumps(insights, indent=2)}"
    
    synthesis_prompt = f"""You are a financial analyst. Answer the user's question comprehensively using all the provided context.

ORIGINAL QUESTION: {user_question}

ANALYSIS FROM MULTIPLE PERSPECTIVES:
{contexts_formatted}
{structured_section}
{metrics_section}
{insights_section}

REQUIREMENTS:
1. Synthesize a comprehensive answer that addresses all aspects
2. Reference specific documents naturally (e.g., "According to the 10-Q report..." or "The financial statements show...")
3. Use plain text ONLY - NO markdown, asterisks, hashtags, or special formatting
4. Be concise but thorough
5. If data conflicts, acknowledge it
6. If information is missing, state it clearly

COMPREHENSIVE ANSWER:"""
    
    # Step 4: Generate final synthesis
    try:
        final_answer = gemini_client.ask_gemini([{
            "role": "user",
            "content": synthesis_prompt
        }])
    except Exception as e:
        print(f"❌ Synthesis failed: {e}")
        final_answer = "Unable to generate comprehensive answer. Please try again."
    
    # Step 5: Return complete result
    return {
        "answer": final_answer,
        "sub_queries": sub_queries,
        "citations": all_citations,
        "reasoning": [f"Analyzed: {sq}" for sq in sub_queries],
        "num_sub_queries": len(sub_queries),
        "num_citations": len(all_citations)
    }
