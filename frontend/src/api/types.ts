export interface Token {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  line_linked: boolean;
  created_at: string;
}

export interface WatchRule {
  id: number;
  rule_type: "train_number" | "time_period";
  train_number: string | null;
  station_id: string | null;
  start_time: string | null;
  end_time: string | null;
  days_of_week: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WatchRuleCreate {
  rule_type: "train_number" | "time_period";
  train_number?: string;
  station_id?: string;
  start_time?: string;
  end_time?: string;
  days_of_week?: string;
}

export interface AlertHistory {
  id: number;
  watch_rule_id: number;
  train_number: string;
  delay_minutes: number;
  is_cancelled: boolean;
  detected_at: string;
  notified: boolean;
}

export interface Station {
  station_id: string;
  name_zh: string;
  name_en: string | null;
}

export interface TrainType {
  type_code: string;
  name_zh: string;
  name_en: string | null;
}
