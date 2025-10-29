/**
 * Notification Sound Utility
 * Creates notification sounds using Web Audio API for better browser compatibility
 */

export class NotificationSoundService {
  private audioContext: AudioContext | null = null
  private isEnabled = true

  constructor() {
    this.initializeAudioContext()
  }

  private initializeAudioContext() {
    try {
      // Don't create audio context immediately to avoid warnings
      // It will be created on first user interaction
      this.audioContext = null
    } catch (error) {
      console.warn('Web Audio API not supported:', error)
    }
  }

  /**
   * Enable or disable notification sounds
   */
  setEnabled(enabled: boolean) {
    this.isEnabled = enabled
  }

  /**
   * Play a simple notification beep
   */
  async playNotificationBeep() {
    if (!this.isEnabled || !this.audioContext) return

    try {
      // Resume audio context if suspended (required by some browsers)
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume()
      }

      const oscillator = this.audioContext.createOscillator()
      const gainNode = this.audioContext.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(this.audioContext.destination)

      // Create a pleasant notification sound
      oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime)
      oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime + 0.1)

      gainNode.gain.setValueAtTime(0, this.audioContext.currentTime)
      gainNode.gain.linearRampToValueAtTime(0.3, this.audioContext.currentTime + 0.01)
      gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3)

      oscillator.start(this.audioContext.currentTime)
      oscillator.stop(this.audioContext.currentTime + 0.3)
    } catch (error) {
      console.warn('Failed to play notification sound:', error)
    }
  }

  /**
   * Play an urgent notification sound (more prominent)
   */
  async playUrgentNotification() {
    if (!this.isEnabled || !this.audioContext) return

    try {
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume()
      }

      // Play two beeps for urgent notifications
      await this.playBeep(900, 0.15)
      setTimeout(() => this.playBeep(900, 0.15), 200)
    } catch (error) {
      console.warn('Failed to play urgent notification sound:', error)
    }
  }

  /**
   * Play a success sound
   */
  async playSuccessSound() {
    if (!this.isEnabled || !this.audioContext) return

    try {
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume()
      }

      // Play ascending notes for success
      await this.playBeep(523, 0.1) // C
      setTimeout(() => this.playBeep(659, 0.1), 100) // E
      setTimeout(() => this.playBeep(784, 0.15), 200) // G
    } catch (error) {
      console.warn('Failed to play success sound:', error)
    }
  }

  /**
   * Play a single beep with specified frequency and duration
   */
  private async playBeep(frequency: number, duration: number) {
    if (!this.audioContext) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime)
    
    gainNode.gain.setValueAtTime(0, this.audioContext.currentTime)
    gainNode.gain.linearRampToValueAtTime(0.2, this.audioContext.currentTime + 0.01)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration)

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + duration)
  }

  /**
   * Initialize audio context on user interaction (required by browsers)
   */
  async initializeOnUserGesture() {
    if (!this.audioContext) {
      try {
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      } catch (error) {
        console.warn('Web Audio API not supported:', error)
        return
      }
    }

    if (this.audioContext && this.audioContext.state === 'suspended') {
      try {
        await this.audioContext.resume()
      } catch (error) {
        console.warn('Failed to resume audio context:', error)
      }
    }
  }
}

// Create a singleton instance
export const notificationSoundService = new NotificationSoundService()

// Initialize on first user interaction
let isInitialized = false
const initializeOnFirstInteraction = () => {
  if (!isInitialized) {
    notificationSoundService.initializeOnUserGesture()
    isInitialized = true
    
    // Remove listeners after first initialization
    document.removeEventListener('click', initializeOnFirstInteraction)
    document.removeEventListener('keydown', initializeOnFirstInteraction)
    document.removeEventListener('touchstart', initializeOnFirstInteraction)
  }
}

// Add event listeners for user interaction
document.addEventListener('click', initializeOnFirstInteraction)
document.addEventListener('keydown', initializeOnFirstInteraction)
document.addEventListener('touchstart', initializeOnFirstInteraction)