import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLogin } from "../api/hooks";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useLogin();
  const navigate = useNavigate();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    login.mutate(
      { email, password },
      {
        onSuccess: (data) => {
          localStorage.setItem("token", data.access_token);
          navigate("/");
          window.location.reload();
        },
      }
    );
  };

  return (
    <div style={{ maxWidth: 400, margin: "80px auto" }}>
      <div className="card">
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {login.isError && <p className="error">Invalid credentials</p>}
          <button className="btn btn-primary" type="submit" disabled={login.isPending}>
            {login.isPending ? "Logging in..." : "Login"}
          </button>
        </form>
        <p style={{ marginTop: 16 }}>
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}
