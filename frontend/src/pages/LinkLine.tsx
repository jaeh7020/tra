import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

export default function LinkLine() {
  const [searchParams] = useSearchParams();
  const linkToken = searchParams.get("linkToken");

  useEffect(() => {
    if (linkToken) {
      const token = localStorage.getItem("token");
      if (token) {
        // User is logged in — redirect to backend to complete the linking
        window.location.href = `/api/auth/link-line?linkToken=${linkToken}&token=${token}`;
      }
    }
  }, [linkToken]);

  if (!linkToken) {
    return (
      <div style={{ maxWidth: 400, margin: "80px auto" }}>
        <div className="card">
          <h2>Invalid Link</h2>
          <p>This linking URL is invalid or has expired. Please send a message to the bot on LINE to get a new one.</p>
        </div>
      </div>
    );
  }

  const token = localStorage.getItem("token");

  if (token) {
    return (
      <div style={{ maxWidth: 400, margin: "80px auto" }}>
        <div className="card" style={{ textAlign: "center" }}>
          <p>Linking your LINE account...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 400, margin: "80px auto" }}>
      <div className="card">
        <h2>Link LINE Account</h2>
        <p style={{ marginBottom: 16 }}>
          Please log in to link your LINE account to TRA Train Monitor.
        </p>
        <a
          href={`/login?redirect=/link-line?linkToken=${encodeURIComponent(linkToken)}`}
          className="btn btn-primary"
          style={{ textDecoration: "none", display: "block", textAlign: "center" }}
        >
          Log In to Link
        </a>
      </div>
    </div>
  );
}
