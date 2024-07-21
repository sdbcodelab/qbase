import dspy

class ReadabilityAnalyzer(dspy.Signature):
    """Analyze the readability of the given context."""
    context = dspy.InputField()
    readability_score = dspy.InputField()

class TopicAndIntentIdentifier(dspy.Signature):
    """Identify the topic and unique user intents from the context."""
    context = dspy.InputField()
    topic = dspy.OutputField()
    user_intents = dspy.OutputField(desc="List of unique user intents in 2-3 words each")

class QuestionGenerator(dspy.Signature):
    """Generate a question based on the context, topic, and user intent."""
    context = dspy.InputField()
    topic = dspy.InputField()
    user_intent = dspy.InputField()
    question = dspy.OutputField(desc="A question in less than 10 words")

class AnswerGenerator(dspy.Signature):
    """Generate answers (simple, short, standard) for a given question."""
    context = dspy.InputField()
    question = dspy.InputField()
    simple_answer = dspy.OutputField(desc="A simple, one-sentence answer")
    short_answer = dspy.OutputField(desc="A concise answer in 2-3 sentences")
    standard_answer = dspy.OutputField(desc="A comprehensive answer in 4-5 sentences")

class FactCollector(dspy.Signature):
    """Collect supporting facts and figures that are relevant to the given answer. Collect facts and figures strictly from the context."""
    context = dspy.InputField()
    answer = dspy.InputField()
    supporting_facts = dspy.OutputField(desc="""
    List of facts in JSON format: [{ 'fact': 'fact_name', 'figure': 'numeric_value' }]
    
    Guidelines:
    1. 'fact' MUST be 1-2 words only. No exceptions.
    2. 'figure' MUST be a numeric value (count, percentage, or ratio) with unit.
    3. Only include numeric facts e.g. quantity, unit price, total amount, product specification, dimension, etc.
    4. If no relevant facts with numeric figures are found, return an empty list: [].
    5. Do not use placeholder values or non-numeric entries for 'figure'.
    
    Example of correct format:
    [
        { 'fact': 'Block time', 'figure': '10 secs' },
        { 'fact': 'Transactions', 'figure': '100000 per sec' },
        { 'fact': 'H x D x L', 'figure': '54 x 36 x 72 cm' },
        { 'fact': 'Price', 'figure': '$ 1400.99' }                            
    ]
    """)
