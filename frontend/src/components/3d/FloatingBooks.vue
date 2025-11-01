<template>
  <div class="floating-books-container" ref="containerRef">
    <div 
      v-for="book in books" 
      :key="book.id"
      class="floating-book"
      :style="book.style"
      :data-speed="book.speed"
    >
      <div class="book-3d">
        <div class="book-front" :style="{ backgroundColor: book.color }">
          <div class="book-title">{{ book.title }}</div>
        </div>
        <div class="book-spine" :style="{ backgroundColor: book.spineColor }"></div>
        <div class="book-back" :style="{ backgroundColor: book.backColor }"></div>
        <div class="book-top" :style="{ backgroundColor: book.topColor }"></div>
        <div class="book-bottom" :style="{ backgroundColor: book.bottomColor }"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Book {
  id: number
  title: string
  color: string
  spineColor: string
  backColor: string
  topColor: string
  bottomColor: string
  style: Record<string, string>
  speed: number
}

const containerRef = ref<HTMLElement>()
const books = ref<Book[]>([])

const bookTitles = [
  'JavaScript', 'Python', 'React', 'Vue.js', 'Node.js', 'CSS', 'HTML', 'TypeScript',
  'Angular', 'Django', 'Flask', 'MongoDB', 'SQL', 'Git', 'Docker', 'AWS'
]

const colors = [
  '#f59e0b', '#d97706', '#92400e', '#fbbf24', '#f3a847',
  '#ea580c', '#dc2626', '#7c2d12', '#a16207', '#ca8a04'
]

const generateBooks = () => {
  const bookCount = 12
  const newBooks: Book[] = []

  for (let i = 0; i < bookCount; i++) {
    const baseColor = colors[i % colors.length]
    const book: Book = {
      id: i,
      title: bookTitles[i % bookTitles.length],
      color: baseColor,
      spineColor: adjustBrightness(baseColor, -20),
      backColor: adjustBrightness(baseColor, -10),
      topColor: adjustBrightness(baseColor, 10),
      bottomColor: adjustBrightness(baseColor, -30),
      style: {
        left: `${Math.random() * 90}%`,
        top: `${Math.random() * 80 + 10}%`,
        animationDelay: `${Math.random() * 5}s`,
        animationDuration: `${8 + Math.random() * 4}s`
      },
      speed: 0.5 + Math.random() * 1.5
    }
    newBooks.push(book)
  }

  books.value = newBooks
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

let animationId: number

const handleScroll = () => {
  if (!containerRef.value) return

  const scrollY = window.scrollY
  const books = containerRef.value.querySelectorAll('.floating-book')
  
  books.forEach((book, index) => {
    const speed = parseFloat(book.getAttribute('data-speed') || '1')
    const yPos = -(scrollY * speed * 0.1)
    const rotation = scrollY * 0.05 + index * 30
    
    ;(book as HTMLElement).style.transform = `
      translateY(${yPos}px) 
      rotateX(${rotation}deg) 
      rotateY(${rotation * 0.5}deg)
      rotateZ(${Math.sin(scrollY * 0.01 + index) * 10}deg)
    `
  })
}

onMounted(() => {
  generateBooks()
  window.addEventListener('scroll', handleScroll, { passive: true })
  handleScroll() // Initial call
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped>
.floating-books-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 1;
}

.floating-book {
  position: absolute;
  animation: float 10s ease-in-out infinite;
  transform-style: preserve-3d;
  perspective: 1000px;
}

.book-3d {
  width: 60px;
  height: 80px;
  position: relative;
  transform-style: preserve-3d;
  animation: gentleBookRotate 25s linear infinite;
  filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.3));
}

.book-front,
.book-back,
.book-spine,
.book-top,
.book-bottom {
  position: absolute;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.book-front {
  width: 60px;
  height: 80px;
  transform: translateZ(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  box-shadow: 
    inset 3px 3px 8px rgba(255, 255, 255, 0.4),
    inset -3px -3px 8px rgba(0, 0, 0, 0.2),
    0 0 15px rgba(0, 0, 0, 0.3);
  position: relative;
}

.book-front::before {
  content: '';
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  bottom: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  pointer-events: none;
}

.book-front::after {
  content: '📚';
  position: absolute;
  top: 5px;
  right: 5px;
  font-size: 12px;
  opacity: 0.6;
}

.book-title {
  color: white;
  font-size: 9px;
  font-weight: bold;
  text-align: center;
  text-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.5),
    0 0 8px rgba(0, 0, 0, 0.3);
  transform: rotate(-90deg);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70px;
  font-family: 'Comic Sans MS', cursive, sans-serif;
  letter-spacing: 0.5px;
}

.book-back {
  width: 60px;
  height: 80px;
  transform: translateZ(-8px) rotateY(180deg);
  border-radius: 4px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  box-shadow: 
    inset 2px 2px 6px rgba(255, 255, 255, 0.3),
    inset -2px -2px 6px rgba(0, 0, 0, 0.2);
}

.book-spine {
  width: 16px;
  height: 80px;
  transform: rotateY(-90deg) translateZ(8px);
  border-radius: 4px 0 0 4px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  box-shadow: 
    inset 2px 0 4px rgba(255, 255, 255, 0.4),
    inset -2px 0 4px rgba(0, 0, 0, 0.3);
  position: relative;
}

.book-spine::after {
  content: '';
  position: absolute;
  top: 10px;
  bottom: 10px;
  left: 2px;
  right: 2px;
  background: repeating-linear-gradient(
    0deg,
    rgba(255, 255, 255, 0.2) 0px,
    rgba(255, 255, 255, 0.2) 1px,
    transparent 1px,
    transparent 4px
  );
}

.book-top {
  width: 60px;
  height: 16px;
  transform: rotateX(90deg) translateZ(40px);
  border-radius: 2px 2px 0 0;
}

.book-bottom {
  width: 60px;
  height: 16px;
  transform: rotateX(-90deg) translateZ(40px);
  border-radius: 0 0 2px 2px;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotateX(0deg) rotateY(0deg);
  }
  25% {
    transform: translateY(-20px) rotateX(5deg) rotateY(5deg);
  }
  50% {
    transform: translateY(-10px) rotateX(-3deg) rotateY(10deg);
  }
  75% {
    transform: translateY(-15px) rotateX(3deg) rotateY(-5deg);
  }
}

@keyframes gentleBookRotate {
  0% {
    transform: rotateY(0deg) rotateX(0deg) rotateZ(0deg);
  }
  25% {
    transform: rotateY(90deg) rotateX(5deg) rotateZ(2deg);
  }
  50% {
    transform: rotateY(180deg) rotateX(-3deg) rotateZ(-2deg);
  }
  75% {
    transform: rotateY(270deg) rotateX(3deg) rotateZ(1deg);
  }
  100% {
    transform: rotateY(360deg) rotateX(0deg) rotateZ(0deg);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .book-3d {
    width: 40px;
    height: 55px;
  }
  
  .book-front,
  .book-back {
    width: 40px;
    height: 55px;
  }
  
  .book-spine {
    width: 12px;
    height: 55px;
  }
  
  .book-top,
  .book-bottom {
    width: 40px;
    height: 12px;
  }
  
  .book-title {
    font-size: 6px;
  }
}
</style>