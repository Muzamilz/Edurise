import anime from 'animejs/lib/anime.es.js'
import { nextTick } from 'vue'

export const useAnimations = () => {
  // Basic fade in animation
  const fadeIn = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      opacity: [0, 1],
      translateY: [20, 0],
      duration: 600,
      easing: 'easeOutQuart',
      ...options
    })
  }

  // Fade out animation
  const fadeOut = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      opacity: [1, 0],
      translateY: [0, -20],
      duration: 400,
      easing: 'easeInQuart',
      ...options
    })
  }

  // Slide in animation from different directions
  const slideIn = (
    target: string | Element | NodeList, 
    direction: 'left' | 'right' | 'up' | 'down' = 'left',
    options: Partial<anime.AnimeParams> = {}
  ) => {
    const transforms: Record<string, [number, number]> = {
      left: [-100, 0],
      right: [100, 0],
      up: [0, -100],
      down: [0, 100]
    }

    const [from, to] = transforms[direction]
    const property = direction === 'left' || direction === 'right' ? 'translateX' : 'translateY'

    return anime({
      targets: target,
      [property]: [from, to],
      opacity: [0, 1],
      duration: 800,
      easing: 'easeOutExpo',
      ...options
    })
  }

  // Slide out animation
  const slideOut = (
    target: string | Element | NodeList,
    direction: 'left' | 'right' | 'up' | 'down' = 'left',
    options: Partial<anime.AnimeParams> = {}
  ) => {
    const transforms: Record<string, [number, number]> = {
      left: [0, -100],
      right: [0, 100],
      up: [0, -100],
      down: [0, 100]
    }

    const [from, to] = transforms[direction]
    const property = direction === 'left' || direction === 'right' ? 'translateX' : 'translateY'

    return anime({
      targets: target,
      [property]: [from, to],
      opacity: [1, 0],
      duration: 600,
      easing: 'easeInExpo',
      ...options
    })
  }

  // Scale animation for buttons and interactive elements
  const scaleIn = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      scale: [0.8, 1],
      opacity: [0, 1],
      duration: 400,
      easing: 'easeOutBack',
      ...options
    })
  }

  // Button morph animation
  const morphButton = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      scale: [1, 1.05, 1],
      duration: 300,
      easing: 'easeInOutQuad',
      ...options
    })
  }

  // Pulse animation for notifications or highlights
  const pulse = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      scale: [1, 1.1, 1],
      duration: 1000,
      easing: 'easeInOutSine',
      loop: true,
      ...options
    })
  }

  // Shake animation for errors
  const shake = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      translateX: [0, -10, 10, -10, 10, 0],
      duration: 500,
      easing: 'easeInOutSine',
      ...options
    })
  }

  // Bounce animation
  const bounce = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      translateY: [0, -20, 0],
      duration: 600,
      easing: 'easeOutBounce',
      ...options
    })
  }

  // Rotate animation
  const rotate = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      rotate: [0, 360],
      duration: 1000,
      easing: 'easeInOutSine',
      ...options
    })
  }

  // Stagger animation for lists
  const staggerIn = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      opacity: [0, 1],
      translateY: [30, 0],
      duration: 600,
      delay: anime.stagger(100),
      easing: 'easeOutQuart',
      ...options
    })
  }

  // Loading spinner animation
  const spin = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      rotate: 360,
      duration: 1000,
      easing: 'linear',
      loop: true,
      ...options
    })
  }

  // Progress bar animation
  const progressBar = (
    target: string | Element | NodeList,
    percentage: number,
    options: Partial<anime.AnimeParams> = {}
  ) => {
    return anime({
      targets: target,
      width: `${percentage}%`,
      duration: 1000,
      easing: 'easeOutQuart',
      ...options
    })
  }

  // Typing indicator animation
  const typingIndicator = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      scale: [1, 1.2, 1],
      duration: 1400,
      delay: anime.stagger(200),
      easing: 'easeInOutSine',
      loop: true,
      ...options
    })
  }

  // Message bubble animation
  const messageBubble = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      scale: [0.8, 1],
      opacity: [0, 1],
      translateY: [20, 0],
      duration: 400,
      easing: 'easeOutBack',
      ...options
    })
  }

  // Card flip animation
  const flipCard = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      rotateY: [0, 180],
      duration: 600,
      easing: 'easeInOutSine',
      ...options
    })
  }

  // Smooth height animation
  const expandHeight = (target: string | Element | NodeList, height: number, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      height: height,
      duration: 400,
      easing: 'easeOutQuart',
      ...options
    })
  }

  // Collapse height animation
  const collapseHeight = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      height: 0,
      duration: 400,
      easing: 'easeInQuart',
      ...options
    })
  }

  // Utility function to animate elements when they enter viewport
  const animateOnScroll = (
    selector: string,
    animation: (target: Element) => anime.AnimeInstance,
    options: {
      threshold?: number
      rootMargin?: string
    } = {}
  ) => {
    const { threshold = 0.1, rootMargin = '0px' } = options

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animation(entry.target)
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold, rootMargin }
    )

    // Observe elements
    const elements = document.querySelectorAll(selector)
    elements.forEach((el) => observer.observe(el))

    return observer
  }

  // Chain multiple animations
  const chain = (...animations: (() => anime.AnimeInstance)[]) => {
    return animations.reduce((promise, animation) => {
      return promise.then(() => animation().finished)
    }, Promise.resolve())
  }

  // Animate with delay
  const withDelay = (
    animationFn: () => anime.AnimeInstance,
    delay: number
  ) => {
    return new Promise<anime.AnimeInstance>((resolve) => {
      setTimeout(() => {
        resolve(animationFn())
      }, delay)
    })
  }

  // Animate on next tick (useful for Vue reactivity)
  const onNextTick = async (animationFn: () => anime.AnimeInstance) => {
    await nextTick()
    return animationFn()
  }

  // AI-specific animations
  const aiThinking = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      opacity: [0.5, 1, 0.5],
      scale: [1, 1.05, 1],
      duration: 2000,
      easing: 'easeInOutSine',
      loop: true,
      ...options
    })
  }

  const quotaWarning = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      backgroundColor: ['#FEF3C7', '#FDE68A', '#FEF3C7'],
      duration: 1000,
      easing: 'easeInOutSine',
      loop: 3,
      ...options
    })
  }

  const successPulse = (target: string | Element | NodeList, options: Partial<anime.AnimeParams> = {}) => {
    return anime({
      targets: target,
      scale: [1, 1.1, 1],
      backgroundColor: ['#D1FAE5', '#A7F3D0', '#D1FAE5'],
      duration: 600,
      easing: 'easeOutBack',
      ...options
    })
  }

  return {
    // Basic animations
    fadeIn,
    fadeOut,
    slideIn,
    slideOut,
    scaleIn,
    
    // Interactive animations
    morphButton,
    pulse,
    shake,
    bounce,
    rotate,
    
    // List animations
    staggerIn,
    
    // Loading animations
    spin,
    progressBar,
    typingIndicator,
    
    // Specialized animations
    messageBubble,
    flipCard,
    expandHeight,
    collapseHeight,
    
    // AI-specific animations
    aiThinking,
    quotaWarning,
    successPulse,
    
    // Utility functions
    animateOnScroll,
    chain,
    withDelay,
    onNextTick
  }
}