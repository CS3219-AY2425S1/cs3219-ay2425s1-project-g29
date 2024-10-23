import type { QuestionAttempt } from "./QuestionAttempt";

export type UserProfile = {
    displayName?: string;
    email?: string;
    photoURL?: string;
    attemptHistory?: QuestionAttempt[];
}