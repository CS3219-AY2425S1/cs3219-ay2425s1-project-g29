import { defineStore } from "pinia";
export type TCollaborationInfo = {
  user1_id: string;
  user2_id: string;
  uid: string;
  question_id: string;
};

export const useCollaborationStore = defineStore({
  id: "collaboration",
  state: () => ({
    collaborationInfo: JSON.parse(
      localStorage.getItem("collaborationInfo") as string
    ) as TCollaborationInfo | null,
  }),
  getters: {
    isCollaborating: (state) => state.collaborationInfo !== null,
    isUserInCollaboration: (state) => (user_id: string) =>
      state.collaborationInfo
        ? [
            state.collaborationInfo.user1_id,
            state.collaborationInfo.user2_id,
          ].includes(user_id)
        : false,
    getCollaborationInfo: (state) => state.collaborationInfo,
  },
  actions: {
    setCollaborationInfo(collaborationInfo: TCollaborationInfo) {
      this.collaborationInfo = collaborationInfo;
      localStorage.setItem(
        "collaborationInfo",
        JSON.stringify(collaborationInfo)
      );
    },
    clearCollaborationInfo() {
      this.collaborationInfo = null;
      localStorage.removeItem("collaborationInfo");
    },
  },
});
