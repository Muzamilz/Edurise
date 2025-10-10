<template>
  <div 
    class="ai-assistant-widget"
    :style="{ 
      bottom: position.y + 'px', 
      right: position.x + 'px' 
    }"
  >

    
    <!-- Floating AI Face Icon -->
    <div
      v-if="!isOpen"
      @click="openChat"
      @mousedown="startDrag"
      class="ai-face-button"
      :class="{ 'animate-bounce': shouldBounce, 'dragging': isDragging }"
      @mouseenter="onHover"
      @mouseleave="onLeave"
    >
      <!-- Teacher Icon Container -->
      <div class="teacher-icon-container">
        <!-- Background Circle -->
        <div class="teacher-bg"></div>
        
        <!-- Graduation Cap -->
        <div class="graduation-cap" :class="{ 'animate-bounce-cap': shouldBounce }">
          <div class="cap-top"></div>
          <div class="cap-base"></div>
          <div class="tassel" :class="{ 'swing': isBlinking }"></div>
        </div>
        
        <!-- Book -->
        <div class="book" :class="{ 'open': mouthState === 'happy' }">
          <div class="book-spine"></div>
          <div class="book-pages"></div>
          <div class="book-bookmark"></div>
        </div>
        
        <!-- AI Sparkles -->
        <div class="ai-sparkles">
          <div class="sparkle sparkle-1" :class="{ 'twinkle': isBlinking }"></div>
          <div class="sparkle sparkle-2" :class="{ 'twinkle': isBlinking }"></div>
          <div class="sparkle sparkle-3" :class="{ 'twinkle': isBlinking }"></div>
        </div>
        
        <!-- Notification Dot -->
        <div v-if="hasNotification" class="notification-dot"></div>
        
        <!-- Settings/Reset Position Button -->
        <button 
          @click.stop="resetPosition"
          class="reset-position-btn"
          title="Reset position"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
      
      <!-- Hover Tooltip -->
      <div 
        v-if="showTooltip && !isDragging" 
        class="tooltip"
        :class="tooltipPosition"
      >
        Hi! I'm your AI Teaching Assistant! 🎓
        <br><small>Drag to move • Click reset to restore position</small>
      </div>
      
      <!-- Drag Tooltip -->
      <div 
        v-if="isDragging" 
        class="drag-tooltip"
        :class="tooltipPosition"
      >
        Release to place here
      </div>
    </div>

    <!-- Chat Interface -->
    <div
      v-if="isOpen"
      class="chat-interface"
      :class="{ 
        'chat-open': isOpen, 
        'minimized': isMinimized,
        'has-unread': unreadCount > 0 && isMinimized
      }"
      :style="chatPosition"
    >
      <!-- Header -->
      <div class="chat-header">
        <div class="flex items-center space-x-3">
          <div class="ai-avatar">
            <div class="teacher-mini">
              <!-- Mini graduation cap -->
              <div class="cap-mini">
                <div class="cap-top-mini"></div>
                <div class="tassel-mini"></div>
              </div>
              <!-- Mini book -->
              <div class="book-mini"></div>
            </div>
          </div>
          <div>
            <div @click="isMinimized && toggleMinimize()" :class="{ 'cursor-pointer': isMinimized }">
              <h3 class="font-semibold text-white flex items-center">
                EduRise AI Teaching Assistant
                <span v-if="unreadCount > 0 && isMinimized" class="unread-badge">{{ unreadCount }}</span>
              </h3>
              <p class="text-xs text-orange-100">
                <span v-if="isTypingUser && !isMinimized">You are typing...</span>
                <span v-else-if="isTyping && !isMinimized">AI is thinking...</span>
                <span v-else>Your personal learning guide and tutor</span>
              </p>
            </div>
          </div>
        </div>
        
        <div class="chat-controls">
          <button @click="toggleMinimize" class="minimize-btn" title="Minimize">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
            </svg>
          </button>
          <button @click="closeChat" class="close-btn" title="Close">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Welcome Animation Overlay -->
      <div v-if="showWelcomeAnimation" class="welcome-overlay">
        <div class="welcome-content">
          <div class="welcome-icon">🎓</div>
          <div class="welcome-text">Welcome to EduRise!</div>
        </div>
      </div>

      <!-- Messages -->
      <div class="messages-container" ref="messagesContainer">
        <div
          v-for="message in messages"
          :key="message.id"
          class="message"
          :class="message.type === 'user' ? 'user-message' : 'ai-message'"
        >
          <div v-if="message.type === 'ai'" class="ai-avatar-small">
            <div class="teacher-tiny">
              <!-- Tiny graduation cap -->
              <div class="cap-tiny">
                <div class="cap-top-tiny"></div>
              </div>
              <!-- Tiny book -->
              <div class="book-tiny"></div>
            </div>
          </div>
          
          <div class="message-content">
            <div v-if="message.type === 'ai' && message.isTyping" class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div v-else v-html="message.content"></div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div v-if="showQuickActions" class="quick-actions">
        <button
          v-for="action in quickActions"
          :key="action.id"
          @click="selectQuickAction(action)"
          class="quick-action-btn"
        >
          {{ action.text }}
        </button>
      </div>

      <!-- Input -->
      <div class="chat-input">
        <div class="input-container">
          <textarea
            ref="messageInput"
            v-model="userInput"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.enter.shift.exact="userInput += '\n'"
            @input="handleInputChange"
            placeholder="Ask me anything about EduRise... (Shift+Enter for new line)"
            class="message-input"
            :disabled="isTyping"
            rows="1"
          ></textarea>
          <button
            @click="sendMessage"
            :disabled="!userInput.trim() || isTyping"
            class="send-btn"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Background Overlay -->
    <div
      v-if="isOpen"
      @click="closeChat"
      class="chat-overlay"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useAnimations } from '../../composables/useAnimations'

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
  isTyping?: boolean
}

