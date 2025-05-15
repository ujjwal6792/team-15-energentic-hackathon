// 📁 store/useSessionStore.ts
import { create } from 'zustand';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

export type SessionResponse = {
  id: string;
  app_name: string;
  user_id: string;
  state: Record<string, unknown>;
  events: unknown[];
  last_update_time: number;
};

type SessionState = {
  session: SessionResponse | null;
  loading: boolean;
  error: string | null;
  createSession: () => Promise<void>;
};

export const useSessionStore = create<SessionState>((set) => ({
  session: null,
  loading: false,
  error: null,

  createSession: async () => {
    const uuid = uuidv4();
    set({ loading: true, error: null });

    try {
      const response = await axios.post<SessionResponse>(
        `https://solar-agent.dhiway.net/apps/tool_agent/users/example_user/sessions/${uuid}`
      );

      set({ session: response.data, loading: false });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },
}));
