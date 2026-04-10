import { FormEvent, useEffect, useState } from "react";
import {
  useCreateRule,
  useDeleteRule,
  useRules,
  useStations,
  useToggleRule,
  useUpdateRule,
} from "../api/hooks";
import type { WatchRule, WatchRuleCreate } from "../api/types";

const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function WatchRules() {
  const { data: rules, isLoading } = useRules();
  const { data: stations } = useStations();
  const deleteRule = useDeleteRule();
  const toggleRule = useToggleRule();

  const [showForm, setShowForm] = useState(false);
  const [editingRule, setEditingRule] = useState<WatchRule | null>(null);

  const openAdd = () => {
    setEditingRule(null);
    setShowForm(true);
  };

  const openEdit = (rule: WatchRule) => {
    setEditingRule(rule);
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingRule(null);
  };

  const handleCreated = () => {
    closeForm();
  };

  if (isLoading) return <p>Loading...</p>;

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Watch Rules</h1>
        {!showForm && (
          <button className="btn btn-primary" onClick={openAdd}>
            + Add Rule
          </button>
        )}
      </div>

      {showForm && (
        <RuleForm
          rule={editingRule}
          stations={stations ?? []}
          onClose={closeForm}
          onSuccess={handleCreated}
        />
      )}

      {!rules || rules.length === 0 ? (
        !showForm && (
          <div className="card">
            <p>No watch rules yet. Click "+ Add Rule" to create one.</p>
          </div>
        )
      ) : (
        rules.map((rule) => (
          <div className="card" key={rule.id} style={{ opacity: rule.is_active ? 1 : 0.5 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
              <div>
                <strong>{rule.rule_type === "train_number" ? "Train #" : "Time Period"}</strong>
                {rule.rule_type === "train_number" ? (
                  <p>Train: {rule.train_number}</p>
                ) : (
                  <p>
                    Station: {rule.station_id} | {rule.start_time} – {rule.end_time}
                  </p>
                )}
                {rule.days_of_week && <p>Days: {formatDays(rule.days_of_week)}</p>}
              </div>
              <div className="actions">
                <button className="btn btn-secondary" onClick={() => toggleRule.mutate(rule.id)}>
                  {rule.is_active ? "Disable" : "Enable"}
                </button>
                <button className="btn btn-secondary" onClick={() => openEdit(rule)}>
                  Edit
                </button>
                <button
                  className="btn btn-danger"
                  onClick={() => {
                    if (confirm("Delete this rule?")) deleteRule.mutate(rule.id);
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </>
  );
}

function RuleForm({
  rule,
  stations,
  onClose,
  onSuccess,
}: {
  rule: WatchRule | null;
  stations: { station_id: string; name_zh: string }[];
  onClose: () => void;
  onSuccess: () => void;
}) {
  const isEdit = rule !== null;
  const createRule = useCreateRule();
  const updateRule = useUpdateRule(rule?.id ?? 0);
  const mutation = isEdit ? updateRule : createRule;

  const [ruleType, setRuleType] = useState<"train_number" | "time_period">("train_number");
  const [trainNumber, setTrainNumber] = useState("");
  const [stationId, setStationId] = useState("");
  const [startTime, setStartTime] = useState("06:00");
  const [endTime, setEndTime] = useState("09:00");
  const [selectedDays, setSelectedDays] = useState<number[]>([0, 1, 2, 3, 4]);

  useEffect(() => {
    if (rule) {
      setRuleType(rule.rule_type as "train_number" | "time_period");
      setTrainNumber(rule.train_number ?? "");
      setStationId(rule.station_id ?? "");
      setStartTime(rule.start_time ?? "06:00");
      setEndTime(rule.end_time ?? "09:00");
      setSelectedDays(rule.days_of_week ? rule.days_of_week.split(",").map(Number) : [0, 1, 2, 3, 4]);
    } else {
      setRuleType("train_number");
      setTrainNumber("");
      setStationId("");
      setStartTime("06:00");
      setEndTime("09:00");
      setSelectedDays([0, 1, 2, 3, 4]);
    }
  }, [rule]);

  const toggleDay = (day: number) => {
    setSelectedDays((prev) => (prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day].sort()));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const data: WatchRuleCreate = {
      rule_type: ruleType,
      days_of_week: selectedDays.join(","),
    };
    if (ruleType === "train_number") {
      data.train_number = trainNumber;
    } else {
      data.station_id = stationId;
      data.start_time = startTime;
      data.end_time = endTime;
    }
    (mutation as ReturnType<typeof useCreateRule>).mutate(data as WatchRuleCreate, {
      onSuccess,
    });
  };

  return (
    <div className="card" style={{ borderLeft: "4px solid #1a73e8" }}>
      <h2>{isEdit ? "Edit Rule" : "Add New Rule"}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Rule Type</label>
          <select value={ruleType} onChange={(e) => setRuleType(e.target.value as "train_number" | "time_period")}>
            <option value="train_number">By Train Number</option>
            <option value="time_period">By Time Period</option>
          </select>
        </div>

        {ruleType === "train_number" ? (
          <div className="form-group">
            <label>Train Number</label>
            <input
              type="text"
              value={trainNumber}
              onChange={(e) => setTrainNumber(e.target.value)}
              placeholder="e.g. 126"
              required
            />
          </div>
        ) : (
          <>
            <div className="form-group">
              <label>Station</label>
              <select value={stationId} onChange={(e) => setStationId(e.target.value)} required>
                <option value="">Select a station</option>
                {stations.map((s) => (
                  <option key={s.station_id} value={s.station_id}>
                    {s.name_zh} ({s.station_id})
                  </option>
                ))}
              </select>
            </div>
            <div style={{ display: "flex", gap: 16 }}>
              <div className="form-group" style={{ flex: 1 }}>
                <label>Start Time</label>
                <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} required />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label>End Time</label>
                <input type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)} required />
              </div>
            </div>
          </>
        )}

        <div className="form-group">
          <label>Days of Week</label>
          <div className="days-checkbox">
            {DAY_LABELS.map((label, idx) => (
              <label key={idx}>
                <input type="checkbox" checked={selectedDays.includes(idx)} onChange={() => toggleDay(idx)} />
                {label}
              </label>
            ))}
          </div>
        </div>

        {mutation.isError && <p className="error">Failed to {isEdit ? "update" : "create"} rule</p>}
        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? "Saving..." : isEdit ? "Save Changes" : "Create Rule"}
          </button>
          <button className="btn btn-secondary" type="button" onClick={onClose}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

function formatDays(days: string): string {
  const indices = days.split(",").map(Number);
  if (indices.length === 7) return "Every day";
  if (indices.length === 5 && indices.every((d) => d < 5)) return "Weekdays";
  return indices.map((i) => DAY_LABELS[i] ?? i).join(", ");
}
