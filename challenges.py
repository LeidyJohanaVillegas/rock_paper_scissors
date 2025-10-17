import random
from quiz import quiz_questions
from guessTheWord import word_guess_questions

def get_random_quiz_question():
    question_data = random.choice(quiz_questions)
    # Return a shallow copy so callers don't accidentally expose the correct answer
    return {
        'type': 'quiz',
        'question': question_data['question'],
        'options': question_data['options'],
        'correct_answer': question_data['correct_answer']  # kept for server-side checking
    }

def get_random_word_challenge():
    challenge = random.choice(word_guess_questions)
    return {
        'type': 'word_guess',
        'clue': challenge['clue'],
        'hint': challenge['hint'],
        'word': challenge['word']  # kept for server-side checking
    }

def get_random_challenge():
    # Choose between quiz and word guess
    if random.choice(['quiz', 'word_guess']) == 'quiz':
        return get_random_quiz_question()
    else:
        return get_random_word_challenge()

def check_challenge(challenge, answer):
    """
    Check the provided answer against the stored challenge.
    For quiz challenge answer should be a single letter like 'a', 'b', etc.
    For word_guess the answer should be the guessed word.
    Returns True if correct, False otherwise.
    """
    if not challenge or 'type' not in challenge:
        return False

    if challenge['type'] == 'quiz':
        expected = challenge.get('correct_answer')
        return str(answer).lower().strip() == str(expected).lower().strip()
    elif challenge['type'] == 'word_guess':
        expected = challenge.get('word')
        return str(answer).lower().strip() == str(expected).lower().strip()
    return False
