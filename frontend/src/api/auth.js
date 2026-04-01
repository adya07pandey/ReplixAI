import api from "./axios"

export const signup = async(data) => {
    return api.post("/auth/signup",data);    
}
export const saveSettings = async (data) => {
    return api.post("/auth/settings", data, {
        headers: {
            "Content-Type": "multipart/form-data"
        }
    })
}
export const connectGoogle = () => {
    window.location.href = "http://localhost:8000/auth/google"
}
export const login = async(data) => {
    return api.post("/auth/login",data);
}

export const authMe = async() => {
    return api.get("/auth/me");
}
