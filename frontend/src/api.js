import axios from 'axios';

// The default Django port is usually 8000
const api = axios.create({
  baseURL: 'http://localhost:8000/api/', // Assuming API routes under /api/
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  }
});

export default api;
