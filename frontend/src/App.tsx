import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useMe } from "./api/hooks";
import AddRule from "./pages/AddRule";
import Dashboard from "./pages/Dashboard";
import EditRule from "./pages/EditRule";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Settings from "./pages/Settings";
import WatchRules from "./pages/WatchRules";

function App() {
  const token = localStorage.getItem("token");
  const { data: user } = useMe();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
    window.location.reload();
  };

  return (
    <>
      {token && (
        <nav>
          <div>
            <Link to="/">Dashboard</Link>
            <Link to="/rules">Watch Rules</Link>
            <Link to="/settings">Settings</Link>
          </div>
          <div>
            <span style={{ color: "white", marginRight: 12 }}>{user?.email}</span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        </nav>
      )}
      <div className="container">
        <Routes>
          <Route path="/login" element={token ? <Navigate to="/" /> : <Login />} />
          <Route path="/register" element={token ? <Navigate to="/" /> : <Register />} />
          <Route path="/" element={token ? <Dashboard /> : <Navigate to="/login" />} />
          <Route path="/rules" element={token ? <WatchRules /> : <Navigate to="/login" />} />
          <Route path="/rules/new" element={token ? <AddRule /> : <Navigate to="/login" />} />
          <Route path="/rules/:id/edit" element={token ? <EditRule /> : <Navigate to="/login" />} />
          <Route path="/settings" element={token ? <Settings /> : <Navigate to="/login" />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