interface QuickAction {
  id: string
  text: string
  response: string
}

// Composables
const { slideIn } = useAnimations()

// State
const isOpen = ref(false)
const userInput = ref('')
const messages = ref<Message[]>([])
const isTyping = ref(false)
const showTooltip = ref(false)
const shouldBounce = ref(false)
const hasNotification = ref(true)
const isBlinking = ref(false)
const eyePosition = ref({ x: 0, y: 0 })
const mouthState = ref('neutral')
const messagesContainer = ref<HTMLElement>()

// Enhanced UX state
const isMinimized = ref(false)
const unreadCount = ref(0)
const lastInteraction = ref(Date.now())
const showWelcomeAnimation = ref(false)
const isTypingUser = ref(false)
const messageInput = ref<HTMLTextAreaElement>()

// Draggable functionality
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const position = ref({ x: 20, y: 20 }) // Default position from bottom-right
const windowSize = ref({ width: 0, height: 0 })

// Quick actions for common questions
const quickActions = ref<QuickAction[]>([
  {
    id: '1',
    text: 'What is EduRise?',
    response: 'EduRise is a comprehensive Learning Management System that combines live classes, AI-powered tutoring, and interactive learning tools to provide an exceptional educational experience. 🎓'
  },
  {
    id: '2',
    text: 'How does AI tutoring work?',
    response: 'Our AI tutor provides personalized assistance 24/7! It can help with homework, generate quizzes, summarize content, and answer questions about your courses. It\'s like having a smart study buddy! 🤖✨'
  },
  {
    id: '3',
    text: 'What features do you offer?',
    response: 'We offer live virtual classes, AI-powered tutoring, content summarization, quiz generation, progress tracking, and much more! Everything you need for effective online learning. 📚💡'
  },
  {
    id: '4',
    text: 'How do I get started?',
    response: 'Getting started is easy! Simply sign up for an account, choose your courses, and start learning. You can join live classes or study at your own pace with our AI assistant. 🚀'
  },
  {
    id: '5',
    text: 'Show me pricing plans',
    response: 'We have flexible pricing options:<br/>• <strong>Basic Plan</strong>: $29/month - Live classes + AI tutoring<br/>• <strong>Pro Plan</strong>: $49/month - Everything + advanced analytics<br/>• <strong>Enterprise</strong>: Custom pricing for institutions<br/>All plans include a 14-day free trial! 💰'
  },
  {
    id: '6',
    text: 'What subjects are available?',
    response: 'We offer courses in:<br/>• Mathematics & Statistics<br/>• Computer Science & Programming<br/>• Sciences (Physics, Chemistry, Biology)<br/>• Languages & Literature<br/>• Business & Economics<br/>• Arts & Design<br/>And many more! What interests you? 📖'
  }
])

