import { ref, computed } from 'vue'
import { useToast } from '../composables/useToast'
import AssignmentService from '../services/assignments'
import type { Certificate, CertificateVerificationResponse } from '../types/assignments'

export const useCertificates = () => {
  const toast = useToast()
  
  // State
  const certificates = ref<Certificate[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Computed
  const issuedCertificates = computed(() => 
    certificates.value.filter(cert => cert.status === 'issued')
  )
  
  const pendingCertificates = computed(() => 
    certificates.value.filter(cert => cert.status === 'pending')
  )
  
  // Methods
  const fetchMyCertificates = async () => {
    loading.value = true
    error.value = null
    
    try {
      certificates.value = await AssignmentService.getMyCertificates()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch certificates'
      toast.error('Failed to load certificates')
    } finally {
      loading.value = false
    }
  }
  
  const generateCertificatePDF = async (certificateId: string, templateType: string = 'completion') => {
    try {
      const result = await AssignmentService.generateCertificatePDF(certificateId, templateType)
      
      // Update certificate in local state
      const certIndex = certificates.value.findIndex(cert => cert.id === certificateId)
      if (certIndex !== -1 && certificates.value[certIndex]) {
        certificates.value[certIndex]!.certificate_file_url = result.download_url
      }
      
      toast.success('Certificate PDF generated successfully')
      return result
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to generate certificate PDF'
      toast.error(message)
      throw err
    }
  }
  
  const downloadCertificate = async (certificateId: string, filename?: string) => {
    try {
      const downloadUrl = await AssignmentService.downloadCertificate(certificateId)
      
      // Create download link
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || `certificate_${certificateId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      toast.success('Certificate downloaded successfully')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to download certificate'
      toast.error(message)
      throw err
    }
  }
  
  const sendCertificateEmail = async (certificateId: string) => {
    try {
      await AssignmentService.sendCertificateEmail(certificateId)
      toast.success('Certificate sent via email successfully')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to send certificate email'
      toast.error(message)
      throw err
    }
  }
  
  const generateQRCode = async (certificateId: string) => {
    try {
      const result = await AssignmentService.generateQRCode(certificateId)
      
      // Update certificate in local state
      const certIndex = certificates.value.findIndex(cert => cert.id === certificateId)
      if (certIndex !== -1 && certificates.value[certIndex]) {
        certificates.value[certIndex]!.qr_code_url = result.qr_code_url
      }
      
      toast.success('QR code generated successfully')
      return result
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to generate QR code'
      toast.error(message)
      throw err
    }
  }
  
  const verifyCertificate = async (certificateNumber: string): Promise<CertificateVerificationResponse> => {
    try {
      const result = await AssignmentService.verifyCertificate({ certificate_number: certificateNumber })
      
      // Return the result as-is since it now matches the expected format
      return result
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Certificate verification failed'
      toast.error(message)
      throw err
    }
  }
  
  const verifyByQRCode = async (qrData: string): Promise<CertificateVerificationResponse> => {
    try {
      const result = await AssignmentService.verifyByQRCode(qrData)
      return result
    } catch (err) {
      const message = err instanceof Error ? err.message : 'QR code verification failed'
      toast.error(message)
      throw err
    }
  }
  
  const shareCertificate = async (certificate: Certificate) => {
    const shareData = {
      title: `Certificate - ${certificate.course.title}`,
      text: `I have successfully completed ${certificate.course.title} and earned a certificate!`,
      url: `${window.location.origin}/verify-certificate/${certificate.certificate_number}`
    }
    
    if (navigator.share) {
      try {
        await navigator.share(shareData)
        toast.success('Certificate shared successfully')
      } catch (error) {
        // User cancelled sharing or sharing not supported
        await copyVerificationUrl(certificate.certificate_number)
      }
    } else {
      await copyVerificationUrl(certificate.certificate_number)
    }
  }
  
  const copyVerificationUrl = async (certificateNumber: string) => {
    const url = `${window.location.origin}/verify-certificate/${certificateNumber}`
    
    try {
      await navigator.clipboard.writeText(url)
      toast.success('Certificate verification URL copied to clipboard')
    } catch (error) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea')
      textArea.value = url
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      toast.success('Certificate verification URL copied to clipboard')
    }
  }
  
  return {
    // State
    certificates,
    loading,
    error,
    
    // Computed
    issuedCertificates,
    pendingCertificates,
    
    // Methods
    fetchMyCertificates,
    generateCertificatePDF,
    downloadCertificate,
    sendCertificateEmail,
    generateQRCode,
    verifyCertificate,
    verifyByQRCode,
    shareCertificate,
    copyVerificationUrl
  }
}