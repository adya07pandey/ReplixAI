import api from "./axios";

export const getEmails = async(category) => {
    return api.get(`/emails/category/${category}`);
}

export const openMail = async(emailid) => {
    return api.get(`/emails/mail/${emailid}`);
}
export const updateMail = async (id, data) => {
  return api.put(`/emails/${id}`, data);
};

// api/emails.js
export const sendMail = async (id) => {
  return api.post(`/emails/send/${id}`);
};