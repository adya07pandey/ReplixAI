import { useState } from "react";
import { useNavigate } from "react-router-dom"
import { connectGoogle, signup } from "../api/auth";

export const Signup = () => {

    const navigate = useNavigate();
    const [form, setForm] = useState({ orgname: "", email: "", password: "", confirmpassword: ""});
    const [error, setError] = useState(null);
    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    }
    const handleSignup = async () => {
        try {
            if (!form.orgname || !form.email || !form.password || !form.confirmpassword) {
                setError("Please fill all the details");
            }
            if ((form.password != form.confirmpassword)) {
                setError("Confirm password is different");
            }
          

            const formData = new FormData();
            formData.append("orgname", form.orgname);
            formData.append("email", form.email);
            formData.append("password", form.password);
            
            await signup(formData);
            navigate("/settings")

        } catch (err) {
            console.log(err);
            setError(err.response?.data?.message || "Signup failed");
        }
    }
   
    return (
        <div className="wholepage">
            <div className="loginbox">
                <h1>Create Account</h1>
                <input type="text" name="orgname" placeholder="Organization Name" onChange={handleChange} />
                <input type="email" name="email" placeholder="Email" onChange={handleChange} />
                <input type="password" name="password" placeholder="Password" onChange={handleChange} />
                <input type="password" name="confirmpassword" placeholder="Confirm Password" onChange={handleChange} />
                {error && <p style={{ color: "#ff6b6b" }}>{error}</p>}
                

                <button className="loginbtn" onClick={handleSignup}>SignUp</button>
                <p>
                    Already have an account?
                    <button className="login-change" onClick={() => navigate("../login")}><b>Login</b></button>
                </p>


            </div>
        </div>
    )
}