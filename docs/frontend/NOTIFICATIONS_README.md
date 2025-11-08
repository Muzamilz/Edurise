# Notification System

A comprehensive notification system for the Edurise LMS platform with real-time updates, sound effects, animations, and customizable preferences.

## Features

### ✨ Core Features
- **Real-time notifications** via WebSocket connections
- **Sound effects** with Web Audio API (no external files needed)
- **Smooth animations** using Anime.js
- **Browser notifications** with permission handling
- **Toast notifications** for immediate feedback
- **Notification preferences** with granular controls
- **Badge system** with multiple variants and animations
- **Responsive design** with mobile support

### 🎨 Visual Features
- Bell shake animation for new notifications
- Pulsing badge for urgent notifications
- Ring expansion effect for real-time updates
- Smooth slide transitions for panels
- Hover effects and micro-interactions
- Custom scrollbar styling

### 🔊 Audio Features
- Simple notification beep for regular notifications
- Urgent notification sound (double beep)
- Success sound (ascending notes)
- Web Audio API implementation (no external files)
- User gesture requirement handling

## Components

### NotificationCenter
Main notification interface with bell icon and dropdown panel.

```vue
<NotificationCenter />
```

**Features:**
- Notification bell with badge
- Dropdown panel with filters
- Real-time updates
- Settings integration

### NotificationItem
Individual notification display component.

```vue
<NotificationItem 
  :notification="notification"
  @click="handleClick"
  @mark-read="markAsRead"
  @delete="deleteNotification"
/>
```

**Props:**
- `notification`: Notification object
- Events: `click`, `mark-read`, `delete`

### NotificationSettings
Preferences panel for notification customization.

```vue
<NotificationSettings
  :preferences="preferences"
  @update="updatePreferences"
  @close="closeSettings"
/>
```

**Features:**
- Sound toggle
- Browser notification toggle
- Email notification toggle
- Category-specific settings
- Quiet hours configuration

### NotificationBadge
Reusable badge component for notification counts.

```vue
<NotificationBadge 
  :count="5"
  variant="urgent"
  :pulse="true"
>
  <YourComponent />
</NotificationBadge>
```

**Props:**
- `count`: Number to display
- `maxCount`: Maximum before showing "+"
- `variant`: 'default' | 'urgent' | 'success' | 'warning'
- `size`: 'sm' | 'md' | 'lg'
- `pulse`: Enable pulsing animation

### NotificationToast
Toast notification system for immediate feedback.

```vue
<NotificationToast />
```

**Usage:**
```typescript
import { showToast, showSuccessToast, showErrorToast } from '@/utils/toast'

showToast('Message', { type: 'info', title: 'Title' })
showSuccessToast('Success message')
showErrorToast('Error message')
```

## Composables

### useNotifications
Main composable for notification management.

```typescript
import { useNotifications } from '@/composables/useNotifications'

const {
  notifications,
  unreadCount,
  loading,
  fetchNotifications,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  refresh
} = useNotifications()
```

### useNotificationPreferences
Composable for managing notification preferences.

```typescript
import { useNotificationPreferences } from '@/composables/useNotifications'

const {
  preferences,
  updatePreferences,
  fetchPreferences
} = useNotificationPreferences()
```

## Services

### NotificationSoundService
Web Audio API-based sound service.

```typescript
import { notificationSoundService } from '@/utils/notificationSound'

// Enable/disable sounds
notificationSoundService.setEnabled(true)

// Play different sounds
notificationSoundService.playNotificationBeep()
notificationSoundService.playUrgentNotification()
notificationSoundService.playSuccessSound()
```

## Integration

### 1. Add to App.vue
```vue
<template>
  <div id="app">
    <!-- Your app content -->
    <NotificationToast />
  </div>
</template>
```

### 2. Add to Header Component
```vue
<template>
  <header>
    <!-- Other header content -->
    <NotificationCenter v-if="isAuthenticated" />
  </header>
</template>
```

### 3. Initialize in Main Component
```typescript
import { useNotifications } from '@/composables/useNotifications'

export default {
  setup() {
    const { refresh } = useNotifications()
    
    onMounted(() => {
      refresh()
    })
  }
}
```

## Notification Types

### Priority Levels
- `low`: Basic notifications
- `normal`: Standard notifications (default)
- `high`: Important notifications
- `urgent`: Critical notifications with enhanced effects

### Categories
- `assignment`: Assignment-related notifications
- `grade`: Grade and feedback notifications
- `live_class`: Live class reminders and updates
- `course`: Course enrollment and updates
- `system`: System announcements
- `announcement`: General announcements
- `reminder`: Reminders and due dates

## Customization

### Styling
All components use Tailwind CSS classes and can be customized via:
- CSS custom properties
- Tailwind configuration
- Component-specific style overrides

### Animations
Animations are built with Anime.js and can be customized in:
- `useAnimations` composable
- Component-specific animation methods
- CSS keyframe animations

### Sounds
Sound effects are generated programmatically and can be customized in:
- `NotificationSoundService` class
- Frequency and duration parameters
- Custom sound patterns

## Browser Support

- **Modern browsers** with Web Audio API support
- **Fallback handling** for unsupported features
- **Progressive enhancement** approach
- **Mobile responsive** design

## Performance

- **Lazy loading** of notification data
- **Virtual scrolling** for large notification lists
- **Debounced** real-time updates
- **Memory management** for WebSocket connections
- **Optimized animations** with hardware acceleration

## Accessibility

- **ARIA labels** for screen readers
- **Keyboard navigation** support
- **High contrast** mode compatibility
- **Reduced motion** respect
- **Focus management** for modals

## Demo

Use the `NotificationDemo` component to test all features:

```vue
<NotificationDemo />
```

This provides interactive buttons to test:
- Different notification types
- Sound effects
- Badge variants
- Animations
- Bulk operations

## API Integration

The notification system integrates with the backend API through:
- `NotificationService` for HTTP requests
- WebSocket connections for real-time updates
- Automatic retry logic for failed requests
- Offline support with local storage

## Best Practices

1. **Use appropriate priority levels** for different notification types
2. **Respect user preferences** for sounds and browser notifications
3. **Provide clear actions** for notification management
4. **Test across devices** and browsers
5. **Monitor performance** with large notification volumes
6. **Handle edge cases** gracefully (network issues, permissions)

## Troubleshooting

### Common Issues

**Sounds not playing:**
- Check user gesture requirements
- Verify audio context initialization
- Test browser audio permissions

**Notifications not appearing:**
- Check WebSocket connection status
- Verify API endpoint configuration
- Test browser notification permissions

**Performance issues:**
- Monitor notification list size
- Check animation performance
- Verify memory usage patterns

### Debug Mode

Enable debug logging:
```typescript
// In development
localStorage.setItem('notification-debug', 'true')
```

This will log:
- WebSocket events
- Sound playback attempts
- Animation triggers
- API requests/responses