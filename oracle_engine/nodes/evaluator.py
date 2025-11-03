def evaluate_answers(quiz, answers):
    results = []
    for q, a in zip(quiz["questions"], answers):
        correct = q["answer"] == a
        results.append({"question": q["question"], "correct": correct})
    return results













