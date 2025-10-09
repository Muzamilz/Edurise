<template>
  <div class="unauthorized-page">
    <div class="unauthorized-content">
      <div class="error-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
      </div>
      
      <h1>Access Denied</h1>
      <p>You don't have permission to access this page.</p>
      
      <div class="actions">
        <router-link to="/dashboard" class="btn btn-primary">
          Go to Dashboard
        </router-link>
        <router-link to="/" class="btn btn-secondary">
          Go Home
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.unauthorized-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background-color: #f9fafb;
}

.unauthorized-content {
  text-align: center;
  max-width: 400px;
}

.error-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 2rem;
  color: #ef4444;
}

.error-icon svg {
  width: 100%;
  height: 100%;
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

p {
  color: #6b7280;
  font-size: 1.125rem;
  margin-bottom: 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background-color: #f9fafb;
}
</style>