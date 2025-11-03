def score_quiz(results):
    score = sum(1 for r in results if r["correct"])
    return {"correct": score, "total": len(results)}













