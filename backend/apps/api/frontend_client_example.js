/**
 * Frontend API Client Example
 * 
 * This file demonstrates how to integrate with the EduRise LMS API
 * from a frontend application (React, Vue, Angular, etc.)
 */

class EduRiseAPIClient {
    constructor(baseURL = 'http://localhost:8000/api', tenant = null) {
        this.baseURL = baseURL;
        this.tenant = tenant;
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    // Set tenant for multi-tenant support
    setTenant(tenant) {
        this.tenant = tenant;
    }

    // Get default headers for API requests
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth && this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        if (this.tenant) {
            headers['X-Tenant'] = this.tenant;
        }

        return headers;
    }

    // Generic API request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(options.includeAuth !== false),
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            // Handle token refresh if needed
            if (response.status === 401 && this.refreshToken) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Retry the original request
                    config.headers['Authorization'] = `Bearer ${this.accessToken}`;
                    const retryResponse = await fetch(url, config);
                    return await retryResponse.json();
                }
            }

            return {
                success: response.ok,
                status: response.status,
                data: data,
            };
        } catch (error) {
            console.error('API Request Error:', error);
            return {
                success: false,
                error: error.message,
            };
        }
    }

    // Authentication Methods
    async login(email, password) {
        const response = await this.request('/v1/accounts/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
            includeAuth: false,
        });

        if (response.success && response.data.access) {
            this.accessToken = response.data.access;
            this.refreshToken = response.data.refresh;
            localStorage.setItem('access_token', this.accessToken);
            localStorage.setItem('refresh_token', this.refreshToken);
        }

        return response;
    }

    async logout() {
        await this.request('/v1/accounts/auth/logout/', {
            method: 'POST',
            body: JSON.stringify({ refresh: this.refreshToken }),
        });

        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    async refreshAccessToken() {
        if (!this.refreshToken) return false;

        const response = await this.request('/v1/accounts/auth/refresh/', {
            method: 'POST',
            body: JSON.stringify({ refresh: this.refreshToken }),
            includeAuth: false,
        });

        if (response.success && response.data.access) {
            this.accessToken = response.data.access;
            localStorage.setItem('access_token', this.accessToken);
            return true;
        }

        return false;
    }

    // Dashboard Methods
    async getStudentDashboard() {
        return await this.request('/v1/dashboard/student/');
    }

    async getTeacherDashboard() {
        return await this.request('/v1/dashboard/teacher/');
    }

    async getAdminDashboard() {
        return await this.request('/v1/dashboard/admin/');
    }

    // Course Methods
    async getCourses(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/v1/courses/${queryString ? `?${queryString}` : ''}`;
        return await this.request(endpoint);
    }

    async getCourse(courseId) {
        return await this.request(`/v1/courses/${courseId}/`);
    }

    async getMarketplaceCourses(filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const endpoint = `/v1/courses/marketplace_enhanced/${queryString ? `?${queryString}` : ''}`;
        return await this.request(endpoint);
    }

    async getCourseRecommendations(limit = 10) {
        return await this.request(`/v1/courses/recommendations/?limit=${limit}`);
    }

    async enrollInCourse(courseId) {
        return await this.request(`/v1/courses/${courseId}/enroll/`, {
            method: 'POST',
        });
    }

    async getCourseAnalytics(courseId) {
        return await this.request(`/v1/courses/${courseId}/analytics/`);
    }

    async getCourseDashboardStats() {
        return await this.request('/v1/courses/dashboard_stats/');
    }

    // Enrollment Methods
    async getEnrollments(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/v1/enrollments/${queryString ? `?${queryString}` : ''}`;
        return await this.request(endpoint);
    }

    async updateEnrollmentProgress(enrollmentId, progressPercentage) {
        return await this.request(`/v1/enrollments/${enrollmentId}/update_progress/`, {
            method: 'PATCH',
            body: JSON.stringify({ progress_percentage: progressPercentage }),
        });
    }

    // Live Class Methods
    async getLiveClasses(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/v1/live-classes/${queryString ? `?${queryString}` : ''}`;
        return await this.request(endpoint);
    }

    async getUpcomingClasses() {
        return await this.request('/v1/live-classes/upcoming/');
    }

    async getClassJoinInfo(classId) {
        return await this.request(`/v1/live-classes/${classId}/join_info/`);
    }

    // Notification Methods
    async getNotifications(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/v1/notifications/${queryString ? `?${queryString}` : ''}`;
        return await this.request(endpoint);
    }

    async markNotificationAsRead(notificationId) {
        return await this.request(`/v1/notifications/${notificationId}/mark_read/`, {
            method: 'POST',
        });
    }

    // AI Methods
    async getAIConversations() {
        return await this.request('/v1/ai-conversations/');
    }

    async createAIConversation(data) {
        return await this.request('/v1/ai-conversations/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getAIQuizzes() {
        return await this.request('/v1/ai-quizzes/');
    }

    // Utility Methods
    async checkHealth() {
        return await this.request('/health/', { includeAuth: false });
    }

    async getAPIDocumentation() {
        return await this.request('/docs/', { includeAuth: false });
    }
}

// Usage Examples
const apiClient = new EduRiseAPIClient('http://localhost:8000/api', 'your-tenant-subdomain');

// Example: Login and get student dashboard
async function loginAndGetDashboard() {
    try {
        // Login
        const loginResponse = await apiClient.login('student@example.com', 'password');
        if (!loginResponse.success) {
            console.error('Login failed:', loginResponse.data);
            return;
        }

        console.log('Login successful!');

        // Get student dashboard
        const dashboardResponse = await apiClient.getStudentDashboard();
        if (dashboardResponse.success) {
            console.log('Dashboard data:', dashboardResponse.data.data);
        } else {
            console.error('Dashboard fetch failed:', dashboardResponse.data);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Example: Get marketplace courses with filters
async function getMarketplaceCourses() {
    try {
        const response = await apiClient.getMarketplaceCourses({
            category: 'technology',
            difficulty: 'beginner',
            min_rating: '4.0',
            sort_by: 'rating',
            sort_order: 'desc',
            page: 1,
            page_size: 20
        });

        if (response.success) {
            console.log('Marketplace courses:', response.data.data);
            console.log('Pagination info:', response.data.meta);
        } else {
            console.error('Failed to fetch courses:', response.data);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Example: Enroll in a course
async function enrollInCourse(courseId) {
    try {
        const response = await apiClient.enrollInCourse(courseId);
        
        if (response.success) {
            console.log('Enrollment successful:', response.data.data);
        } else {
            console.error('Enrollment failed:', response.data);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// React Hook Example
function useEduRiseAPI() {
    const [apiClient] = useState(() => new EduRiseAPIClient());
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const makeRequest = async (requestFn) => {
        setLoading(true);
        setError(null);
        
        try {
            const response = await requestFn();
            if (!response.success) {
                setError(response.data?.message || 'Request failed');
                return null;
            }
            return response.data;
        } catch (err) {
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    };

    return {
        apiClient,
        loading,
        error,
        makeRequest,
    };
}

// Vue Composable Example
function useEduRiseAPI() {
    const apiClient = new EduRiseAPIClient();
    const loading = ref(false);
    const error = ref(null);

    const makeRequest = async (requestFn) => {
        loading.value = true;
        error.value = null;
        
        try {
            const response = await requestFn();
            if (!response.success) {
                error.value = response.data?.message || 'Request failed';
                return null;
            }
            return response.data;
        } catch (err) {
            error.value = err.message;
            return null;
        } finally {
            loading.value = false;
        }
    };

    return {
        apiClient,
        loading: readonly(loading),
        error: readonly(error),
        makeRequest,
    };
}

export default EduRiseAPIClient;