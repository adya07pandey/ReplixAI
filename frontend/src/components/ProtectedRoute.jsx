import { Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { authMe } from "../api/auth";

export const ProtectedRoute = ({ children }) => {
    const [loading, setLoading] = useState(true);
    const [isAuth, setIsAuth] = useState(false);

    useEffect(() => {
        const check = async () => {
            try {
                await authMe();   
                setIsAuth(true);
            } catch {
                setIsAuth(false);
            } finally {
                setLoading(false);
            }
        };

        check();
    }, []);

    if (loading) return <div className="loading">Checking auth...</div>;

    if (!isAuth) return <Navigate to="/login" />;

    return children;
};