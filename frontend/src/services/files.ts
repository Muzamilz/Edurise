import { api, type PaginatedResponse } from './api'

export interface FileUpload {
  id: string
  original_filename: string
  file: string
  file_size: number
  file_size_mb: number
  file_type: string
  file_extension: string
  category: {
    id: string
    name: string
    description: string
  }
  title: string
  description: string
  tags: string[]
  uploaded_by: {
    id: string
    email: string
    name: string
  }
  access_level: 'public' | 'tenant' | 'enrolled' | 'instructor' | 'private'
  course?: {
    id: string
    title: string
  }
  status: 'uploading' | 'processing' | 'active' | 'archived' | 'deleted'
  download_count: number
  last_accessed?: string
  created_at: string
  updated_at: string
  expires_at?: string
  is_image: boolean
  is_video: boolean
  is_document: boolean
  is_expired: boolean
}

export interface FilePermissions {
  can_view: boolean
  can_download: boolean
  can_edit: boolean
  can_delete: boolean
  can_share: boolean
  access_reason: string
  restrictions: string[]
}

export interface FileAccessResult {
  allowed: boolean
  reason: string
  restrictions: string[]
  subscription_required: boolean
  upgrade_url?: string
}

export interface FileUploadRequest {
  file: File
  category: string
  title?: string
  description?: string
  access_level?: string
  course_id?: string
  tags?: string[]
  expires_at?: string
}

export interface FileShareRequest {
  user_emails: string[]
}

export class FileService {
  // File CRUD operations
  static async getFiles(filters?: {
    category?: string
    access_level?: string
    status?: string
    course?: string
    search?: string
    ordering?: string
  }): Promise<PaginatedResponse<FileUpload>> {
    const params = new URLSearchParams()
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString())
        }
      })
    }
    
    const response = await api.get<PaginatedResponse<FileUpload>>(`/api/v1/file-uploads/?${params}`)
    return response.data.data
  }

  static async getFile(id: string): Promise<FileUpload> {
    const response = await api.get<FileUpload>(`/api/v1/file-uploads/${id}/`)
    return response.data.data
  }

  static async uploadFile(data: FileUploadRequest): Promise<FileUpload> {
    const formData = new FormData()
    formData.append('file', data.file)
    formData.append('category', data.category)
    
    if (data.title) formData.append('title', data.title)
    if (data.description) formData.append('description', data.description)
    if (data.access_level) formData.append('access_level', data.access_level)
    if (data.course_id) formData.append('course_id', data.course_id)
    if (data.expires_at) formData.append('expires_at', data.expires_at)
    if (data.tags) formData.append('tags', JSON.stringify(data.tags))
    
    const response = await api.post<FileUpload>('/api/v1/file-uploads/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data.data
  }

  static async updateFile(id: string, data: Partial<FileUploadRequest>): Promise<FileUpload> {
    const response = await api.patch<FileUpload>(`/api/v1/file-uploads/${id}/`, data)
    return response.data.data
  }

  static async deleteFile(id: string): Promise<void> {
    await api.delete(`/api/v1/file-uploads/${id}/`)
  }

  // Access control operations
  static async getSecureUrl(id: string, expiresIn: number = 3600): Promise<{
    secure_url: string
    expires_in: number
  }> {
    const response = await api.get(`/api/v1/file-uploads/${id}/secure_url/?expires_in=${expiresIn}`)
    return response.data.data
  }

  static async downloadFile(id: string): Promise<void> {
    const response = await api.get(`/api/v1/file-uploads/${id}/download/`, {
      responseType: 'blob'
    })
    
    // Create download link
    const blob = new Blob([response.data.data || response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Try to get filename from response headers
    const contentDisposition = response.headers['content-disposition']
    let filename = 'download'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  static async getFilePermissions(id: string): Promise<FilePermissions> {
    const response = await api.get<FilePermissions>(`/api/v1/files/permissions/${id}/`)
    return response.data.data
  }

  static async bulkCheckPermissions(fileIds: string[]): Promise<Record<string, {
    access_allowed: boolean
    access_reason: string
    permissions: FilePermissions
    file_info: {
      filename: string
      size_mb: number
      type: string
      access_level: string
    }
  }>> {
    const response = await api.post('/api/v1/files/permissions/bulk/', {
      file_ids: fileIds
    })
    return response.data.data
  }

  // File sharing operations
  static async shareFile(id: string, data: FileShareRequest): Promise<{
    shared_with: Array<{
      user_id: string
      email: string
      name: string
    }>
    denied_users: Array<{
      user_id: string
      email: string
      reason: string
    }>
  }> {
    const response = await api.post(`/api/v1/file-uploads/${id}/share/`, data)
    return response.data.data
  }

  static async unshareFile(id: string, data: FileShareRequest): Promise<void> {
    await api.post(`/api/v1/file-uploads/${id}/unshare/`, data)
  }

  static async getSharedUsers(id: string): Promise<Array<{
    id: string
    email: string
    name: string
    shared_at: string
  }>> {
    const response = await api.get(`/api/v1/file-uploads/${id}/shared_users/`)
    return response.data.data
  }

  static async setAccessLevel(id: string, accessLevel: string): Promise<FileUpload> {
    const response = await api.post(`/api/v1/file-uploads/${id}/set_access_level/`, {
      access_level: accessLevel
    })
    return response.data.data
  }

  // File listing operations
  static async getMyFiles(category?: string): Promise<FileUpload[]> {
    const params = category ? `?category=${category}` : ''
    const response = await api.get<FileUpload[]>(`/api/v1/file-uploads/my_files/${params}`)
    return response.data.data
  }

  static async getCourseFiles(courseId: string): Promise<FileUpload[]> {
    const response = await api.get<FileUpload[]>(`/api/v1/file-uploads/course_files/?course_id=${courseId}`)
    return response.data.data
  }

  static async getFileStatistics(id: string): Promise<{
    download_count: number
    unique_downloaders: number
    last_accessed: string
    access_logs: Array<{
      user: string
      accessed_at: string
      ip_address: string
    }>
  }> {
    const response = await api.get(`/api/v1/file-uploads/${id}/statistics/`)
    return response.data.data
  }

  // File categories
  static async getFileCategories(): Promise<Array<{
    id: string
    name: string
    description: string
    icon: string
    allowed_extensions: string[]
    max_file_size_mb: number
  }>> {
    const response = await api.get('/api/v1/file-categories/')
    return response.data.data
  }
}

export default FileService