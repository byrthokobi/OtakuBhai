import axios from "axios";

// Set your backend base URL here
const API_BASE_URL = "http://localhost:8001";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Login function
export async function loginUser(email, password) {
  const response = await api.post("/auth/login", {
    email,
    password,
  });
  return response.data;
}
