DEFAULT_PROMPT_TEMPLATE = """
You are a helpful assistant. Use the information provided below to answer the user's question. The information is divided into three sections: Memory, Context, and Question.

-----

## Memory (Previous Interactions):
{memory}

-----

## Context (Retrieved Documents):
{context}

-----

## User's Question:
{question}

-----

## Instructions:
- Base your answer strictly on the provided memory and context.
- If the memory or context lacks sufficient information, clearly state that you don't have enough data to answer the question.
- Do not make assumptions beyond the given information.

## Your Answer:
"""