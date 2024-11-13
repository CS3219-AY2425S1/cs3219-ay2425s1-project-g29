export type QuestionAttempt = {
    sessionId: string;
    timeDate: string;
    matchedUser: string;
    questionId: string;
    questionTitle: string;
    questionDifficulty: string;  // Match this with actual_difficulty
    questionCategory: string;
};

export type QuestionAttemptNet = {
    session_id: string;
    timestamp: number;
    matched_user: string;
    question_id: string;
};