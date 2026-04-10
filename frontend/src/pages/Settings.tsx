import { FormEvent, useState } from "react";
import { useMe, useUpdateLineUserId } from "../api/hooks";

export default function Settings() {
  const { data: user } = useMe();
  const updateLineUserId = useUpdateLineUserId();
  const [lineUserId, setLineUserId] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    updateLineUserId.mutate(lineUserId, {
      onSuccess: () => setLineUserId(""),
    });
  };

  return (
    <>
      <h1>Settings</h1>

      <div className="card">
        <h2>LINE Messaging</h2>
        <p style={{ marginBottom: 12 }}>
          Status:{" "}
          {user?.line_linked ? (
            <span className="badge badge-ok">Linked</span>
          ) : (
            <span className="badge badge-delay">Not linked</span>
          )}
        </p>
        <p style={{ marginBottom: 8 }}>
          To receive delay/cancellation alerts via LINE:
        </p>
        <ol style={{ marginBottom: 16, paddingLeft: 20 }}>
          <li>Add our LINE Official Account as a friend (scan the QR code or search the bot ID)</li>
          <li>Send any message to the bot — it will reply with your LINE User ID</li>
          <li>Paste your LINE User ID below to link your account</li>
        </ol>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>LINE User ID</label>
            <input
              type="text"
              value={lineUserId}
              onChange={(e) => setLineUserId(e.target.value)}
              placeholder="e.g. U1234567890abcdef..."
              required
            />
          </div>
          {updateLineUserId.isSuccess && (
            <p style={{ color: "#1e8e3e", marginBottom: 8 }}>LINE account linked!</p>
          )}
          {updateLineUserId.isError && <p className="error">Failed to link LINE account</p>}
          <button className="btn btn-primary" type="submit" disabled={updateLineUserId.isPending}>
            {updateLineUserId.isPending ? "Saving..." : "Link LINE Account"}
          </button>
        </form>
      </div>
    </>
  );
}
