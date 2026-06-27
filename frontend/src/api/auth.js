import api from "./axios";

export const checkEmail = (email) =>
  api.post("/auth/check-email/", { email });

export const verifyOTP = (email, otp, otp_type = "signup") =>
  api.post("/auth/verify-otp/", { email, otp, otp_type });


export const resendOTP = (email) =>
  api.post("/auth/check-email/", { email });