const showQuickActions = computed(() => messages.value.length <= 1)

// Dynamic chat positioning based on icon position
const chatPosition = computed(() => {
  // Default fallback if window is not available (SSR)
  if (typeof window === 'undefined') {
    return {
      bottom: '80px',
      right: '0px'
    }
  }
  
  const iconX = position.value.x
  const iconY = position.value.y
  const chatWidth = 350
  const chatHeight = 500
  const margin = 20
  const screenWidth = window.innerWidth
  const screenHeight = window.innerHeight
  
  // Calculate position relative to screen edges
  const iconFromLeft = screenWidth - iconX - 70 // Distance from left edge
  const iconFromTop = screenHeight - iconY - 70 // Distance from top edge
  
  let styles: Record<string, string> = {}
  
  // Horizontal positioning
  if (iconFromLeft > screenWidth / 2) {
    // Icon is on left side - show chat to the right
    styles.left = (iconFromLeft + 80) + 'px'
  } else {
    // Icon is on right side - show chat to the left
    styles.right = (iconX + 80) + 'px'
  }
  
  // Vertical positioning
  if (iconFromTop > screenHeight / 2) {
    // Icon is in top half - show chat below
    styles.top = (iconFromTop + 80) + 'px'
  } else {
    // Icon is in bottom half - show chat above
    styles.bottom = (iconY + 80) + 'px'
  }
  
  // Boundary checks to ensure chat stays on screen
  if (styles.left && parseInt(styles.left) + chatWidth > screenWidth - margin) {
    delete styles.left
    styles.right = margin + 'px'
  }
  
  if (styles.right && parseInt(styles.right) + chatWidth > screenWidth - margin) {
    delete styles.right
    styles.left = margin + 'px'
  }
  
  if (styles.top && parseInt(styles.top) + chatHeight > screenHeight - margin) {
    delete styles.top
    styles.bottom = margin + 'px'
  }
  
  if (styles.bottom && parseInt(styles.bottom) + chatHeight > screenHeight - margin) {
    delete styles.bottom
    styles.top = margin + 'px'
  }
  
  return styles
})

// Dynamic tooltip positioning
const tooltipPosition = computed(() => {
  if (typeof window === 'undefined') return 'tooltip-bottom'
  
  const iconY = position.value.y
  const screenHeight = window.innerHeight
  const iconFromTop = screenHeight - iconY - 70
  
  // If icon is in top half, show tooltip below
  if (iconFromTop > screenHeight / 2) {
    return 'tooltip-bottom'
  } else {
    return 'tooltip-top'
  }
})

// Face animations
let blinkInterval: NodeJS.Timeout
let bounceTimeout: NodeJS.Timeout
let mouseTracker: (e: MouseEvent) => void

// Methods
const openChat = () => {
  isOpen.value = true
  isMinimized.value = false
  hasNotification.value = false
  shouldBounce.value = false
  unreadCount.value = 0
  
  // Add welcome message if first time
  if (messages.value.length === 0) {
    showWelcomeExperience()
    setTimeout(() => {
      addAIMessageEnhanced('Hello! 🎓 Welcome to EduRise! I\'m your AI Teaching Assistant and I\'m here to help you learn about our educational platform. What would you like to know?')
    }, 500)
  }
  
  nextTick(() => {
    const chatInterface = document.querySelector('.chat-interface')
    if (chatInterface) {
      slideIn(chatInterface, 'up', { duration: 400, easing: 'easeOutBack' })
    }
    
    // Auto-focus input
    if (messageInput.value) {
      messageInput.value.focus()
    }
  })
}

