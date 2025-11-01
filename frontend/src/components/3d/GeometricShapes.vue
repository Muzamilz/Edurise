<template>
  <div class="educational-items-container" ref="containerRef">
    <div 
      v-for="item in educationalItems" 
      :key="item.id"
      class="educational-item"
      :class="item.type"
      :style="item.style"
      :data-speed="item.speed"
    >
      <div class="item-3d" :class="item.type">
        <!-- Pencil -->
        <template v-if="item.type === 'pencil'">
          <div class="pencil-body" :style="{ backgroundColor: item.color }">
            <div class="pencil-stripes"></div>
            <div class="pencil-brand">{{ item.brand }}</div>
          </div>
          <div class="pencil-tip"></div>
          <div class="pencil-eraser" :style="{ backgroundColor: item.eraserColor }"></div>
          <div class="pencil-ferrule"></div>
        </template>
        
        <!-- Pen -->
        <template v-if="item.type === 'pen'">
          <div class="pen-body" :style="{ backgroundColor: item.color }">
            <div class="pen-clip"></div>
            <div class="pen-grip"></div>
            <div class="pen-logo">{{ item.brand }}</div>
          </div>
          <div class="pen-tip"></div>
          <div class="pen-cap" :style="{ backgroundColor: item.capColor }"></div>
        </template>
        
        <!-- Notebook -->
        <template v-if="item.type === 'notebook'">
          <div class="notebook-cover" :style="{ backgroundColor: item.color }">
            <div class="notebook-title">{{ item.subject }}</div>
            <div class="notebook-lines"></div>
            <div class="notebook-corner"></div>
          </div>
          <div class="notebook-spine" :style="{ backgroundColor: item.spineColor }"></div>
          <div class="notebook-pages"></div>
        </template>
        
        <!-- Eraser -->
        <template v-if="item.type === 'eraser'">
          <div class="eraser-body" :style="{ backgroundColor: item.color }">
            <div class="eraser-brand">{{ item.brand }}</div>
            <div class="eraser-texture"></div>
          </div>
        </template>
        
        <!-- Ruler -->
        <template v-if="item.type === 'ruler'">
          <div class="ruler-body" :style="{ backgroundColor: item.color }">
            <div class="ruler-markings">
              <div v-for="mark in 12" :key="mark" class="ruler-mark" :class="{ major: mark % 5 === 0 }">
                <span v-if="mark % 5 === 0" class="ruler-number">{{ mark }}</span>
              </div>
            </div>
          </div>
        </template>
        
        <!-- Calculator -->
        <template v-if="item.type === 'calculator'">
          <div class="calculator-body" :style="{ backgroundColor: item.color }">
            <div class="calculator-screen">{{ item.display }}</div>
            <div class="calculator-buttons">
              <div class="calc-btn" v-for="btn in calculatorButtons" :key="btn">{{ btn }}</div>
            </div>
            <div class="calculator-brand">{{ item.brand }}</div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface EducationalItem {
  id: number
  type: 'pencil' | 'pen' | 'notebook' | 'eraser' | 'ruler' | 'calculator'
  color: string
  brand?: string
  subject?: string
  display?: string
  eraserColor?: string
  capColor?: string
  spineColor?: string
  style: Record<string, string>
  speed: number
}

const containerRef = ref<HTMLElement>()
const educationalItems = ref<EducationalItem[]>([])

const itemTypes: Array<'pencil' | 'pen' | 'notebook' | 'eraser' | 'ruler' | 'calculator'> = 
  ['pencil', 'pen', 'notebook', 'eraser', 'ruler', 'calculator']

const colors = [
  '#f59e0b', '#d97706', '#92400e', '#fbbf24', '#f3a847',
  '#ea580c', '#dc2626', '#7c2d12', '#a16207', '#ca8a04',
  '#f97316', '#fb923c', '#fdba74', '#fed7aa', '#3b82f6', 
  '#10b981', '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16'
]

