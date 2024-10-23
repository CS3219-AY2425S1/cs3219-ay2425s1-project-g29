export type QuestionAttempt = {
    questionId: string;
    questionTitle: string;
    difficulty: string;  // Match this with actual_difficulty
    category: string;
    timestamp: number;
    user1: string;
    user2: string;
    matchId: string;
};