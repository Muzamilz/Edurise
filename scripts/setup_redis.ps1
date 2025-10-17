# Redis Setup Script for Edurise LMS
# Run this script in PowerShell as Administrator

Write-Host "=== Edurise LMS Redis Setup ===" -ForegroundColor Green
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to check if port is available
function Test-Port($port) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
    return -not $connection
}

Write-Host "Checking system requirements..." -ForegroundColor Yellow

# Check available options
$dockerAvailable = Test-Command "docker"
$chocoAvailable = Test-Command "choco"
$wslAvailable = Test-Command "wsl"

Write-Host ""
Write-Host "Available installation options:" -ForegroundColor Cyan

if ($dockerAvailable) {
    Write-Host "✓ Docker is available" -ForegroundColor Green
} else {
    Write-Host "✗ Docker is not installed" -ForegroundColor Red
}

if ($chocoAvailable) {
    Write-Host "✓ Chocolatey is available" -ForegroundColor Green
} else {
    Write-Host "✗ Chocolatey is not installed" -ForegroundColor Red
}

if ($wslAvailable) {
    Write-Host "✓ WSL is available" -ForegroundColor Green
} else {
    Write-Host "✗ WSL is not installed" -ForegroundColor Red
}

Write-Host ""

# Check if Redis is already running
$redisRunning = -not (Test-Port 6379)
if ($redisRunning) {
    Write-Host "Redis appears to be already running on port 6379" -ForegroundColor Yellow
    $testRedis = Read-Host "Do you want to test the existing Redis connection? (y/n)"
    
    if ($testRedis -eq "y" -or $testRedis -eq "Y") {
        try {
            # Try to connect to Redis (requires redis-cli)
            if (Test-Command "redis-cli") {
                $result = redis-cli ping
                if ($result -eq "PONG") {
                    Write-Host "✓ Redis is working correctly!" -ForegroundColor Green
                    Write-Host "You can proceed with testing the WebSocket functionality." -ForegroundColor Cyan
                    Read-Host "Press Enter to exit"
                    exit 0
                } else {
                    Write-Host "✗ Redis is not responding correctly" -ForegroundColor Red
                }
            } else {
                Write-Host "Redis CLI not available for testing" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Could not test Redis connection" -ForegroundColor Red
        }
    }
}

# Installation menu
Write-Host "Choose an installation method:" -ForegroundColor Cyan
Write-Host "1. Docker (Recommended - Easy setup and cleanup)"
Write-Host "2. Chocolatey (Windows package manager)"
Write-Host "3. WSL2 (Windows Subsystem for Linux)"
Write-Host "4. Manual download instructions"
Write-Host "5. Exit"

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        if (-not $dockerAvailable) {
            Write-Host "Docker is not installed. Please install Docker Desktop first:" -ForegroundColor Red
            Write-Host "https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        Write-Host "Installing Redis using Docker..." -ForegroundColor Yellow
        
        # Stop existing Redis container if it exists
        docker stop edurise-redis 2>$null
        docker rm edurise-redis 2>$null
        
        # Pull and run Redis
        Write-Host "Pulling Redis image..." -ForegroundColor Yellow
        docker pull redis:7-alpine
        
        Write-Host "Starting Redis container..." -ForegroundColor Yellow
        docker run -d --name edurise-redis -p 6379:6379 redis:7-alpine
        
        # Wait a moment for container to start
        Start-Sleep -Seconds 3
        
        # Test the connection
        $testResult = docker exec edurise-redis redis-cli ping 2>$null
        if ($testResult -eq "PONG") {
            Write-Host "✓ Redis is running successfully!" -ForegroundColor Green
            Write-Host "Container name: edurise-redis" -ForegroundColor Cyan
            Write-Host "Port: 6379" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "To stop Redis: docker stop edurise-redis" -ForegroundColor Yellow
            Write-Host "To start Redis: docker start edurise-redis" -ForegroundColor Yellow
        } else {
            Write-Host "✗ Failed to start Redis container" -ForegroundColor Red
        }
    }
    
    "2" {
        if (-not $chocoAvailable) {
            Write-Host "Installing Chocolatey first..." -ForegroundColor Yellow
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
            
            # Refresh environment
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        }
        
        Write-Host "Installing Redis using Chocolatey..." -ForegroundColor Yellow
        choco install redis-64 -y
        
        Write-Host "Starting Redis service..." -ForegroundColor Yellow
        Start-Service redis
        
        # Test the connection
        Start-Sleep -Seconds 3
        if (Test-Command "redis-cli") {
            $testResult = redis-cli ping
            if ($testResult -eq "PONG") {
                Write-Host "✓ Redis is running successfully!" -ForegroundColor Green
            } else {
                Write-Host "✗ Redis is not responding" -ForegroundColor Red
            }
        }
    }
    
    "3" {
        if (-not $wslAvailable) {
            Write-Host "WSL is not installed. Installing WSL2..." -ForegroundColor Yellow
            wsl --install
            Write-Host "WSL installation started. You may need to restart your computer." -ForegroundColor Yellow
            Write-Host "After restart, run this script again and choose option 3." -ForegroundColor Cyan
        } else {
            Write-Host "Setting up Redis in WSL2..." -ForegroundColor Yellow
            Write-Host "Please run the following commands in your WSL2 terminal:" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "sudo apt update" -ForegroundColor White
            Write-Host "sudo apt install redis-server -y" -ForegroundColor White
            Write-Host "sudo service redis-server start" -ForegroundColor White
            Write-Host "redis-cli ping" -ForegroundColor White
            Write-Host ""
            Write-Host "Opening WSL2 terminal..." -ForegroundColor Yellow
            Start-Process wsl
        }
    }
    
    "4" {
        Write-Host "Manual installation instructions:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Go to: https://github.com/microsoftarchive/redis/releases" -ForegroundColor White
        Write-Host "2. Download the latest Redis-x64-*.msi file" -ForegroundColor White
        Write-Host "3. Run the installer" -ForegroundColor White
        Write-Host "4. Start Redis from the Start menu or Services panel" -ForegroundColor White
        Write-Host "5. Test with: redis-cli ping" -ForegroundColor White
        Write-Host ""
        Write-Host "Opening download page..." -ForegroundColor Yellow
        Start-Process "https://github.com/microsoftarchive/redis/releases"
    }
    
    "5" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host "Invalid choice. Exiting..." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Green
Write-Host "1. Start your Django backend server: python manage.py runserver" -ForegroundColor Cyan
Write-Host "2. Start your frontend server: npm run dev" -ForegroundColor Cyan
Write-Host "3. Test WebSocket connections in the live classes interface" -ForegroundColor Cyan
Write-Host "4. Check browser console for WebSocket connection logs" -ForegroundColor Cyan

Read-Host "Press Enter to exit"