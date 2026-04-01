import { BrowserRouter, Routes, Route } from "react-router-dom"
import { Login } from "./pages/Login";
import { Signup } from "./pages/Signup";
import { Home } from "./pages/Home";
import { Dashboard } from "./pages/Dashboard";
import { Settings } from "./pages/Settings";
import { ProtectedRoute } from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>


        <Route path="/" element={<Home/>}/>
        <Route path="/login" element={<Login/>}/>
        <Route path="/signup" element={<Signup/>}/>

        <Route 
          path="/settings" 
          element={
            <ProtectedRoute>
              <Settings/>
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard/>
            </ProtectedRoute>
          } 
        />

      </Routes>
    </BrowserRouter>
  )
}

export default App;