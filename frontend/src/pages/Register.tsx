import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useRegister } from "../api/hooks";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const register = useRegister();
  const navigate = useNavigate();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    register.mutate(
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
        <h2>Register</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>
          {register.isError && <p className="error">Registration failed. Email may already be in use.</p>}
          <button className="btn btn-primary" type="submit" disabled={register.isPending}>
            {register.isPending ? "Registering..." : "Register"}
          </button>
        </form>
        <p style={{ marginTop: 16 }}>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