const closeChat = () => {
  isOpen.value = false
  userInput.value = ''
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isTyping.value) return

  const message = userInput.value.trim()
  userInput.value = ''

  // Add user message
  addUserMessage(message)

  // Reset typing state
  isTypingUser.value = false
  
  // Show typing indicator
  isTyping.value = true
  const typingMessage = addAIMessage('', true)

  // Simulate AI response delay with more realistic timing
  const responseDelay = 800 + Math.random() * 1500
  await new Promise(resolve => setTimeout(resolve, responseDelay))

  // Remove typing indicator
  messages.value = messages.value.filter(m => m.id !== typingMessage.id)
  isTyping.value = false

  // Generate AI response
  const response = generateAIResponse(message)
  addAIMessageEnhanced(response)
  
  // Auto-resize input back to single line
  if (messageInput.value) {
    messageInput.value.style.height = 'auto'
  }
}

const selectQuickAction = (action: QuickAction) => {
  addUserMessage(action.text)
  
  setTimeout(() => {
    addAIMessage(action.response)
  }, 500)
}

const addUserMessage = (content: string) => {
  const message: Message = {
    id: `user-${Date.now()}`,
    type: 'user',
    content,
    timestamp: new Date()
  }
  messages.value.push(message)
  scrollToBottom()
}

const addAIMessage = (content: string, isTyping = false) => {
  const message: Message = {
    id: `ai-${Date.now()}`,
    type: 'ai',
    content,
    timestamp: new Date(),
    isTyping
  }
  messages.value.push(message)
  scrollToBottom()
  return message
}

const generateAIResponse = (userMessage: string): string => {
  const lowerMessage = userMessage.toLowerCase()
  
  // Simple keyword-based responses
  if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('pricing')) {
    return 'We offer flexible pricing plans to suit different needs! Our basic plan starts at $29/month with access to live classes and AI tutoring. Check out our pricing page for detailed information! 💰'
  }
  
  if (lowerMessage.includes('ai') || lowerMessage.includes('artificial intelligence')) {
    return 'Our AI technology is designed to enhance your learning experience! It can provide personalized tutoring, generate practice quizzes, summarize complex content, and answer your questions 24/7. It\'s like having a personal tutor that never sleeps! 🤖🧠'
  }
  
  if (lowerMessage.includes('live class') || lowerMessage.includes('zoom') || lowerMessage.includes('virtual')) {
    return 'Our live classes are conducted through integrated video conferencing with features like screen sharing, breakout rooms, and interactive whiteboards. You can attend from anywhere and interact with instructors and classmates in real-time! 📹👥'
  }
  
  if (lowerMessage.includes('mobile') || lowerMessage.includes('app') || lowerMessage.includes('phone')) {
    return 'Yes! EduRise works perfectly on mobile devices through your web browser. We\'re also working on dedicated mobile apps for iOS and Android. You can learn on-the-go! 📱✨'
  }
  
  if (lowerMessage.includes('support') || lowerMessage.includes('help') || lowerMessage.includes('contact')) {
    return 'We provide 24/7 support through multiple channels! You can reach us via live chat, email, or phone. Our support team is always ready to help you succeed in your learning journey! 🎧💬'
  }
  
  if (lowerMessage.includes('demo') || lowerMessage.includes('trial') || lowerMessage.includes('free')) {
    return 'Absolutely! We offer a 14-day free trial so you can explore all our features. No credit card required! You can also schedule a personalized demo with our team. Ready to get started? 🎯'
  }
  
  if (lowerMessage.includes('course') || lowerMessage.includes('subject') || lowerMessage.includes('learn')) {
    return 'We offer courses in various subjects including Mathematics, Science, Programming, Languages, Business, and more! Our AI adapts to your learning style and pace. What subject interests you most? 📖'
  }
  
  if (lowerMessage.includes('teacher') || lowerMessage.includes('instructor') || lowerMessage.includes('expert')) {
    return 'Our platform features certified instructors and subject matter experts from top universities and companies. They conduct live classes and provide personalized feedback. Plus, our AI tutor is available 24/7! 👨‍🏫'
  }
  
  if (lowerMessage.includes('technology') || lowerMessage.includes('tech') || lowerMessage.includes('platform')) {
    return 'EduRise is built with cutting-edge technology including AI/ML, real-time video streaming, interactive whiteboards, and cloud-based infrastructure. We ensure a seamless learning experience across all devices! 💻'
  }
  
  // Default responses
  const defaultResponses = [
    'That\'s a great question! EduRise is designed to make learning more effective and engaging. Would you like to know more about any specific feature? 🤔',
    'I\'d be happy to help you with that! EduRise offers comprehensive learning solutions. What aspect interests you most? 📚',
    'Thanks for asking! Our platform combines the best of traditional and modern learning methods. Is there something specific you\'d like to explore? 🚀',
    'Great to hear from you! EduRise is all about empowering learners with cutting-edge technology. What would you like to discover? 💡'
  ]
  
  return defaultResponses[Math.floor(Math.random() * defaultResponses.length)]
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const onHover = () => {
  showTooltip.value = true
  mouthState.value = 'happy'
}

