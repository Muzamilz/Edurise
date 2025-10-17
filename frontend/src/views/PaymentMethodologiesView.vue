<template>
  <div class="payment-methodologies-view">
    <div class="container">
      <div class="page-header">
        <h1>Payment Methodologies</h1>
        <p>Secure and flexible payment options for your learning journey</p>
      </div>

      <div class="content">
        <section class="payment-methods">
          <h2>Accepted Payment Methods</h2>
          <div class="methods-grid">
            <div class="method-card">
              <div class="method-icon">💳</div>
              <h3>Credit & Debit Cards</h3>
              <p>Visa, Mastercard, American Express, and Discover</p>
            </div>
            <div class="method-card">
              <div class="method-icon">🏦</div>
              <h3>Bank Transfer</h3>
              <p>Direct bank transfers and wire payments</p>
            </div>
            <div class="method-card">
              <div class="method-icon">📱</div>
              <h3>Digital Wallets</h3>
              <p>PayPal, Apple Pay, Google Pay, and more</p>
            </div>
            <div class="method-card">
              <div class="method-icon">🔄</div>
              <h3>Installments</h3>
              <p>Split payments into manageable installments</p>
            </div>
          </div>
        </section>

        <section class="security-section">
          <h2>Security & Protection</h2>
          <div class="security-features">
            <div class="security-item">
              <h3>🔒 SSL Encryption</h3>
              <p>All transactions are protected with 256-bit SSL encryption</p>
            </div>
            <div class="security-item">
              <h3>🛡️ PCI Compliance</h3>
              <p>We meet the highest standards for payment card security</p>
            </div>
            <div class="security-item">
              <h3>💰 Money-Back Guarantee</h3>
              <p>30-day refund policy for your peace of mind</p>
            </div>
          </div>
        </section>

        <section class="faq-section">
          <h2>Payment FAQs</h2>
          <div class="faq-list">
            <div class="faq-item">
              <h3>When will I be charged?</h3>
              <p>You'll be charged immediately upon enrollment or at the start of your subscription period.</p>
            </div>
            <div class="faq-item">
              <h3>Can I get a refund?</h3>
              <p>Yes, we offer a 30-day money-back guarantee for all courses and subscriptions.</p>
            </div>
            <div class="faq-item">
              <h3>Are there any hidden fees?</h3>
              <p>No, the price you see is the price you pay. No hidden fees or additional charges.</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component logic can be added here
</script>

<style scoped>
.payment-methodologies-view {
  min-height: 100vh;
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 3rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.page-header p {
  font-size: 1.25rem;
  color: #6b7280;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.payment-methods h2,
.security-section h2,
.faq-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  text-align: center;
  margin-bottom: 2rem;
}

.methods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.method-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.method-card:hover {
  transform: translateY(-5px);
}

.method-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.method-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.method-card p {
  color: #6b7280;
}

.security-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.security-item {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.security-item h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.security-item p {
  color: #6b7280;
}

.faq-list {
  max-width: 800px;
  margin: 0 auto;
}

.faq-item {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.faq-item h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.faq-item p {
  color: #6b7280;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .methods-grid,
  .security-features {
    grid-template-columns: 1fr;
  }
}
</style>