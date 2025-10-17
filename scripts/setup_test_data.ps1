# PowerShell script to set up comprehensive test data for Edurise LMS Platform

Write-Host "🚀 Setting up comprehensive test data for Edurise LMS Platform..." -ForegroundColor Green
Write-Host "=" * 60

# Change to backend directory
$backendDir = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path $backendDir)) {
    Write-Host "❌ Backend directory not found!" -ForegroundColor Red
    exit 1
}

Set-Location $backendDir

try {
    Write-Host "📊 Creating comprehensive test data..." -ForegroundColor Yellow
    
    # Run the management command
    python manage.py setup_comprehensive_data --clean --organizations 5 --users-per-org 25 --courses-per-teacher 3
    
    Write-Host "`n🎉 Test data setup completed successfully!" -ForegroundColor Green
    
    Write-Host "`n🔑 LOGIN CREDENTIALS:" -ForegroundColor Cyan
    Write-Host "Super Admin: admin@edurise.com / admin123456"
    Write-Host "Org Admins: admin@[subdomain].com / admin123456"
    Write-Host "Teachers: teacher[N]@[subdomain].com / teacher123456"
    Write-Host "Students: student[N]@[subdomain].com / student123456"
    
    Write-Host "`n🏢 ORGANIZATIONS CREATED:" -ForegroundColor Cyan
    Write-Host "- Edurise Platform (main) - Enterprise"
    Write-Host "- Tech University (techuni) - Pro"
    Write-Host "- Business Academy (bizacademy) - Pro"
    Write-Host "- Creative Institute (creative) - Basic"
    Write-Host "- Medical College (medcollege) - Enterprise"
    
    Write-Host "`n🌐 ACCESS URLs:" -ForegroundColor Cyan
    Write-Host "- Main Platform: http://localhost:3000"
    Write-Host "- Tech University: http://techuni.localhost:3000"
    Write-Host "- Business Academy: http://bizacademy.localhost:3000"
    
    Write-Host "`n📚 WHAT WAS CREATED:" -ForegroundColor Magenta
    Write-Host "✅ 5 Organizations with different subscription plans"
    Write-Host "✅ 125+ Users (Super Admin, Org Admins, Teachers, Students)"
    Write-Host "✅ 45+ Courses with modules and live classes"
    Write-Host "✅ Enrollments and course reviews"
    Write-Host "✅ Payment records and invoices"
    Write-Host "✅ AI conversations and summaries"
    Write-Host "✅ Notifications and usage data"
    Write-Host "✅ Live class attendance records"
    Write-Host "✅ Teacher approval workflows"
    
} catch {
    Write-Host "❌ Error running setup command: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n🚀 Ready to test the complete Edurise LMS Platform!" -ForegroundColor Green