import { useMe } from "../api/hooks";

export default function Settings() {
  const { data: user } = useMe();

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

        {user?.line_linked ? (
          <p style={{ color: "#1e8e3e" }}>
            Your LINE account is linked. You will receive notifications when watched trains are delayed or cancelled.
          </p>
        ) : (
          <>
            <p style={{ marginBottom: 8 }}>
              To receive delay/cancellation alerts via LINE:
            </p>
            <ol style={{ marginBottom: 16, paddingLeft: 20 }}>
              <li>Scan the QR code below to add our bot as a friend (or search <strong>@122bvrcf</strong>)</li>
              <li>Send any message to the bot</li>
              <li>The bot will reply with a linking URL — click it to connect your account</li>
            </ol>
            <div style={{ textAlign: "center", marginBottom: 20 }}>
              <img
                src="https://qr-official.line.me/gs/M_122bvrcf_BW.png"
                alt="LINE QR Code"
                style={{ width: 180, height: 180, border: "1px solid #ddd", borderRadius: 8 }}
              />
              <p style={{ fontSize: 13, color: "#5f6368", marginTop: 8 }}>@122bvrcf</p>
            </div>
          </>
        )}
      </div>
    </>
  );
}
