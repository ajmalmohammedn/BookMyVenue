import api from "./axios";

export const checkEmail = (email) =>
  api.post("/auth/check-email/", { email });

export const verifyOTP = (email, otp, otp_type = "signup") =>
  api.post("/auth/verify-otp/", { email, otp, otp_type });


export const resendOTP = (email) =>
  api.post("/auth/check-email/", { email });

export const login = (email, password) =>
  api.post("/auth/login/", { email, password });

export const logout = (refresh_token) =>
  api.post("/auth/logout/", { refresh_token });

export const completeProfile = (data) =>
  api.post("/auth/complete-profile/", data);

export const refreshToken = (refresh_token) =>
  api.post("/auth/refresh-token/", { refresh_token });

export const setPassword = (password, confirm_password) =>
  api.post("/auth/set-password/", { password, confirm_password });

export const resetPassword = (email) =>
  api.post("/auth/reset-password/", { email });