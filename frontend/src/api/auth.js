import api from "./axios";

export const checkEmail = (email) =>
  api.post("/auth/check-email/", { email });


