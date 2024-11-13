export type Question = {
  id?: number;
  title: string;
  description: string;
  category: string;
  difficulty: "easy" | "medium" | "hard";
  uid?: string;
};
