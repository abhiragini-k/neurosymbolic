import axios from 'axios';

const api = axios.create({
    // baseURL: 'http://localhost:8000', // Removed to use Vite proxy
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add the auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle 401 (optional but good practice)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            // Optionally redirect to login, but Context usually handles this state
        }
        return Promise.reject(error);
    }
);

api.predictDrug = async (drugName) => {
    const response = await api.post('/predict/drug', { drug_name: drugName });
    return response.data;
};

api.analyzeDisease = async (diseaseName) => {
    const response = await api.post('/analyze/disease', { disease_name: diseaseName });
    return response.data;
};

export default api;