const onLeave = () => {
  showTooltip.value = false
  mouthState.value = 'neutral'
}

// Drag functionality
const startDrag = (e: MouseEvent) => {
  if (isOpen.value) return // Don't drag when chat is open
  
  isDragging.value = true
  const rect = (e.target as HTMLElement).getBoundingClientRect()
  dragOffset.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  e.preventDefault()
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  
  const newX = window.innerWidth - (e.clientX - dragOffset.value.x + 70) // 70 is widget width
  const newY = window.innerHeight - (e.clientY - dragOffset.value.y + 70) // 70 is widget height
  
  // Keep within bounds
  position.value.x = Math.max(20, Math.min(newX, window.innerWidth - 90))
  position.value.y = Math.max(20, Math.min(newY, window.innerHeight - 90))
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  
  // Save position to localStorage
  localStorage.setItem('ai-widget-position', JSON.stringify(position.value))
}

const resetPosition = () => {
  position.value = { x: 20, y: 20 }
  localStorage.removeItem('ai-widget-position')
}

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
  if (!isMinimized.value) {
    unreadCount.value = 0
    // Auto-focus input when maximizing
    nextTick(() => {
      if (messageInput.value) {
        messageInput.value.focus()
      }
    })
  }
}

// Enhanced message handling with better UX
const addAIMessageEnhanced = (content: string, isTyping = false) => {
  const message = addAIMessage(content, isTyping)
  
  // Increment unread count if minimized
  if (isMinimized.value && !isTyping) {
    unreadCount.value++
  }
  
  // Update last interaction time
  lastInteraction.value = Date.now()
  
  return message
}

// Auto-resize textarea and typing indicators
const handleInputChange = () => {
  // Auto-resize textarea
  if (messageInput.value) {
    messageInput.value.style.height = 'auto'
    messageInput.value.style.height = messageInput.value.scrollHeight + 'px'
  }
  
  // Show typing indicator
  isTypingUser.value = userInput.value.length > 0
  
  // Update last interaction
  lastInteraction.value = Date.now()
}

// Enhanced welcome experience
const showWelcomeExperience = () => {
  showWelcomeAnimation.value = true
  setTimeout(() => {
    showWelcomeAnimation.value = false
  }, 2000)
}

