import dayjs from "dayjs";
import { Link } from "react-router-dom";
import { useAlerts, useRules } from "../api/hooks";

export default function Dashboard() {
  const { data: rules, isLoading: rulesLoading } = useRules();
  const { data: alerts, isLoading: alertsLoading } = useAlerts();

  if (rulesLoading || alertsLoading) return <p>Loading...</p>;

  const activeRules = rules?.filter((r) => r.is_active) ?? [];

  return (
    <>
      <h1>Dashboard</h1>

      <div className="card">
        <h2>Active Watch Rules ({activeRules.length})</h2>
        {activeRules.length === 0 ? (
          <p>
            No active watch rules. <Link to="/rules/new">Add one</Link>
          </p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Target</th>
                <th>Schedule</th>
              </tr>
            </thead>
            <tbody>
              {activeRules.map((rule) => (
                <tr key={rule.id}>
                  <td>{rule.rule_type === "train_number" ? "Train #" : "Time Period"}</td>
                  <td>
                    {rule.rule_type === "train_number"
                      ? rule.train_number
                      : `Station ${rule.station_id} ${rule.start_time}–${rule.end_time}`}
                  </td>
                  <td>{formatDays(rule.days_of_week)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h2>Recent Alerts</h2>
        {!alerts || alerts.length === 0 ? (
          <p>No alerts yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Train</th>
                <th>Status</th>
                <th>Notified</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((a) => (
                <tr key={a.id}>
                  <td>{dayjs(a.detected_at).format("MM/DD HH:mm")}</td>
                  <td>{a.train_number}</td>
                  <td>
                    {a.is_cancelled ? (
                      <span className="badge badge-cancel">Cancelled</span>
                    ) : (
                      <span className="badge badge-delay">Delayed {a.delay_minutes}min</span>
                    )}
                  </td>
                  <td>{a.notified ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}

const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function formatDays(days: string | null): string {
  if (!days) return "Every day";
  const indices = days.split(",").map(Number);
  if (indices.length === 7) return "Every day";
  if (indices.length === 5 && indices.every((d) => d < 5)) return "Weekdays";
  return indices.map((i) => DAY_NAMES[i] ?? i).join(", ");
}
