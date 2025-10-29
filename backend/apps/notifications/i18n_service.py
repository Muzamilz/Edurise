"""
Internationalization service for notifications
Supports English, Arabic (RTL), and Somali languages as per requirements
"""

from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language
from typing import Dict, Any, Optional


class NotificationI18nService:
    """Service for handling multi-language notifications"""
    
    # Supported languages as per requirements
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'ar': 'Arabic',
        'so': 'Somali'
    }
    
    # RTL languages
    RTL_LANGUAGES = ['ar']
    
    # Notification message templates in multiple languages
    MESSAGE_TEMPLATES = {
        'course_enrollment': {
            'en': {
                'title': 'Enrolled in {course_title}',
                'message': 'You have successfully enrolled in {course_title}. Start learning now!'
            },
            'ar': {
                'title': 'تم التسجيل في {course_title}',
                'message': 'لقد تم تسجيلك بنجاح في {course_title}. ابدأ التعلم الآن!'
            },
            'so': {
                'title': 'Waxaad ku diiwaan gashay {course_title}',
                'message': 'Si guul leh ayaad ugu diiwaan gashay {course_title}. Bilow barashada hadda!'
            }
        },
        'class_reminder': {
            'en': {
                'title': 'Class Reminder: {class_title}',
                'message': 'Your class "{class_title}" starts in {minutes} minutes.'
            },
            'ar': {
                'title': 'تذكير بالفصل: {class_title}',
                'message': 'سيبدأ فصلك "{class_title}" خلال {minutes} دقيقة.'
            },
            'so': {
                'title': 'Xusuusin fasalka: {class_title}',
                'message': 'Fasalkaaga "{class_title}" wuxuu bilaabmayaa {minutes} daqiiqo gudahood.'
            }
        },
        'assignment_due': {
            'en': {
                'title': 'Assignment Due: {assignment_title}',
                'message': 'Your assignment "{assignment_title}" is due in {hours} hours.'
            },
            'ar': {
                'title': 'موعد تسليم الواجب: {assignment_title}',
                'message': 'واجبك "{assignment_title}" مطلوب تسليمه خلال {hours} ساعة.'
            },
            'so': {
                'title': 'Hawsha la dhammeeyo: {assignment_title}',
                'message': 'Hawshaada "{assignment_title}" waa in la dhammeeyo {hours} saacadood gudahood.'
            }
        },
        'payment_success': {
            'en': {
                'title': 'Payment Successful',
                'message': 'Your payment of {amount} for {item_name} has been processed successfully.'
            },
            'ar': {
                'title': 'تم الدفع بنجاح',
                'message': 'تم معالجة دفعتك البالغة {amount} لـ {item_name} بنجاح.'
            },
            'so': {
                'title': 'Lacag bixinta guul',
                'message': 'Lacag bixintaada {amount} ee {item_name} si guul leh ayaa loo habeeyay.'
            }
        },
        'payment_failed': {
            'en': {
                'title': 'Payment Failed',
                'message': 'We were unable to process your payment for {item_name}. Please update your payment method.'
            },
            'ar': {
                'title': 'فشل في الدفع',
                'message': 'لم نتمكن من معالجة دفعتك لـ {item_name}. يرجى تحديث طريقة الدفع الخاصة بك.'
            },
            'so': {
                'title': 'Lacag bixintu way fashilantay',
                'message': 'Ma awoodnayn inaan ka habeeyno lacag bixintaada {item_name}. Fadlan cusboonaysii habka lacag bixinta.'
            }
        },
        'payment_overdue': {
            'en': {
                'title': 'Payment Overdue',
                'message': 'Your payment for {item_name} is overdue. Please make payment to continue accessing services.'
            },
            'ar': {
                'title': 'الدفع متأخر',
                'message': 'دفعتك لـ {item_name} متأخرة. يرجى الدفع لمواصلة الوصول إلى الخدمات.'
            },
            'so': {
                'title': 'Lacag bixintu way dhaaftay',
                'message': 'Lacag bixintaada {item_name} way dhaaftay waqtigeeda. Fadlan bixi lacagta si aad u sii isticmaasho adeegyada.'
            }
        },
        'subscription_renewed': {
            'en': {
                'title': 'Subscription Renewed',
                'message': 'Your {plan_name} subscription has been renewed successfully until {expiry_date}.'
            },
            'ar': {
                'title': 'تم تجديد الاشتراك',
                'message': 'تم تجديد اشتراكك في {plan_name} بنجاح حتى {expiry_date}.'
            },
            'so': {
                'title': 'Rukunka la cusboonaysiiyay',
                'message': 'Rukunkaaga {plan_name} si guul leh ayaa loo cusboonaysiiyay ilaa {expiry_date}.'
            }
        },
        'subscription_cancelled': {
            'en': {
                'title': 'Subscription Cancelled',
                'message': 'Your {plan_name} subscription has been cancelled. You will have access until {expiry_date}.'
            },
            'ar': {
                'title': 'تم إلغاء الاشتراك',
                'message': 'تم إلغاء اشتراكك في {plan_name}. ستتمكن من الوصول حتى {expiry_date}.'
            },
            'so': {
                'title': 'Rukunka la joojiyay',
                'message': 'Rukunkaaga {plan_name} waa la joojiyay. Waxaad heli doontaa gelitaan ilaa {expiry_date}.'
            }
        },
        'invoice_sent': {
            'en': {
                'title': 'Invoice Sent',
                'message': 'Your invoice #{invoice_number} for {amount} has been sent to your email.'
            },
            'ar': {
                'title': 'تم إرسال الفاتورة',
                'message': 'تم إرسال فاتورتك رقم #{invoice_number} بمبلغ {amount} إلى بريدك الإلكتروني.'
            },
            'so': {
                'title': 'Biilka la diray',
                'message': 'Biilkaaga #{invoice_number} ee {amount} waxaa loo diray emailkaaga.'
            }
        },
        'teacher_approval': {
            'en': {
                'title': 'Teacher Application {status}',
                'message': 'Your teacher application has been {status}. {additional_info}'
            },
            'ar': {
                'title': 'طلب المعلم {status}',
                'message': 'تم {status} طلب المعلم الخاص بك. {additional_info}'
            },
            'so': {
                'title': 'Codsiga macallinka {status}',
                'message': 'Codsigaaga macallinka waa la {status}. {additional_info}'
            }
        },
        'system': {
            'en': {
                'title': 'System Notification',
                'message': 'System update: {message}'
            },
            'ar': {
                'title': 'إشعار النظام',
                'message': 'تحديث النظام: {message}'
            },
            'so': {
                'title': 'Ogeysiiska nidaamka',
                'message': 'Cusboonaysiinta nidaamka: {message}'
            }
        }
    }
    
    @classmethod
    def get_user_language(cls, user) -> str:
        """Get user's preferred language"""
        if hasattr(user, 'userprofile'):
            # Get language from user profile
            profiles = user.profiles.all()
            if profiles.exists():
                return profiles.first().language
        
        # Default to English
        return 'en'
    
    @classmethod
    def get_localized_message(cls, notification_type: str, language: str, context: Dict[str, Any] = None) -> Dict[str, str]:
        """Get localized notification message"""
        if context is None:
            context = {}
        
        # Get template for notification type and language
        templates = cls.MESSAGE_TEMPLATES.get(notification_type, {})
        template = templates.get(language, templates.get('en', {}))
        
        if not template:
            # Fallback to generic message
            template = {
                'title': 'Notification',
                'message': 'You have a new notification.'
            }
        
        # Format message with context
        try:
            title = template['title'].format(**context)
            message = template['message'].format(**context)
        except (KeyError, ValueError):
            # If formatting fails, use template as-is
            title = template['title']
            message = template['message']
        
        return {
            'title': title,
            'message': message,
            'language': language,
            'is_rtl': language in cls.RTL_LANGUAGES
        }
    
    @classmethod
    def get_all_supported_languages(cls) -> Dict[str, str]:
        """Get all supported languages"""
        return cls.SUPPORTED_LANGUAGES.copy()
    
    @classmethod
    def is_rtl_language(cls, language: str) -> bool:
        """Check if language is RTL"""
        return language in cls.RTL_LANGUAGES
    
    @classmethod
    def get_email_subject_prefix(cls, language: str, tenant_name: str = None) -> str:
        """Get localized email subject prefix"""
        prefixes = {
            'en': f'[{tenant_name or "Edurise"}]',
            'ar': f'[{tenant_name or "إدورايز"}]',
            'so': f'[{tenant_name or "Edurise"}]'
        }
        return prefixes.get(language, prefixes['en'])
    
    @classmethod
    def get_notification_preferences_labels(cls, language: str) -> Dict[str, str]:
        """Get localized notification preference labels"""
        labels = {
            'en': {
                'email_notifications': 'Email Notifications',
                'push_notifications': 'Push Notifications',
                'course_enrollment_notifications': 'Course Enrollment',
                'class_reminder_notifications': 'Class Reminders',
                'assignment_due_notifications': 'Assignment Due Dates',
                'payment_notifications': 'Payment Updates',
                'system_notifications': 'System Announcements'
            },
            'ar': {
                'email_notifications': 'إشعارات البريد الإلكتروني',
                'push_notifications': 'الإشعارات الفورية',
                'course_enrollment_notifications': 'تسجيل الدورات',
                'class_reminder_notifications': 'تذكيرات الفصول',
                'assignment_due_notifications': 'مواعيد تسليم الواجبات',
                'payment_notifications': 'تحديثات الدفع',
                'system_notifications': 'إعلانات النظام'
            },
            'so': {
                'email_notifications': 'Ogeysiisyada Email-ka',
                'push_notifications': 'Ogeysiisyada Degdegga ah',
                'course_enrollment_notifications': 'Diiwaan gelinta Koorsada',
                'class_reminder_notifications': 'Xusuusinta Fasalka',
                'assignment_due_notifications': 'Taariikhyada Hawlaha',
                'payment_notifications': 'Cusboonaysiinta Lacag bixinta',
                'system_notifications': 'Ogeysiisyada Nidaamka'
            }
        }
        return labels.get(language, labels['en'])
    
    @classmethod
    def format_datetime_for_language(cls, dt, language: str) -> str:
        """Format datetime according to language preferences"""
        if language == 'ar':
            # Arabic date format
            return dt.strftime('%d/%m/%Y %H:%M')
        elif language == 'so':
            # Somali date format
            return dt.strftime('%d-%m-%Y %H:%M')
        else:
            # English date format
            return dt.strftime('%B %d, %Y at %I:%M %p')
    
    @classmethod
    def get_time_ago_text(cls, language: str, minutes: int) -> str:
        """Get localized 'time ago' text"""
        if minutes < 1:
            texts = {
                'en': 'just now',
                'ar': 'الآن',
                'so': 'hadda'
            }
        elif minutes < 60:
            texts = {
                'en': f'{minutes} minute{"s" if minutes != 1 else ""} ago',
                'ar': f'منذ {minutes} دقيقة',
                'so': f'{minutes} daqiiqo ka hor'
            }
        elif minutes < 1440:  # Less than 24 hours
            hours = minutes // 60
            texts = {
                'en': f'{hours} hour{"s" if hours != 1 else ""} ago',
                'ar': f'منذ {hours} ساعة',
                'so': f'{hours} saacadood ka hor'
            }
        else:  # Days
            days = minutes // 1440
            texts = {
                'en': f'{days} day{"s" if days != 1 else ""} ago',
                'ar': f'منذ {days} يوم',
                'so': f'{days} maalmood ka hor'
            }
        
        return texts.get(language, texts['en'])