const startFaceAnimations = () => {
  // Blinking animation
  blinkInterval = setInterval(() => {
    isBlinking.value = true
    setTimeout(() => {
      isBlinking.value = false
    }, 150)
  }, 3000 + Math.random() * 2000)

  // Periodic bounce to attract attention
  const scheduleBounce = () => {
    bounceTimeout = setTimeout(() => {
      if (!isOpen.value && hasNotification.value) {
        shouldBounce.value = true
        setTimeout(() => {
          shouldBounce.value = false
        }, 1000)
      }
      scheduleBounce()
    }, 8000 + Math.random() * 5000)
  }
  scheduleBounce()

  // Mouse tracking for eyes
  mouseTracker = (e: MouseEvent) => {
    if (isOpen.value) return
    
    const faceButton = document.querySelector('.ai-face-button')
    if (!faceButton) return
    
    const rect = faceButton.getBoundingClientRect()
    const faceCenterX = rect.left + rect.width / 2
    const faceCenterY = rect.top + rect.height / 2
    
    const deltaX = e.clientX - faceCenterX
    const deltaY = e.clientY - faceCenterY
    
    const maxDistance = 3
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
    const normalizedDistance = Math.min(distance / 100, 1)
    
    eyePosition.value = {
      x: (deltaX / distance) * maxDistance * normalizedDistance || 0,
      y: (deltaY / distance) * maxDistance * normalizedDistance || 0
    }
  }
  
  document.addEventListener('mousemove', mouseTracker)
}

const stopFaceAnimations = () => {
  if (blinkInterval) clearInterval(blinkInterval)
  if (bounceTimeout) clearTimeout(bounceTimeout)
  if (mouseTracker) document.removeEventListener('mousemove', mouseTracker)
}

// Lifecycle
onMounted(() => {
  // Load saved position from localStorage
  const savedPosition = localStorage.getItem('ai-widget-position')
  if (savedPosition) {
    try {
      position.value = JSON.parse(savedPosition)
    } catch (e) {
      console.warn('Failed to parse saved position:', e)
    }
  }
  
  // Initialize window size
  windowSize.value = {
    width: window.innerWidth,
    height: window.innerHeight
  }
  
  // Handle window resize
  const handleResize = () => {
    windowSize.value = {
      width: window.innerWidth,
      height: window.innerHeight
    }
  }
  
  window.addEventListener('resize', handleResize)
  
  startFaceAnimations()
  
  // Show initial bounce after a delay
  setTimeout(() => {
    shouldBounce.value = true
    setTimeout(() => {
      shouldBounce.value = false
    }, 1000)
  }, 3000)
})

onUnmounted(() => {
  stopFaceAnimations()
  // Clean up drag event listeners
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  // Clean up resize listener
  window.removeEventListener('resize', () => {})
})
</script>

<style scoped>
.ai-assistant-widget {
  position: fixed;
  z-index: 9999;
  pointer-events: auto;
  transition: all 0.3s ease;
}

