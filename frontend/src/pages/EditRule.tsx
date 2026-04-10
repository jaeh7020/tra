import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useRule, useStations, useUpdateRule } from "../api/hooks";

const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function EditRule() {
  const { id } = useParams<{ id: string }>();
  const ruleId = Number(id);
  const { data: rule, isLoading } = useRule(ruleId);
  const { data: stations } = useStations();
  const updateRule = useUpdateRule(ruleId);
  const navigate = useNavigate();

  const [ruleType, setRuleType] = useState<"train_number" | "time_period">("train_number");
  const [trainNumber, setTrainNumber] = useState("");
  const [stationId, setStationId] = useState("");
  const [startTime, setStartTime] = useState("06:00");
  const [endTime, setEndTime] = useState("09:00");
  const [selectedDays, setSelectedDays] = useState<number[]>([]);

  useEffect(() => {
    if (rule) {
      setRuleType(rule.rule_type as "train_number" | "time_period");
      setTrainNumber(rule.train_number ?? "");
      setStationId(rule.station_id ?? "");
      setStartTime(rule.start_time ?? "06:00");
      setEndTime(rule.end_time ?? "09:00");
      setSelectedDays(rule.days_of_week ? rule.days_of_week.split(",").map(Number) : []);
    }
  }, [rule]);

  const toggleDay = (day: number) => {
    setSelectedDays((prev) => (prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day].sort()));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const data: Record<string, unknown> = {
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
    updateRule.mutate(data as Parameters<typeof updateRule.mutate>[0], {
      onSuccess: () => navigate("/rules"),
    });
  };

  if (isLoading) return <p>Loading...</p>;
  if (!rule) return <p>Rule not found</p>;

  return (
    <>
      <h1>Edit Watch Rule</h1>
      <div className="card">
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
                  {stations?.map((s) => (
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

          {updateRule.isError && <p className="error">Failed to update rule</p>}
          <div className="actions">
            <button className="btn btn-primary" type="submit" disabled={updateRule.isPending}>
              {updateRule.isPending ? "Saving..." : "Save Changes"}
            </button>
            <button className="btn btn-secondary" type="button" onClick={() => navigate("/rules")}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
