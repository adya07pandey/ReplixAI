
import { useNavigate } from "react-router-dom";

export const Home = () => {
    const navigate = useNavigate();
    return (
        <div className="homepage">
            <div className="homenavbar">
                <div className="lightlogo">
                    <div>
                        <img src="\lightlogo.png" alt="logo" />
                    </div>
                </div>
                    <div className="homebtn">
                        <button className="home-signup"  onClick={() => navigate("/signup")}>Signup</button>
                        <button className="home-login"  onClick={() => navigate("/login")}>Login</button>
                    </div>
            </div>

            <div className="hometitles">
                <h1>Replix AI</h1>  
                <h2>AI Email Automation Platform</h2>
                <h3>Streamline high-volume email workflows with intelligent agents that categorize, process, and respond instantly.</h3>  
                <button  onClick={() => navigate("/signup")} >Get Started</button>
            </div>    
        </div>
    )
}