const brands = ['EduRise', 'StudyPro', 'LearnMax', 'AcademiX', 'ScholarTech', 'BrainBoost']
const subjects = ['Math', 'Science', 'History', 'English', 'Art', 'Music', 'Code', 'Design']
const calculatorButtons = ['7', '8', '9', '+', '4', '5', '6', '-', '1', '2', '3', '×', '0', '.', '=', '÷']

const generateEducationalItems = () => {
  const itemCount = 18
  const newItems: EducationalItem[] = []

  for (let i = 0; i < itemCount; i++) {
    const type = itemTypes[i % itemTypes.length]
    const baseColor = colors[i % colors.length]
    
    const item: EducationalItem = {
      id: i,
      type,
      color: baseColor,
      brand: brands[i % brands.length],
      subject: subjects[i % subjects.length],
      display: Math.floor(Math.random() * 999).toString(),
      eraserColor: colors[(i + 3) % colors.length],
      capColor: adjustBrightness(baseColor, -20),
      spineColor: adjustBrightness(baseColor, -15),
      style: {
        left: `${Math.random() * 85 + 5}%`,
        top: `${Math.random() * 70 + 15}%`,
        animationDelay: `${Math.random() * 10}s`,
        animationDuration: `${15 + Math.random() * 10}s`
      },
      speed: 0.4 + Math.random() * 1.0
    }
    newItems.push(item)
  }

  educationalItems.value = newItems
}

