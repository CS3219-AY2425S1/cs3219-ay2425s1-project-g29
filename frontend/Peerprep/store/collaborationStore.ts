import { defineStore } from "pinia";
import { useStorage } from '@vueuse/core';
export type TCollaborationInfo = {
  user1_id: string;
  user2_id: string;
  uid: string;
  question_id: string;
};

export const useCollaborationStore = defineStore({
  id: "collaboration",
  state: () => ({
    collaborationInfo: useStorage('collaborationInfo', null as TCollaborationInfo | null),
    // `useSotrage`: persist collaborationInfo in reloads, w/ persistence plugin
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
    },
    clearCollaborationInfo() {
      this.collaborationInfo = null;
    },
  },
});
