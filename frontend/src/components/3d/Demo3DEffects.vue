<template>
  <div class="demo-container">
    <h2>3D Effects Demo</h2>
    <p>Scroll down to see the 3D shapes and books animate with parallax effects!</p>
    
    <div class="demo-section">
      <h3>Floating Books</h3>
      <div class="demo-area books-demo">
        <FloatingBooks />
      </div>
    </div>
    
    <div class="demo-section">
      <h3>Educational Items (Anime Style)</h3>
      <div class="demo-area shapes-demo">
        <GeometricShapes />
      </div>
    </div>
    
    <div class="demo-section">
      <h3>Full Parallax Background</h3>
      <div class="demo-area parallax-demo">
        <ParallaxBackground />
        <div class="demo-content">
          <h4>Interactive 3D Environment</h4>
          <p>This combines all 3D elements with scroll-based animations</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import FloatingBooks from './FloatingBooks.vue'
import GeometricShapes from './GeometricShapes.vue'
import ParallaxBackground from './ParallaxBackground.vue'
</script>

<style scoped>
.demo-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.demo-section {
  margin-bottom: 3rem;
}

.demo-area {
  position: relative;
  height: 400px;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #92400e 100%);
}

.books-demo {
  background: linear-gradient(135deg, #fef3e2 0%, #fed7aa 100%);
}

.shapes-demo {
  background: linear-gradient(135deg, #ffffff 0%, #fef3e2 100%);
}

.parallax-demo {
  height: 600px;
}

.demo-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: white;
  z-index: 10;
}

.demo-content h4 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.demo-content p {
  font-size: 1.2rem;
  opacity: 0.9;
}

h2 {
  text-align: center;
  color: #92400e;
  margin-bottom: 1rem;
}

h3 {
  color: #d97706;
  margin-bottom: 1rem;
}

p {
  text-align: center;
  color: #6b7280;
  margin-bottom: 2rem;
}
</style>