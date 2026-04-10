import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "./client";
import type {
  AlertHistory,
  Station,
  Token,
  User,
  WatchRule,
  WatchRuleCreate,
} from "./types";

// --- Auth ---

export function useLogin() {
  return useMutation({
    mutationFn: async (data: { email: string; password: string }) => {
      const res = await api.post<Token>("/auth/login", data);
      return res.data;
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: async (data: { email: string; password: string }) => {
      const res = await api.post<Token>("/auth/register", data);
      return res.data;
    },
  });
}

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const res = await api.get<User>("/auth/me");
      return res.data;
    },
    enabled: !!localStorage.getItem("token"),
  });
}

// --- Watch Rules ---

export function useRules() {
  return useQuery({
    queryKey: ["rules"],
    queryFn: async () => {
      const res = await api.get<WatchRule[]>("/rules");
      return res.data;
    },
  });
}

export function useRule(id: number) {
  return useQuery({
    queryKey: ["rules", id],
    queryFn: async () => {
      const res = await api.get<WatchRule>(`/rules/${id}`);
      return res.data;
    },
  });
}

export function useCreateRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: WatchRuleCreate) => {
      const res = await api.post<WatchRule>("/rules", data);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rules"] }),
  });
}

export function useUpdateRule(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<WatchRuleCreate & { is_active: boolean }>) => {
      const res = await api.put<WatchRule>(`/rules/${id}`, data);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rules"] }),
  });
}

export function useDeleteRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/rules/${id}`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rules"] }),
  });
}

export function useToggleRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const res = await api.patch<WatchRule>(`/rules/${id}/toggle`);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rules"] }),
  });
}

// --- Alerts ---

export function useAlerts(limit = 50) {
  return useQuery({
    queryKey: ["alerts", limit],
    queryFn: async () => {
      const res = await api.get<AlertHistory[]>("/alerts", { params: { limit } });
      return res.data;
    },
    refetchInterval: 30_000,
  });
}

// --- Trains (reference data) ---

export function useStations() {
  return useQuery({
    queryKey: ["stations"],
    queryFn: async () => {
      const res = await api.get<Station[]>("/trains/stations");
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000, // 24h
  });
}

// --- LINE ---

export function useUpdateLineUserId() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (line_user_id: string) => {
      await api.post("/auth/line-user-id", { line_user_id });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["me"] }),
  });
}