/* AI Face Button */
.ai-face-button {
  position: relative;
  width: 70px;
  height: 70px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.ai-face-button:hover {
  transform: scale(1.1);
}

.ai-face-button.dragging {
  cursor: grabbing;
  transform: scale(1.05);
  z-index: 10000;
}

.ai-face-button:not(.dragging) {
  cursor: grab;
}

.ai-face-button.animate-bounce {
  animation: bounce 1s infinite;
}

.teacher-icon-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.teacher-bg {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  background-color: #f59e0b; /* fallback */
  border-radius: 50%;
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
  border: 3px solid #ffffff;
}

/* Graduation Cap */
.graduation-cap {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
}

.cap-top {
  width: 24px;
  height: 24px;
  background: #1f2937;
  border-radius: 2px;
  position: relative;
  transform: perspective(20px) rotateX(15deg);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.cap-base {
  width: 20px;
  height: 8px;
  background: #374151;
  border-radius: 10px;
  position: absolute;
  top: 18px;
  left: 2px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.tassel {
  position: absolute;
  top: 2px;
  right: -2px;
  width: 2px;
  height: 12px;
  background: #10b981;
  border-radius: 1px;
  transform-origin: top;
  transition: transform 0.3s ease;
}

.tassel.swing {
  transform: rotate(15deg);
}

.animate-bounce-cap {
  animation: bounceTeacher 0.6s ease-in-out;
}

/* Book */
.book {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
}

.book-spine {
  width: 16px;
  height: 12px;
  background: #dc2626;
  border-radius: 1px;
  position: relative;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.book-pages {
  width: 14px;
  height: 10px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0 1px 1px 0;
  position: absolute;
  top: 1px;
  right: -1px;
  transition: transform 0.3s ease;
}

.book.open .book-pages {
  transform: rotateY(-20deg);
}

.book-bookmark {
  width: 2px;
  height: 8px;
  background: #10b981;
  position: absolute;
  top: -2px;
  right: 2px;
  border-radius: 0 0 1px 1px;
}

/* AI Sparkles */
.ai-sparkles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.sparkle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #10b981;
  border-radius: 50%;
  opacity: 0.8;
  transition: all 0.3s ease;
}

.sparkle-1 {
  top: 15px;
  right: 8px;
  animation: twinkle1 2s infinite;
}

.sparkle-2 {
  bottom: 20px;
  right: 12px;
  animation: twinkle2 2.5s infinite;
  animation-delay: 0.5s;
}

.sparkle-3 {
  top: 25px;
  left: 10px;
  animation: twinkle3 3s infinite;
  animation-delay: 1s;
}

.sparkle.twinkle {
  transform: scale(1.5);
  opacity: 1;
}

/* Notification Dot */
.notification-dot {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 12px;
  height: 12px;
  background: #ef4444;
  border-radius: 50%;
  border: 2px solid white;
  animation: pulse 2s infinite;
}

/* Reset Position Button */
.reset-position-btn {
  position: absolute;
  top: -5px;
  left: -5px;
  width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e5e7eb;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
  color: #6b7280;
}

.ai-face-button:hover .reset-position-btn {
  opacity: 1;
}

.reset-position-btn:hover {
  background: #f3f4f6;
  color: #374151;
  transform: scale(1.1);
}

/* Tooltip */
.tooltip {
  position: absolute;
  right: 0;
  background: #1f2937;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: fadeInUp 0.3s ease;
  z-index: 10001;
}

.tooltip-bottom {
  bottom: 80px;
}

.tooltip-top {
  top: 80px;
}

.tooltip-bottom::after {
  content: '';
  position: absolute;
  top: 100%;
  right: 20px;
  border: 6px solid transparent;
  border-top-color: #1f2937;
}

.tooltip-top::after {
  content: '';
  position: absolute;
  bottom: 100%;
  right: 20px;
  border: 6px solid transparent;
  border-bottom-color: #1f2937;
}

/* Drag Tooltip */
.drag-tooltip {
  position: absolute;
  right: 0;
  background: #f59e0b;
  color: white;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
  animation: fadeInUp 0.2s ease;
  z-index: 10001;
}

.drag-tooltip.tooltip-bottom {
  bottom: 80px;
}

.drag-tooltip.tooltip-top {
  top: 80px;
}

.drag-tooltip.tooltip-bottom::after {
  content: '';
  position: absolute;
  top: 100%;
  right: 20px;
  border: 5px solid transparent;
  border-top-color: #f59e0b;
}

.drag-tooltip.tooltip-top::after {
  content: '';
  position: absolute;
  bottom: 100%;
  right: 20px;
  border: 5px solid transparent;
  border-bottom-color: #f59e0b;
}

/* Chat Interface */
.chat-interface {
  position: fixed;
  width: 350px;
  height: 500px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform: translateY(20px) scale(0.95);
  opacity: 0;
  transition: all 0.3s ease;
  z-index: 10000;
}

.chat-interface.chat-open {
  transform: translateY(0) scale(1);
  opacity: 1;
}

.chat-interface.minimized {
  height: 60px;
  overflow: hidden;
}

.chat-interface.minimized .messages-container,
.chat-interface.minimized .quick-actions,
.chat-interface.minimized .chat-input {
  display: none;
}

.chat-interface.has-unread {
  animation: gentlePulse 2s infinite;
}

/* Welcome Animation */
.welcome-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  border-radius: 16px;
  animation: welcomeFadeOut 2s ease-in-out forwards;
}

.welcome-content {
  text-align: center;
  color: white;
}

.welcome-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: bounceIn 0.8s ease-out;
}

.welcome-text {
  font-size: 1.2rem;
  font-weight: 600;
  animation: fadeInUp 0.8s ease-out 0.3s both;
}

.chat-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  z-index: -1;
}