const adjustBrightness = (hex: string, percent: number) => {
  const num = parseInt(hex.replace('#', ''), 16)
  const amt = Math.round(2.55 * percent)
  const R = (num >> 16) + amt
  const G = (num >> 8 & 0x00FF) + amt
  const B = (num & 0x0000FF) + amt
  return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
    (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
    (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1)
}

const handleScroll = () => {
  if (!containerRef.value) return

  const scrollY = window.scrollY
  const items = containerRef.value.querySelectorAll('.educational-item')
  
  items.forEach((item, index) => {
    const speed = parseFloat(item.getAttribute('data-speed') || '1')
    const yPos = -(scrollY * speed * 0.06)
    const rotationX = scrollY * 0.02 + index * 30
    const rotationY = scrollY * 0.015 + index * 25
    const rotationZ = Math.sin(scrollY * 0.008 + index) * 12
    const bounce = Math.sin(scrollY * 0.01 + index) * 5
    
    ;(item as HTMLElement).style.transform = `
      translateY(${yPos + bounce}px) 
      rotateX(${rotationX}deg) 
      rotateY(${rotationY}deg)
      rotateZ(${rotationZ}deg)
    `
  })
}

onMounted(() => {
  generateEducationalItems()
  window.addEventListener('scroll', handleScroll, { passive: true })
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.educational-items-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 1;
}

.educational-item {
  position: absolute;
  animation: float 18s ease-in-out infinite;
  transform-style: preserve-3d;
  perspective: 1000px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.item-3d {
  transform-style: preserve-3d;
  animation: gentleRotate 30s linear infinite;
}

/* Pencil Styles - Anime/Cartoon */
.item-3d.pencil {
  width: 12px;
  height: 80px;
}

.pencil-body {
  position: relative;
  width: 12px;
  height: 60px;
  border-radius: 6px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  box-shadow: 
    inset 2px 0 4px rgba(255, 255, 255, 0.6),
    inset -2px 0 4px rgba(0, 0, 0, 0.2);
}

.pencil-stripes {
  position: absolute;
  top: 10px;
  left: 0;
  right: 0;
  height: 20px;
  background: repeating-linear-gradient(
    0deg,
    rgba(255, 255, 255, 0.3) 0px,
    rgba(255, 255, 255, 0.3) 2px,
    transparent 2px,
    transparent 4px
  );
}

.pencil-brand {
  position: absolute;
  top: 35px;
  left: 50%;
  transform: translateX(-50%) rotate(90deg);
  font-size: 6px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
}

.pencil-tip {
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 12px solid #2d1810;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.pencil-eraser {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 10px;
  height: 8px;
  border-radius: 5px;
  border: 1px solid rgba(0, 0, 0, 0.2);
}

.pencil-ferrule {
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 14px;
  height: 6px;
  background: linear-gradient(45deg, #ffd700, #ffed4e);
  border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.2);
}

/* Pen Styles - Anime/Cartoon */
.item-3d.pen {
  width: 10px;
  height: 70px;
}

.pen-body {
  position: relative;
  width: 10px;
  height: 50px;
  border-radius: 5px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  box-shadow: 
    inset 1px 0 3px rgba(255, 255, 255, 0.6),
    inset -1px 0 3px rgba(0, 0, 0, 0.2);
}

.pen-clip {
  position: absolute;
  top: -5px;
  right: -3px;
  width: 3px;
  height: 15px;
  background: linear-gradient(45deg, #c0c0c0, #e0e0e0);
  border-radius: 1.5px;
  border: 1px solid rgba(0, 0, 0, 0.3);
}

.pen-grip {
  position: absolute;
  bottom: 5px;
  left: 0;
  right: 0;
  height: 15px;
  background: repeating-linear-gradient(
    90deg,
    rgba(0, 0, 0, 0.1) 0px,
    rgba(0, 0, 0, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
}

.pen-logo {
  position: absolute;
  top: 15px;
  left: 50%;
  transform: translateX(-50%) rotate(90deg);
  font-size: 5px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
}

.pen-tip {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 8px;
  background: linear-gradient(45deg, #2d1810, #4a2c1a);
  border-radius: 0 0 3px 3px;
}

.pen-cap {
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  height: 15px;
  border-radius: 6px 6px 2px 2px;
  border: 2px solid rgba(0, 0, 0, 0.2);
}

/* Notebook Styles - Anime/Cartoon */
.item-3d.notebook {
  width: 45px;
  height: 60px;
}

.notebook-cover {
  position: relative;
  width: 45px;
  height: 60px;
  border-radius: 3px;
  border: 2px solid rgba(0, 0, 0, 0.3);
  box-shadow: 
    inset 2px 2px 6px rgba(255, 255, 255, 0.4),
    inset -2px -2px 6px rgba(0, 0, 0, 0.2),
    0 4px 8px rgba(0, 0, 0, 0.3);
  transform: translateZ(4px);
}

.notebook-title {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 8px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  text-align: center;
}

.notebook-lines {
  position: absolute;
  top: 20px;
  left: 5px;
  right: 5px;
  bottom: 10px;
  background: repeating-linear-gradient(
    0deg,
    rgba(255, 255, 255, 0.2) 0px,
    rgba(255, 255, 255, 0.2) 1px,
    transparent 1px,
    transparent 6px
  );
}

.notebook-corner {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.2);
}

.notebook-spine {
  position: absolute;
  left: -4px;
  top: 0;
  width: 4px;
  height: 60px;
  border-radius: 2px 0 0 2px;
  border: 1px solid rgba(0, 0, 0, 0.3);
}

.notebook-pages {
  position: absolute;
  right: -2px;
  top: 2px;
  width: 2px;
  height: 56px;
  background: #f8f8f8;
  border-radius: 0 1px 1px 0;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
}

/* Eraser Styles - Anime/Cartoon */
.item-3d.eraser {
  width: 25px;
  height: 15px;
}

.eraser-body {
  position: relative;
  width: 25px;
  height: 15px;
  border-radius: 3px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  box-shadow: 
    inset 1px 1px 3px rgba(255, 255, 255, 0.6),
    inset -1px -1px 3px rgba(0, 0, 0, 0.2);
}

.eraser-brand {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 6px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.eraser-texture {
  position: absolute;
  top: 2px;
  left: 2px;
  right: 2px;
  bottom: 2px;
  background: repeating-linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.1) 0px,
    rgba(255, 255, 255, 0.1) 1px,
    transparent 1px,
    transparent 3px
  );
  border-radius: 1px;
}

/* Ruler Styles - Anime/Cartoon */
.item-3d.ruler {
  width: 80px;
  height: 12px;
}

.ruler-body {
  position: relative;
  width: 80px;
  height: 12px;
  border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.3);
  box-shadow: 
    inset 0 2px 4px rgba(255, 255, 255, 0.6),
    inset 0 -2px 4px rgba(0, 0, 0, 0.2);
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.2) 50%, transparent 100%);
}

.ruler-markings {
  position: absolute;
  top: 0;
  left: 5px;
  right: 5px;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.ruler-mark {
  width: 1px;
  height: 4px;
  background: rgba(0, 0, 0, 0.6);
  position: relative;
}

.ruler-mark.major {
  height: 8px;
  width: 1.5px;
  background: rgba(0, 0, 0, 0.8);
}

.ruler-number {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 4px;
  font-weight: bold;
  color: rgba(0, 0, 0, 0.7);
}

/* Calculator Styles - Anime/Cartoon */
.item-3d.calculator {
  width: 35px;
  height: 50px;
}

.calculator-body {
  position: relative;
  width: 35px;
  height: 50px;
  border-radius: 4px;
  border: 2px solid rgba(0, 0, 0, 0.3);
  box-shadow: 
    inset 1px 1px 4px rgba(255, 255, 255, 0.4),
    inset -1px -1px 4px rgba(0, 0, 0, 0.2),
    0 4px 8px rgba(0, 0, 0, 0.3);
}

.calculator-screen {
  position: absolute;
  top: 3px;
  left: 3px;
  right: 3px;
  height: 12px;
  background: #1a1a1a;
  border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 2px;
  font-size: 6px;
  color: #00ff00;
  font-family: 'Courier New', monospace;
}

.calculator-buttons {
  position: absolute;
  top: 18px;
  left: 3px;
  right: 3px;
  bottom: 8px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
}

.calc-btn {
  background: linear-gradient(45deg, #f0f0f0, #d0d0d0);
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4px;
  font-weight: bold;
  color: #333;
}

.calculator-brand {
  position: absolute;
  bottom: 1px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 4px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.5);
}

/* Animations */
@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotateX(0deg) rotateY(0deg) rotateZ(0deg);
  }
  25% {
    transform: translateY(-15px) rotateX(5deg) rotateY(10deg) rotateZ(3deg);
  }
  50% {
    transform: translateY(-8px) rotateX(-3deg) rotateY(15deg) rotateZ(-5deg);
  }
  75% {
    transform: translateY(-12px) rotateX(4deg) rotateY(-8deg) rotateZ(4deg);
  }
}

@keyframes gentleRotate {
  0% {
    transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg);
  }
  100% {
    transform: rotateX(360deg) rotateY(360deg) rotateZ(360deg);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .item-3d.pencil {
    width: 10px;
    height: 60px;
  }
  
  .pencil-body {
    width: 10px;
    height: 45px;
  }
  
  .item-3d.pen {
    width: 8px;
    height: 55px;
  }
  
  .pen-body {
    width: 8px;
    height: 40px;
  }
  
  .item-3d.notebook {
    width: 35px;
    height: 45px;
  }
  
  .notebook-cover {
    width: 35px;
    height: 45px;
  }
  
  .item-3d.eraser {
    width: 20px;
    height: 12px;
  }
  
  .eraser-body {
    width: 20px;
    height: 12px;
  }
  
  .item-3d.ruler {
    width: 60px;
    height: 10px;
  }
  
  .ruler-body {
    width: 60px;
    height: 10px;
  }
  
  .item-3d.calculator {
    width: 28px;
    height: 40px;
  }
  
  .calculator-body {
    width: 28px;
    height: 40px;
  }
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  .educational-item,
  .item-3d {
    animation: none;
  }
  
  .educational-items-container * {
    transform: none !important;
  }
}
</style>