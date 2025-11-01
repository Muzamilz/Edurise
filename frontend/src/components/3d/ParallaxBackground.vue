<template>
  <div class="parallax-background" ref="backgroundRef">
    <!-- Animated gradient background -->
    <div class="gradient-layer layer-1"></div>
    <div class="gradient-layer layer-2"></div>
    <div class="gradient-layer layer-3"></div>
    
    <!-- Floating particles -->
    <div class="particles-container">
      <div 
        v-for="particle in particles" 
        :key="particle.id"
        class="particle"
        :style="particle.style"
        :data-speed="particle.speed"
      ></div>
    </div>
    
    <!-- 3D Educational Items -->
    <GeometricShapes />
    
    <!-- Floating Books -->
    <FloatingBooks />
    
    <!-- Interactive light rays -->
    <div class="light-rays">
      <div 
        v-for="ray in lightRays" 
        :key="ray.id"
        class="light-ray"
        :style="ray.style"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import GeometricShapes from './GeometricShapes.vue' // Now contains educational items
import FloatingBooks from './FloatingBooks.vue'

interface Particle {
  id: number
  style: Record<string, string>
  speed: number
}

interface LightRay {
  id: number
  style: Record<string, string>
}

const backgroundRef = ref<HTMLElement>()
const particles = ref<Particle[]>([])
const lightRays = ref<LightRay[]>([])

const generateParticles = () => {
  const particleCount = 25
  const newParticles: Particle[] = []

  for (let i = 0; i < particleCount; i++) {
    const particle: Particle = {
      id: i,
      style: {
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        animationDelay: `${Math.random() * 10}s`,
        animationDuration: `${15 + Math.random() * 10}s`,
        opacity: `${0.1 + Math.random() * 0.3}`,
        transform: `scale(${0.5 + Math.random() * 1.5})`
      },
      speed: 0.2 + Math.random() * 0.8
    }
    newParticles.push(particle)
  }

  particles.value = newParticles
}

const generateLightRays = () => {
  const rayCount = 8
  const newRays: LightRay[] = []

  for (let i = 0; i < rayCount; i++) {
    const ray: LightRay = {
      id: i,
      style: {
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        transform: `rotate(${Math.random() * 360}deg)`,
        animationDelay: `${Math.random() * 5}s`,
        animationDuration: `${20 + Math.random() * 10}s`,
        opacity: `${0.05 + Math.random() * 0.15}`
      }
    }
    newRays.push(ray)
  }

  lightRays.value = newRays
}

let animationId: number

const handleScroll = () => {
  if (!backgroundRef.value) return

  const scrollY = window.scrollY
  const particles = backgroundRef.value.querySelectorAll('.particle')
  const gradientLayers = backgroundRef.value.querySelectorAll('.gradient-layer')
  const lightRays = backgroundRef.value.querySelectorAll('.light-ray')
  
  // Animate particles
  particles.forEach((particle, index) => {
    const speed = parseFloat(particle.getAttribute('data-speed') || '1')
    const yPos = -(scrollY * speed * 0.05)
    const rotation = scrollY * 0.02 + index * 10
    
    ;(particle as HTMLElement).style.transform = `
      translateY(${yPos}px) 
      rotate(${rotation}deg)
      scale(${0.5 + Math.sin(scrollY * 0.01 + index) * 0.3})
    `
  })
  
  // Animate gradient layers
  gradientLayers.forEach((layer, index) => {
    const speed = (index + 1) * 0.02
    const yPos = -(scrollY * speed)
    ;(layer as HTMLElement).style.transform = `translateY(${yPos}px)`
  })
  
  // Animate light rays
  lightRays.forEach((ray, index) => {
    const rotation = scrollY * 0.01 + index * 45
    const scale = 1 + Math.sin(scrollY * 0.005 + index) * 0.2
    ;(ray as HTMLElement).style.transform = `
      rotate(${rotation}deg) 
      scale(${scale})
    `
  })
}

onMounted(() => {
  generateParticles()
  generateLightRays()
  window.addEventListener('scroll', handleScroll, { passive: true })
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped>
.parallax-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.gradient-layer {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  opacity: 0.3;
  animation: gradientShift 30s ease-in-out infinite;
}

.layer-1 {
  background: radial-gradient(circle at 20% 30%, rgba(245, 158, 11, 0.2) 0%, transparent 50%);
  animation-delay: 0s;
}

.layer-2 {
  background: radial-gradient(circle at 80% 70%, rgba(217, 119, 6, 0.15) 0%, transparent 50%);
  animation-delay: 10s;
}

.layer-3 {
  background: radial-gradient(circle at 50% 50%, rgba(146, 64, 14, 0.1) 0%, transparent 50%);
  animation-delay: 20s;
}

.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.8) 0%, rgba(245, 158, 11, 0.2) 50%, transparent 100%);
  border-radius: 50%;
  animation: particleFloat 20s linear infinite;
}

.light-rays {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.light-ray {
  position: absolute;
  width: 200px;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(245, 158, 11, 0.3) 20%, 
    rgba(245, 158, 11, 0.6) 50%, 
    rgba(245, 158, 11, 0.3) 80%, 
    transparent 100%
  );
  transform-origin: center;
  animation: rayPulse 15s ease-in-out infinite;
  filter: blur(1px);
}

@keyframes gradientShift {
  0%, 100% {
    transform: translateX(0%) translateY(0%) rotate(0deg);
  }
  25% {
    transform: translateX(-10%) translateY(-5%) rotate(90deg);
  }
  50% {
    transform: translateX(-5%) translateY(-10%) rotate(180deg);
  }
  75% {
    transform: translateX(5%) translateY(5%) rotate(270deg);
  }
}

@keyframes particleFloat {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100px) rotate(360deg);
    opacity: 0;
  }
}

@keyframes rayPulse {
  0%, 100% {
    opacity: 0.1;
    transform: scale(1) rotate(0deg);
  }
  50% {
    opacity: 0.4;
    transform: scale(1.2) rotate(180deg);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .light-ray {
    width: 100px;
    height: 1px;
  }
  
  .particle {
    width: 3px;
    height: 3px;
  }
  
  .gradient-layer {
    opacity: 0.2;
  }
}

/* Reduce motion for users who prefer it */
@media (prefers-reduced-motion: reduce) {
  .particle,
  .light-ray,
  .gradient-layer {
    animation: none;
  }
  
  .parallax-background * {
    transform: none !important;
  }
}
</style>