/* Chat Header */
.chat-header {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.teacher-mini {
  position: relative;
  width: 24px;
  height: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.cap-mini {
  position: relative;
  margin-bottom: 2px;
}

.cap-top-mini {
  width: 12px;
  height: 8px;
  background: #1f2937;
  border-radius: 1px;
  position: relative;
}

.tassel-mini {
  position: absolute;
  top: 0;
  right: -1px;
  width: 1px;
  height: 6px;
  background: #10b981;
  border-radius: 0.5px;
}

.book-mini {
  width: 8px;
  height: 6px;
  background: #dc2626;
  border-radius: 0.5px;
  position: relative;
}

.book-mini::after {
  content: '';
  position: absolute;
  top: 0;
  right: -1px;
  width: 6px;
  height: 5px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 0 0.5px 0.5px 0;
}

.chat-controls {
  display: flex;
  gap: 4px;
}

.minimize-btn,
.close-btn {
  color: white;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
  background: transparent;
}

.minimize-btn:hover,
.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.unread-badge {
  background: #ef4444;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
  font-weight: bold;
  animation: pulse 2s infinite;
}

/* Messages */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  animation: slideInMessage 0.4s ease-out;
  margin-bottom: 4px;
}

.user-message {
  flex-direction: row-reverse;
}

.ai-avatar-small {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.teacher-tiny {
  position: relative;
  width: 16px;
  height: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.cap-tiny {
  position: relative;
  margin-bottom: 1px;
}

.cap-top-tiny {
  width: 8px;
  height: 5px;
  background: #1f2937;
  border-radius: 0.5px;
}

.book-tiny {
  width: 6px;
  height: 4px;
  background: #dc2626;
  border-radius: 0.5px;
  position: relative;
}

.book-tiny::after {
  content: '';
  position: absolute;
  top: 0;
  right: -0.5px;
  width: 4px;
  height: 3px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 0 0.5px 0.5px 0;
}

.message-content {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.4;
}

.user-message .message-content {
  background: #f59e0b;
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-message .message-content {
  background: #f3f4f6;
  color: #374151;
  border-bottom-left-radius: 4px;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #9ca3af;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

/* Quick Actions */
.quick-actions {
  padding: 12px 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-action-btn {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 12px;
  text-align: left;
  font-size: 13px;
  color: #374151;
  transition: all 0.2s;
  cursor: pointer;
}

.quick-action-btn:hover {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

/* Chat Input */
.chat-input {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
}

.input-container {
  display: flex;
  gap: 8px;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  resize: none;
  min-height: 36px;
  max-height: 120px;
  font-family: inherit;
  line-height: 1.4;
}

.message-input:focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.message-input::placeholder {
  color: #9ca3af;
}

.send-btn {
  width: 36px;
  height: 36px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #d97706;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Animations */
@keyframes bounce {
  0%, 20%, 53%, 80%, 100% { transform: translate3d(0,0,0); }
  40%, 43% { transform: translate3d(0,-15px,0); }
  70% { transform: translate3d(0,-7px,0); }
  90% { transform: translate3d(0,-2px,0); }
}

@keyframes bounceTeacher {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-3px); }
}

@keyframes twinkle1 {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

@keyframes twinkle2 {
  0%, 100% { opacity: 0.4; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.3); }
}

@keyframes twinkle3 {
  0%, 100% { opacity: 0.2; transform: scale(1.1); }
  50% { opacity: 0.9; transform: scale(1.4); }
}

@keyframes gentlePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

@keyframes slideInMessage {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes welcomeFadeOut {
  0% { opacity: 1; }
  80% { opacity: 1; }
  100% { opacity: 0; pointer-events: none; }
}

@keyframes bounceIn {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .ai-assistant-widget {
    bottom: 15px;
    right: 15px;
  }
  
  .chat-interface {
    width: calc(100vw - 30px);
    height: calc(100vh - 120px);
    bottom: 85px;
    right: -15px;
  }
  
  .tooltip {
    display: none;
  }
}

/* Scrollbar */
.messages-container::-webkit-scrollbar {
  width: 4px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>