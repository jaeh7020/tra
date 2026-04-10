import { Link } from "react-router-dom";
import { useDeleteRule, useRules, useToggleRule } from "../api/hooks";

export default function WatchRules() {
  const { data: rules, isLoading } = useRules();
  const deleteRule = useDeleteRule();
  const toggleRule = useToggleRule();

  if (isLoading) return <p>Loading...</p>;

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Watch Rules</h1>
        <Link to="/rules/new" className="btn btn-primary" style={{ textDecoration: "none" }}>
          + Add Rule
        </Link>
      </div>

      {!rules || rules.length === 0 ? (
        <div className="card">
          <p>No watch rules yet. Click "Add Rule" to create one.</p>
        </div>
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
                {rule.days_of_week && <p>Days: {rule.days_of_week}</p>}
              </div>
              <div className="actions">
                <button
                  className="btn btn-secondary"
                  onClick={() => toggleRule.mutate(rule.id)}
                >
                  {rule.is_active ? "Disable" : "Enable"}
                </button>
                <Link to={`/rules/${rule.id}/edit`} className="btn btn-secondary" style={{ textDecoration: "none" }}>
                  Edit
                </Link>
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