class NotificationTemplateI18nService:
    """Service for managing multi-language notification templates"""
    
    @classmethod
    def get_email_template_path(cls, notification_type: str, language: str) -> str:
        """Get email template path for specific language"""
        # Try language-specific template first
        template_path = f'emails/notifications/{language}/{notification_type}.html'
        
        # Fallback to English template
        fallback_path = f'emails/notifications/{notification_type}.html'
        
        # Check if language-specific template exists
        try:
            from django.template.loader import get_template
            get_template(template_path)
            return template_path
        except:
            return fallback_path
    
    @classmethod
    def get_template_context(cls, notification, language: str) -> Dict[str, Any]:
        """Get template context with localized content"""
        context = {
            'notification': notification,
            'user': notification.user,
            'tenant': notification.tenant,
            'language': language,
            'is_rtl': NotificationI18nService.is_rtl_language(language),
            'site_url': cls._get_site_url(),
            'formatted_date': NotificationI18nService.format_datetime_for_language(
                notification.created_at, language
            )
        }
        
        # Add localized labels
        context['labels'] = NotificationI18nService.get_notification_preferences_labels(language)
        
        return context
    
    @classmethod
    def _get_site_url(cls) -> str:
        """Get site URL from settings"""
        from django.conf import settings
        return getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')