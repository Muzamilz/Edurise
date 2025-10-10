<template>
  <div class="ai-tutor-chat h-full flex flex-col bg-white rounded-lg shadow-lg">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900">AI Tutor</h3>
          <p class="text-sm text-gray-500">
            {{ hasActiveConversation ? currentConversation?.title : 'Start a new conversation' }}
          </p>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex items-center space-x-2">
        <button
          @click="showConversationList = !showConversationList"
          class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          title="Conversation History"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </button>
        
        <button
          @click="startNewConversation"
          class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          title="New Conversation"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Conversation List Sidebar -->
    <div 
      v-if="showConversationList"
      class="absolute top-16 right-4 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-96 overflow-y-auto"
    >
      <div class="p-3 border-b border-gray-200">
        <h4 class="font-medium text-gray-900">Recent Conversations</h4>
      </div>
      <div class="p-2">
        <div
          v-for="conversation in conversations"
          :key="conversation.id"
          @click="selectConversationHandler(conversation.id)"
          class="p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          :class="{ 'bg-blue-50 border border-blue-200': currentConversation?.id === conversation.id }"
        >
          <div class="font-medium text-sm text-gray-900 truncate">
            {{ conversation.title }}
          </div>
          <div class="text-xs text-gray-500 mt-1">
            {{ formatDate(conversation.last_activity) }} • {{ conversation.message_count }} messages
          </div>
        </div>
        
        <div v-if="conversations.length === 0" class="p-3 text-center text-gray-500 text-sm">
          No conversations yet
        </div>
      </div>
    </div>

    <!-- Messages Area -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
      <!-- Welcome Message -->
      <div v-if="messages.length === 0" class="text-center py-8">
        <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">Welcome to AI Tutor!</h3>
        <p class="text-gray-600 max-w-md mx-auto">
          I'm here to help you learn and understand your course material. Ask me anything about your studies!
        </p>
      </div>

      <!-- Messages -->
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-item"
        :class="message.role === 'user' ? 'user-message' : 'ai-message'"
      >
        <div class="flex items-start space-x-3">
          <!-- Avatar -->
          <div class="flex-shrink-0">
            <div
              v-if="message.role === 'user'"
              class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center"
            >
              <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div
              v-else
              class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center"
            >
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
          </div>

          <!-- Message Content -->
          <div class="flex-1 min-w-0">
            <div
              class="message-bubble p-3 rounded-lg"
              :class="message.role === 'user' 
                ? 'bg-blue-600 text-white ml-auto max-w-xs' 
                : 'bg-gray-100 text-gray-900 max-w-2xl'"
            >
              <div class="whitespace-pre-wrap">{{ message.content }}</div>
              
              <!-- Message metadata -->
              <div
                v-if="message.role === 'assistant' && message.response_time_ms"
                class="text-xs text-gray-500 mt-2"
              >
                Response time: {{ message.response_time_ms }}ms
              </div>
            </div>
            
            <!-- Timestamp -->
            <div
              class="text-xs text-gray-500 mt-1"
              :class="message.role === 'user' ? 'text-right' : 'text-left'"
            >
              {{ formatTime(message.created_at) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="loading.chat" class="flex items-start space-x-3">
        <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div class="bg-gray-100 rounded-lg p-3">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="p-4 bg-red-50 border-t border-red-200">
      <div class="flex items-center space-x-2">
        <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-red-700 text-sm">{{ error.message }}</span>
        <button @click="clearError" class="text-red-500 hover:text-red-700">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Input Area -->
    <div class="p-4 border-t border-gray-200">
      <form @submit.prevent="handleSendMessage" class="flex space-x-3">
        <div class="flex-1">
          <textarea
            v-model="newMessage"
            @keydown.enter.exact.prevent="handleSendMessage"
            @keydown.enter.shift.exact="newMessage += '\n'"
            placeholder="Ask me anything about your studies..."
            rows="1"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            :disabled="loading.chat || !canUseFeature('chat')"
            ref="messageInput"
          ></textarea>
        </div>
        
        <button
          type="submit"
          :disabled="!newMessage.trim() || loading.chat || !canUseFeature('chat')"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg v-if="loading.chat" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </form>
      
      <!-- Usage warning -->
      <div v-if="!canUseFeature('chat')" class="mt-2 text-sm text-red-600">
        Chat quota exceeded. Please upgrade your plan or wait for next month.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useAI } from '@/composables/useAI'
import { useAnimations } from '@/composables/useAnimations'

// Props
interface Props {
  courseId?: string
  context?: Record<string, any>
}

const props = withDefaults(defineProps<Props>(), {
  context: () => ({})
})

// Composables
const {
  conversations,
  currentConversation,
  messages,
  loading,
  error,
  hasActiveConversation,
  loadConversations,
  createConversation,
  selectConversation,
  sendMessage,
  clearError,
  canUseFeature
} = useAI()

const { messageBubble } = useAnimations()

// Local state
const newMessage = ref('')
const showConversationList = ref(false)
const messagesContainer = ref<HTMLElement>()
const messageInput = ref<HTMLTextAreaElement>()

// Methods
const handleSendMessage = async () => {
  if (!newMessage.value.trim() || loading.chat) return

  const message = newMessage.value.trim()
  newMessage.value = ''

  try {
    // Create conversation if none exists
    if (!hasActiveConversation.value) {
      await createConversation({
        title: `Chat - ${new Date().toLocaleDateString()}`,
        conversation_type: 'tutor',
        context: {
          ...props.context,
          course_id: props.courseId
        }
      })
    }

    await sendMessage(message, {
      ...props.context,
      course_id: props.courseId
    })

    // Scroll to bottom
    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error('Failed to send message:', err)
  }
}

const startNewConversation = async () => {
  try {
    await createConversation({
      title: `New Chat - ${new Date().toLocaleDateString()}`,
      conversation_type: 'tutor',
      context: {
        ...props.context,
        course_id: props.courseId
      }
    })
    showConversationList.value = false
  } catch (err) {
    console.error('Failed to create conversation:', err)
  }
}

const selectConversationHandler = async (conversationId: string) => {
  try {
    await selectConversation(conversationId)
    showConversationList.value = false
    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error('Failed to select conversation:', err)
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

  if (diffInHours < 24) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } else if (diffInHours < 168) { // 7 days
    return date.toLocaleDateString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' })
  } else {
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }
}

const formatTime = (dateString: string) => {
  return new Date(dateString).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// Auto-resize textarea
const autoResize = () => {
  if (messageInput.value) {
    messageInput.value.style.height = 'auto'
    messageInput.value.style.height = messageInput.value.scrollHeight + 'px'
  }
}

// Watch for new messages and scroll to bottom
watch(messages, async () => {
  await nextTick()
  scrollToBottom()
  
  // Animate new messages with message bubble animation
  const messageItems = document.querySelectorAll('.message-item:last-child')
  if (messageItems.length > 0) {
    messageBubble(messageItems[messageItems.length - 1])
  }
}, { deep: true })

// Watch textarea content for auto-resize
watch(newMessage, autoResize)

// Initialize
onMounted(async () => {
  try {
    await loadConversations()
    
    // Auto-focus input
    if (messageInput.value) {
      messageInput.value.focus()
    }
  } catch (err) {
    console.error('Failed to initialize AI chat:', err)
  }
})
</script>

<style scoped>
/* Typing indicator animation */
.typing-indicator {
  display: flex;
  align-items: center;
  space-x: 1px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #9CA3AF;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
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

/* Message animations */
.message-item {
  opacity: 0;
  transform: translateY(10px);
  animation: messageSlideIn 0.3s ease-out forwards;
}

@keyframes messageSlideIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scrollbar styling */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>