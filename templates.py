templates = {
    "theorem":"""
You are an expert mathematician. Extract all mathematical theorems, lemmas, propositions, and corollaries from the text below.

Return ONLY a valid JSON object in this exact format (no other text):
{{
"theorems": [
{{
    "name": "theorem name",
    "statement": "formal mathematical statement",
    "proof": "proof text or 'Not provided'",
    "subject": "main subject: Algebra, Analysis, Topology, Number Theory, Geometry, Probability, or Logic",
    "domain": "specific subdomain like Linear Algebra, Real Analysis, Group Theory, etc.",
    "dependencies": ["theorem1", "theorem2"],
    "type":  "Theorem, Lemma, Proposition, Corollary, Conjecture, Definition, property or Hypothesis"
}}
]
}}

Rules:
1. Extract ALL mathematical statements
2. Use clear, standard mathematical terminology
3. If proof is not explicit, write "Not provided"
4. Dependencies are theorem names mentioned in the proof
5. Return valid JSON only
6. Read the Context twice and carefully before generating JSON object.
7. Do not return anything other than the JSON object.
8. Do not include any explanations or apologies in your responses.
9. Do not hallucinate.
10. chose one type for theorem type
12. Preserve all mathematical symbols exactly. 

Text to analyze:
{text}

JSON response:""",
    "examples": """
You are an expert mathematician. Extract all mathematical examples from the text below.

Return ONLY a valid JSON object in this exact format (no other text):
{{
"examples": [
{{
    "name": "example title or 'Example: [brief description]'",
    "content": "the complete example with solution/work shown",
    "subject": "same subject classification as theorems",
    "domain": "same domain classification as theorems",
    "illustrates_theorems": ["theorem names that this example demonstrates"],
    "difficulty": "Easy, Medium, or Hard"

}}
]
}}

Rules:
1. Extract ALL mathematical examples
2. Use clear, standard mathematical terminology
4. Return valid JSON only
5. Read the Context twice and carefully before generating JSON object.
6. Do not return anything other than the JSON object.
7. Do not include any explanations or apologies in your responses.
8. Do not hallucinate.
9. Skip any book introduction.
10. Examples include worked problems, illustrations, applications.
11. Examples should reference which theorems they demonstrate.
12. Preserve all mathematical symbols exactly. 
13. If no examples found, return empty examples array.
Text to analyze:
{text}

JSON response:"""

}