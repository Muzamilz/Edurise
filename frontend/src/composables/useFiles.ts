import { ref, computed } from 'vue'
import { useToast } from './useToast'
import FileService, { type FileUpload, type FilePermissions, type FileUploadRequest } from '../services/files'

export const useFiles = () => {
  const toast = useToast()
  
  // State
  const files = ref<FileUpload[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const uploadProgress = ref(0)
  const uploading = ref(false)
  
  // Computed
  const activeFiles = computed(() => 
    files.value.filter(file => file.status === 'active')
  )
  
  const myFiles = computed(() => 
    files.value.filter(file => file.uploaded_by.id === 'current-user-id') // This should be dynamic
  )
  
  const sharedFiles = computed(() => 
    files.value.filter(file => 
      file.access_level !== 'private' && file.uploaded_by.id !== 'current-user-id'
    )
  )
  
  // Methods
  const fetchFiles = async (filters?: Parameters<typeof FileService.getFiles>[0]) => {
    loading.value = true
    error.value = null
    
    try {
      const result = await FileService.getFiles(filters)
      files.value = result.results
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch files'
      toast.error('Failed to load files')
    } finally {
      loading.value = false
    }
  }
  
  const fetchMyFiles = async (category?: string) => {
    loading.value = true
    error.value = null
    
    try {
      files.value = await FileService.getMyFiles(category)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch your files'
      toast.error('Failed to load your files')
    } finally {
      loading.value = false
    }
  }
  
  const fetchCourseFiles = async (courseId: string) => {
    loading.value = true
    error.value = null
    
    try {
      files.value = await FileService.getCourseFiles(courseId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch course files'
      toast.error('Failed to load course files')
    } finally {
      loading.value = false
    }
  }
  
  const uploadFile = async (data: FileUploadRequest) => {
    uploading.value = true
    uploadProgress.value = 0
    
    try {
      // Simulate upload progress (in real implementation, this would come from the upload request)
      const progressInterval = setInterval(() => {
        if (uploadProgress.value < 90) {
          uploadProgress.value += 10
        }
      }, 200)
      
      const uploadedFile = await FileService.uploadFile(data)
      
      clearInterval(progressInterval)
      uploadProgress.value = 100
      
      // Add to files list
      files.value.unshift(uploadedFile)
      
      toast.success('File uploaded successfully')
      return uploadedFile
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to upload file'
      toast.error(message)
      throw err
    } finally {
      uploading.value = false
      uploadProgress.value = 0
    }
  }
  
  const downloadFile = async (fileId: string, useSecureUrl: boolean = true) => {
    try {
      if (useSecureUrl) {
        // Get secure URL first
        const { secure_url } = await FileService.getSecureUrl(fileId)
        
        // Open secure URL in new tab or download directly
        const link = document.createElement('a')
        link.href = secure_url
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } else {
        // Direct download
        await FileService.downloadFile(fileId)
      }
      
      toast.success('File download started')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to download file'
      toast.error(message)
      throw err
    }
  }
  
  const shareFile = async (fileId: string, userEmails: string[]) => {
    try {
      const result = await FileService.shareFile(fileId, { user_emails: userEmails })
      
      if (result.shared_with.length > 0) {
        toast.success(`File shared with ${result.shared_with.length} user(s)`)
      }
      
      if (result.denied_users.length > 0) {
        toast.warning(`Could not share with ${result.denied_users.length} user(s)`)
      }
      
      return result
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to share file'
      toast.error(message)
      throw err
    }
  }
  
  const unshareFile = async (fileId: string, userEmails: string[]) => {
    try {
      await FileService.unshareFile(fileId, { user_emails: userEmails })
      toast.success('File sharing removed successfully')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to remove file sharing'
      toast.error(message)
      throw err
    }
  }
  
  const updateAccessLevel = async (fileId: string, accessLevel: string) => {
    try {
      const updatedFile = await FileService.setAccessLevel(fileId, accessLevel)
      
      // Update file in local state
      const fileIndex = files.value.findIndex(file => file.id === fileId)
      if (fileIndex !== -1) {
        files.value[fileIndex] = updatedFile
      }
      
      toast.success('File access level updated successfully')
      return updatedFile
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update access level'
      toast.error(message)
      throw err
    }
  }
  
  const deleteFile = async (fileId: string) => {
    try {
      await FileService.deleteFile(fileId)
      
      // Remove from local state
      files.value = files.value.filter(file => file.id !== fileId)
      
      toast.success('File deleted successfully')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete file'
      toast.error(message)
      throw err
    }
  }
  
  const checkFilePermissions = async (fileId: string): Promise<FilePermissions> => {
    try {
      return await FileService.getFilePermissions(fileId)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to check file permissions'
      toast.error(message)
      throw err
    }
  }
  
  const getFileStatistics = async (fileId: string) => {
    try {
      return await FileService.getFileStatistics(fileId)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get file statistics'
      toast.error(message)
      throw err
    }
  }
  
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
  
  const getFileIcon = (file: FileUpload): string => {
    if (file.is_image) return '🖼️'
    if (file.is_video) return '🎥'
    if (file.is_document) return '📄'
    if (file.file_type.startsWith('audio/')) return '🎵'
    return '📁'
  }
  
  const getAccessLevelLabel = (accessLevel: string): string => {
    const labels = {
      'public': 'Public',
      'tenant': 'Organization Only',
      'enrolled': 'Enrolled Students',
      'instructor': 'Instructor Only',
      'private': 'Private'
    }
    return labels[accessLevel as keyof typeof labels] || accessLevel
  }
  
  const getAccessLevelColor = (accessLevel: string): string => {
    const colors = {
      'public': 'green',
      'tenant': 'blue',
      'enrolled': 'purple',
      'instructor': 'orange',
      'private': 'red'
    }
    return colors[accessLevel as keyof typeof colors] || 'gray'
  }
  
  return {
    // State
    files,
    loading,
    error,
    uploadProgress,
    uploading,
    
    // Computed
    activeFiles,
    myFiles,
    sharedFiles,
    
    // Methods
    fetchFiles,
    fetchMyFiles,
    fetchCourseFiles,
    uploadFile,
    downloadFile,
    shareFile,
    unshareFile,
    updateAccessLevel,
    deleteFile,
    checkFilePermissions,
    getFileStatistics,
    
    // Utilities
    formatFileSize,
    getFileIcon,
    getAccessLevelLabel,
    getAccessLevelColor
  }
}