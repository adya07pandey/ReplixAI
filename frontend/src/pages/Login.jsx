import { useState } from "react";
import {useNavigate} from "react-router-dom";
import { login } from "../api/auth";

export const Login = () => {
    const navigate = useNavigate("");
    const [form,setForm] = useState({ email:"", password:""})
    const [error,setError] = useState(null);
    const handleChange = (e) => {
        setForm({...form,[e.target.name]:e.target.value})
    }
    const handleLogin = async() => {
        try{
            await login(form);
            navigate("/dashboard");
        }catch(err){
            setError(err.response?.data?.message || "Login failed");
        }
    }

    return (
        <div className="wholepage">
            <div className="loginbox">
                <h1>Welcome Back!</h1>
                {/* <input type="text" name="name" placeholder="Name" onChange={handleChange}/> */}
                <input type="email" name="email" placeholder="Email" onChange={handleChange}/>
                <input type="password" name="password" placeholder="Password" onChange={handleChange}/>
                {error && <p style={{color:"#ff6b6b"}}>{error}</p>}
                <button className="loginbtn" onClick={handleLogin}>Login</button>
                <p>
                    Don't have an account?
                    <button className="login-change" onClick={()=>navigate("../signup")}><b>SignUp</b></button>
                </p>
            </div>
        </div>
    )
}