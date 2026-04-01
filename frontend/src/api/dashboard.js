import api from "./axios";

export const dashboardResults = async () => {
    const res = api.get(`/dashboard`);

    console.log(res);
    return res;
}