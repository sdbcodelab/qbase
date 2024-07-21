import dspy
from services.signatures import *
from textstat import flesch_kincaid_grade
from utils.logger import get_logger

logger = get_logger(__name__)

class ContextAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.readability_analyzer = dspy.Predict(ReadabilityAnalyzer)
        self.topic_intent_identifier = dspy.Predict(TopicAndIntentIdentifier)
        self.question_generator = dspy.Predict(QuestionGenerator)
        self.answer_generator = dspy.Predict(AnswerGenerator)
        self.fact_collector = dspy.Predict(FactCollector)
        logger.info("ContextAnalyzer initialized")

    def forward(self, context):
        logger.info("Starting context analysis")
        try:
            readability = calculate_readability(context)
            readability_str = f"{readability:.2f}"
            logger.info(f"Readability score calculated: {readability_str}")
            
            readability_result = self.readability_analyzer(context=context, readability_score=readability_str)
            topic_intents = self.topic_intent_identifier(context=context)
            
            logger.info(f"Topic identified: {topic_intents.topic}")
            logger.info(f"User intents identified: {topic_intents.user_intents}")
            
            # Ensure user_intents is a list
            if isinstance(topic_intents.user_intents, str):
                user_intents = topic_intents.user_intents.split('\n')
            else:
                user_intents = topic_intents.user_intents

            # Filter out invalid intents
            valid_intents = [intent.strip() for intent in user_intents if len(intent.strip()) >= 3]
            logger.info(f"Valid intents: {valid_intents}")
            
            questions_answers = []
            generated_questions = set()
            
            for intent in valid_intents:
                logger.info(f"Processing intent: {intent}")
                try:
                    question_result = self.question_generator(context=context, topic=topic_intents.topic, user_intent=intent)
                    logger.info(f"Generated question: {question_result.question}")
                    
                    if question_result.question not in generated_questions and len(question_result.question.split()) <= 10:
                        generated_questions.add(question_result.question)
                        answers = self.answer_generator(context=context, question=question_result.question)
                        facts = self.fact_collector(context=context, answer=answers.standard_answer)
                        
                        questions_answers.append({
                            "question": question_result.question,
                            "simple_answer": answers.simple_answer,
                            "short_answer": answers.short_answer,
                            "standard_answer": answers.standard_answer,
                            "supporting_facts": facts.supporting_facts
                        })
                        logger.info(f"Added question and answers to results")
                    else:
                        logger.info(f"Skipping duplicate or invalid question: {question_result.question}")
                except Exception as e:
                    logger.error(f"Error processing intent '{intent}': {str(e)}")
            
            logger.info(f"Generated {len(questions_answers)} questions and answers")
            logger.info("Context analysis completed")
            return {
                "readability_score": readability_str,
                "topic": topic_intents.topic,
                "user_intents": valid_intents,
                "questions_answers": questions_answers
            }
        except Exception as e:
            logger.error(f"Error during context analysis: {str(e)}")
            raise

def calculate_readability(text):
    try:
        return flesch_kincaid_grade(text)
    except Exception as e:
        logger.error(f"Error calculating readability: {str(e)}")
        return 0.0
