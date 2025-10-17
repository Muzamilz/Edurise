from django.db.models import Count, Avg, Q
from django.utils import timezone
from .models import Course, Enrollment, CourseReview, CourseModule


class CourseService:
    """Service class for course-related operations"""
    
    @staticmethod
    def get_course_statistics(course):
        """Get comprehensive statistics for a course"""
        enrollments = course.enrollments.all()
        reviews = course.reviews.filter(is_approved=True)
        
        return {
            'total_enrollments': enrollments.count(),
            'active_enrollments': enrollments.filter(status='active').count(),
            'completed_enrollments': enrollments.filter(status='completed').count(),
            'completion_rate': (
                enrollments.filter(status='completed').count() / 
                max(enrollments.count(), 1) * 100
            ),
            'average_progress': enrollments.aggregate(
                avg_progress=Avg('progress_percentage')
            )['avg_progress'] or 0,
            'total_reviews': reviews.count(),
            'average_rating': reviews.aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0,
            'rating_distribution': {
                '5_star': reviews.filter(rating=5).count(),
                '4_star': reviews.filter(rating=4).count(),
                '3_star': reviews.filter(rating=3).count(),
                '2_star': reviews.filter(rating=2).count(),
                '1_star': reviews.filter(rating=1).count(),
            }
        }
    
    @staticmethod
    def get_recommended_courses(user, tenant, limit=10):
        """Get recommended courses for a user based on their enrollments and preferences"""
        # Get user's enrolled courses
        enrolled_courses = Course.objects.filter(
            enrollments__student=user,
            tenant=tenant
        )
        
        if not enrolled_courses.exists():
            # New user - return popular courses
            return Course.objects.filter(
                tenant=tenant,
                is_public=True
            ).annotate(
                enrollment_count=Count('enrollments')
            ).order_by('-enrollment_count')[:limit]
        
        # Get categories and tags from enrolled courses
        enrolled_categories = enrolled_courses.values_list('category', flat=True).distinct()
        enrolled_tags = []
        for course in enrolled_courses:
            enrolled_tags.extend(course.tags)
        
        # Find similar courses
        recommended = Course.objects.filter(
            tenant=tenant,
            is_public=True
        ).exclude(
            id__in=enrolled_courses.values_list('id', flat=True)
        ).annotate(
            enrollment_count=Count('enrollments'),
            avg_rating=Avg('reviews__rating')
        )
        
        # Score courses based on similarity
        category_q = Q(category__in=enrolled_categories)
        tag_q = Q()
        for tag in set(enrolled_tags):
            tag_q |= Q(tags__icontains=tag)
        
        # Prioritize courses with similar categories or tags
        recommended = recommended.filter(category_q | tag_q).order_by(
            '-avg_rating', '-enrollment_count'
        )[:limit]
        
        return recommended
    
    @staticmethod
    def calculate_course_progress(enrollment):
        """Calculate detailed progress for a course enrollment"""
        course = enrollment.course
        modules = course.modules.filter(is_published=True).order_by('order')
        
        if not modules.exists():
            return {
                'overall_progress': enrollment.progress_percentage,
                'modules_completed': 0,
                'total_modules': 0,
                'current_module': None,
                'next_module': None
            }
        
        # This is a simplified calculation
        # In a real system, you'd track module completion separately
        total_modules = modules.count()
        completed_modules = int((enrollment.progress_percentage / 100) * total_modules)
        
        current_module = None
        next_module = None
        
        if completed_modules < total_modules:
            current_module = modules[completed_modules]
            if completed_modules + 1 < total_modules:
                next_module = modules[completed_modules + 1]
        
        return {
            'overall_progress': enrollment.progress_percentage,
            'modules_completed': completed_modules,
            'total_modules': total_modules,
            'current_module': current_module,
            'next_module': next_module
        }
    
    @staticmethod
    def can_enroll_in_course(user, course):
        """Check if a user can enroll in a course"""
        # Check if already enrolled
        if Enrollment.objects.filter(student=user, course=course).exists():
            return False, "Already enrolled in this course"
        
        # Check if course has available spots
        if course.max_students:
            current_enrollments = course.enrollments.filter(
                status__in=['active', 'completed']
            ).count()
            if current_enrollments >= course.max_students:
                return False, "Course is full"
        
        # Check if user has required permissions (for private courses)
        if not course.is_public:
            # Add logic for private course access
            pass
        
        return True, "Can enroll"
    
    @staticmethod
    def get_course_analytics_for_instructor(instructor, tenant):
        """Get analytics for all courses by an instructor"""
        courses = Course.objects.filter(
            instructor=instructor,
            tenant=tenant
        )
        
        total_enrollments = Enrollment.objects.filter(
            course__in=courses
        )
        
        return {
            'total_courses': courses.count(),
            'published_courses': courses.filter(is_public=True).count(),
            'total_students': total_enrollments.values('student').distinct().count(),
            'total_enrollments': total_enrollments.count(),
            'completed_enrollments': total_enrollments.filter(status='completed').count(),
            'average_rating': CourseReview.objects.filter(
                course__in=courses,
                is_approved=True
            ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0,
            'total_revenue': sum(
                float(course.price or 0) * course.enrollments.count()
                for course in courses
            ),
            'courses_by_category': courses.values('category').annotate(
                count=Count('id')
            ).order_by('-count')
        }
    
    @staticmethod
    def search_courses(query, tenant, filters=None):
        """Advanced course search with ranking"""
        courses = Course.objects.filter(tenant=tenant)
        
        if query:
            # Search in title (highest priority)
            title_matches = courses.filter(title__icontains=query)
            
            # Search in description (medium priority)
            description_matches = courses.filter(description__icontains=query)
            
            # Search in tags (lower priority)
            tag_matches = courses.filter(tags__icontains=query)
            
            # Combine results with ranking
            courses = (title_matches | description_matches | tag_matches).distinct()
        
        # Apply additional filters
        if filters:
            if 'category' in filters:
                courses = courses.filter(category=filters['category'])
            if 'difficulty_level' in filters:
                courses = courses.filter(difficulty_level=filters['difficulty_level'])
            if 'min_price' in filters:
                courses = courses.filter(price__gte=filters['min_price'])
            if 'max_price' in filters:
                courses = courses.filter(price__lte=filters['max_price'])
        
        # Add annotations for sorting
        courses = courses.annotate(
            enrollment_count=Count('enrollments'),
            avg_rating=Avg('reviews__rating')
        )
        
        return courses.order_by('-avg_rating', '-enrollment_count')


class EnrollmentService:
    """Service class for enrollment-related operations"""
    
    @staticmethod
    def enroll_student(student, course, tenant):
        """Enroll a student in a course with validation"""
        can_enroll, message = CourseService.can_enroll_in_course(student, course)
        
        if not can_enroll:
            raise ValueError(message)
        
        enrollment = Enrollment.objects.create(
            student=student,
            course=course,
            tenant=tenant
        )
        
        return enrollment
    
    @staticmethod
    def update_progress(enrollment, progress_percentage):
        """Update enrollment progress with validation"""
        progress_percentage = max(0, min(100, progress_percentage))
        enrollment.progress_percentage = progress_percentage
        
        # Auto-complete if 100%
        if progress_percentage == 100 and enrollment.status != 'completed':
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
        
        enrollment.save()
        return enrollment
    
    @staticmethod
    def get_student_dashboard_data(student, tenant):
        """Get dashboard data for a student"""
        enrollments = Enrollment.objects.filter(
            student=student,
            tenant=tenant
        ).select_related('course')
        
        return {
            'total_enrollments': enrollments.count(),
            'active_courses': enrollments.filter(status='active').count(),
            'completed_courses': enrollments.filter(status='completed').count(),
            'average_progress': enrollments.aggregate(
                avg_progress=Avg('progress_percentage')
            )['avg_progress'] or 0,
            'recent_enrollments': enrollments.order_by('-enrolled_at')[:5],
            'courses_in_progress': enrollments.filter(
                status='active',
                progress_percentage__lt=100
            ).order_by('-last_accessed')[:5]
        }


class RecommendationService:
    """Advanced recommendation service with multiple algorithms"""
    
    @staticmethod
    def get_personalized_recommendations(user, tenant, limit=10, algorithm='hybrid'):
        """
        Get personalized course recommendations using various algorithms
        
        Args:
            user: User object
            tenant: Tenant object
            limit: Number of recommendations to return
            algorithm: 'collaborative', 'content_based', 'hybrid', 'popularity'
        """
        from .models import Course, Enrollment, Wishlist
        from django.db.models import Count, Avg, Q, F
        from collections import defaultdict
        import math
        
        if algorithm == 'collaborative':
            return RecommendationService._collaborative_filtering(user, tenant, limit)
        elif algorithm == 'content_based':
            return RecommendationService._content_based_filtering(user, tenant, limit)
        elif algorithm == 'popularity':
            return RecommendationService._popularity_based(user, tenant, limit)
        else:  # hybrid
            return RecommendationService._hybrid_recommendations(user, tenant, limit)
    
    @staticmethod
    def _collaborative_filtering(user, tenant, limit):
        """Collaborative filtering based on similar users' preferences"""
        from .models import Course, Enrollment
        from django.db.models import Count, Q
        from collections import defaultdict
        
        # Get user's enrolled courses
        user_courses = set(Enrollment.objects.filter(
            student=user, tenant=tenant
        ).values_list('course_id', flat=True))
        
        if not user_courses:
            return RecommendationService._popularity_based(user, tenant, limit)
        
        # Find users with similar course preferences
        similar_users = Enrollment.objects.filter(
            course_id__in=user_courses,
            tenant=tenant
        ).exclude(student=user).values('student').annotate(
            common_courses=Count('course')
        ).filter(common_courses__gte=2).order_by('-common_courses')[:50]
        
        # Get courses liked by similar users
        similar_user_ids = [u['student'] for u in similar_users]
        recommended_courses = Enrollment.objects.filter(
            student_id__in=similar_user_ids,
            tenant=tenant,
            status__in=['active', 'completed']
        ).exclude(
            course_id__in=user_courses
        ).values('course').annotate(
            recommendation_score=Count('student'),
            avg_progress=Avg('progress_percentage')
        ).filter(
            recommendation_score__gte=2,
            avg_progress__gte=50  # Only recommend courses with good completion rates
        ).order_by('-recommendation_score', '-avg_progress')[:limit]
        
        # Format recommendations
        recommendations = []
        for rec in recommended_courses:
            try:
                course = Course.objects.get(id=rec['course'], tenant=tenant)
                recommendations.append({
                    'course': course,
                    'score': rec['recommendation_score'] / 10.0,  # Normalize score
                    'reason': f"Students with similar interests also enrolled in this course",
                    'algorithm': 'collaborative_filtering',
                    'metadata': {
                        'similar_users_count': rec['recommendation_score'],
                        'avg_completion_rate': rec['avg_progress']
                    }
                })
            except Course.DoesNotExist:
                continue
        
        return recommendations
    
    @staticmethod
    def _content_based_filtering(user, tenant, limit):
        """Content-based filtering using course features and user preferences"""
        from .models import Course, Enrollment
        from django.db.models import Count, Avg, Q
        from collections import Counter
        
        # Analyze user's course preferences
        user_enrollments = Enrollment.objects.filter(
            student=user, tenant=tenant
        ).select_related('course')
        
        if not user_enrollments.exists():
            return RecommendationService._popularity_based(user, tenant, limit)
        
        # Extract user preferences
        user_categories = Counter()
        user_difficulty_levels = Counter()
        user_instructors = Counter()
        total_courses = 0
        
        for enrollment in user_enrollments:
            course = enrollment.course
            user_categories[course.category] += 1
            user_difficulty_levels[course.difficulty_level] += 1
            user_instructors[course.instructor_id] += 1
            total_courses += 1
        
        # Get candidate courses
        enrolled_course_ids = user_enrollments.values_list('course_id', flat=True)
        candidate_courses = Course.objects.filter(
            tenant=tenant,
            is_public=True
        ).exclude(
            id__in=enrolled_course_ids
        ).select_related('instructor').prefetch_related('reviews')
        
        # Score each course based on content similarity
        scored_courses = []
        for course in candidate_courses:
            score = 0
            reasons = []
            
            # Category similarity (40% weight)
            category_score = user_categories.get(course.category, 0) / total_courses
            score += category_score * 0.4
            if category_score > 0:
                reasons.append(f"matches your interest in {course.category}")
            
            # Difficulty progression (30% weight)
            difficulty_weights = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
            user_avg_difficulty = sum(
                difficulty_weights[level] * count 
                for level, count in user_difficulty_levels.items()
            ) / total_courses
            
            course_difficulty = difficulty_weights[course.difficulty_level]
            # Prefer courses slightly above user's average level
            if course_difficulty <= user_avg_difficulty + 1:
                difficulty_score = 1 - abs(course_difficulty - user_avg_difficulty) / 3
                score += difficulty_score * 0.3
                if difficulty_score > 0.7:
                    reasons.append(f"appropriate {course.difficulty_level} level")
            
            # Instructor familiarity (20% weight)
            instructor_score = user_instructors.get(course.instructor_id, 0) / total_courses
            score += instructor_score * 0.2
            if instructor_score > 0:
                reasons.append(f"from {course.instructor.get_full_name()}")
            
            # Quality indicators (10% weight)
            avg_rating = course.reviews.filter(is_approved=True).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0
            
            if avg_rating >= 4.0:
                score += 0.1
                reasons.append("highly rated")
            
            if score > 0.1:  # Only include courses with meaningful similarity
                scored_courses.append({
                    'course': course,
                    'score': min(score, 1.0),  # Cap at 1.0
                    'reason': f"Recommended because it {', '.join(reasons[:2])}",
                    'algorithm': 'content_based',
                    'metadata': {
                        'category_match': category_score,
                        'difficulty_match': difficulty_score if 'difficulty_score' in locals() else 0,
                        'instructor_familiarity': instructor_score,
                        'quality_score': avg_rating / 5.0
                    }
                })
        
        # Sort by score and return top recommendations
        scored_courses.sort(key=lambda x: x['score'], reverse=True)
        return scored_courses[:limit]
    
    @staticmethod
    def _popularity_based(user, tenant, limit):
        """Popularity-based recommendations for new users or fallback"""
        from .models import Course, Enrollment
        from django.db.models import Count, Avg, Q
        
        # Get user's enrolled courses to exclude
        enrolled_course_ids = []
        if user.is_authenticated:
            enrolled_course_ids = Enrollment.objects.filter(
                student=user, tenant=tenant
            ).values_list('course_id', flat=True)
        
        # Get popular courses with good ratings
        popular_courses = Course.objects.filter(
            tenant=tenant,
            is_public=True
        ).exclude(
            id__in=enrolled_course_ids
        ).annotate(
            enrollment_count=Count('enrollments'),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            completion_rate=Avg('enrollments__progress_percentage')
        ).filter(
            enrollment_count__gte=5,  # At least 5 enrollments
            avg_rating__gte=3.5  # At least 3.5 rating
        ).order_by('-enrollment_count', '-avg_rating')[:limit]
        
        recommendations = []
        for course in popular_courses:
            recommendations.append({
                'course': course,
                'score': min((course.enrollment_count / 100.0) + (course.avg_rating / 5.0), 1.0),
                'reason': f"Popular course with {course.enrollment_count} students and {course.avg_rating:.1f}★ rating",
                'algorithm': 'popularity_based',
                'metadata': {
                    'enrollment_count': course.enrollment_count,
                    'avg_rating': course.avg_rating or 0,
                    'completion_rate': course.completion_rate or 0
                }
            })
        
        return recommendations
    
    @staticmethod
    def _hybrid_recommendations(user, tenant, limit):
        """Hybrid approach combining multiple algorithms"""
        # Get recommendations from different algorithms
        collaborative_recs = RecommendationService._collaborative_filtering(user, tenant, limit // 2)
        content_recs = RecommendationService._content_based_filtering(user, tenant, limit // 2)
        popularity_recs = RecommendationService._popularity_based(user, tenant, limit // 4)
        
        # Combine and deduplicate
        all_recommendations = {}
        
        # Add collaborative filtering results (highest weight)
        for rec in collaborative_recs:
            course_id = rec['course'].id
            all_recommendations[course_id] = {
                **rec,
                'score': rec['score'] * 0.5,  # 50% weight
                'algorithm': 'hybrid_collaborative'
            }
        
        # Add content-based results
        for rec in content_recs:
            course_id = rec['course'].id
            if course_id in all_recommendations:
                # Boost score if recommended by multiple algorithms
                all_recommendations[course_id]['score'] += rec['score'] * 0.3
                all_recommendations[course_id]['algorithm'] = 'hybrid_multi'
            else:
                all_recommendations[course_id] = {
                    **rec,
                    'score': rec['score'] * 0.4,  # 40% weight
                    'algorithm': 'hybrid_content'
                }
        
        # Fill remaining slots with popularity-based
        current_count = len(all_recommendations)
        if current_count < limit:
            for rec in popularity_recs:
                course_id = rec['course'].id
                if course_id not in all_recommendations:
                    all_recommendations[course_id] = {
                        **rec,
                        'score': rec['score'] * 0.2,  # 20% weight
                        'algorithm': 'hybrid_popularity'
                    }
                    current_count += 1
                    if current_count >= limit:
                        break
        
        # Sort by final score and return
        final_recommendations = list(all_recommendations.values())
        final_recommendations.sort(key=lambda x: x['score'], reverse=True)
        return final_recommendations[:limit]
    
    @staticmethod
    def track_recommendation_interaction(user, course_id, interaction_type, tenant=None):
        """Track user interactions with recommendations for improving the system"""
        from .models import RecommendationInteraction
        
        try:
            RecommendationInteraction.objects.create(
                user=user,
                course_id=course_id,
                interaction_type=interaction_type,
                tenant=tenant
            )
        except Exception as e:
            # Log error but don't fail the main operation
            print(f"Failed to track recommendation interaction: {e}")
    
    @staticmethod
    def get_recommendation_analytics(tenant, days=30):
        """Get analytics on recommendation system performance"""
        from .models import RecommendationInteraction
        from datetime import timedelta
        from django.utils import timezone
        
        since_date = timezone.now() - timedelta(days=days)
        
        interactions = RecommendationInteraction.objects.filter(
            tenant=tenant,
            created_at__gte=since_date
        )
        
        analytics = {
            'total_interactions': interactions.count(),
            'interactions_by_type': {},
            'click_through_rate': 0,
            'conversion_rate': 0,
            'top_recommended_courses': [],
            'algorithm_performance': {}
        }
        
        # Calculate metrics
        interaction_counts = interactions.values('interaction_type').annotate(
            count=Count('id')
        )
        
        for item in interaction_counts:
            analytics['interactions_by_type'][item['interaction_type']] = item['count']
        
        # Calculate rates
        views = analytics['interactions_by_type'].get('view', 0)
        clicks = analytics['interactions_by_type'].get('click', 0)
        enrollments = analytics['interactions_by_type'].get('enroll', 0)
        
        if views > 0:
            analytics['click_through_rate'] = (clicks / views) * 100
            analytics['conversion_rate'] = (enrollments / views) * 100
        
        return analytics


class WishlistService:
    """Service class for wishlist-related operations and analytics"""
    
    @staticmethod
    def get_wishlist_analytics(user, tenant):
        """Get comprehensive wishlist analytics for a user"""
        from .models import Wishlist
        
        wishlist_items = Wishlist.objects.filter(
            user=user,
            tenant=tenant
        ).select_related('course', 'course__instructor')
        
        if not wishlist_items.exists():
            return {
                'total_items': 0,
                'total_value': 0,
                'categories': [],
                'price_ranges': [],
                'availability_status': [],
                'recommendations': []
            }
        
        # Basic statistics
        total_items = wishlist_items.count()
        total_value = sum(float(item.course.price or 0) for item in wishlist_items)
        
        # Category analysis
        categories = {}
        for item in wishlist_items:
            category = item.course.category
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'total_value': 0,
                    'avg_rating': 0
                }
            categories[category]['count'] += 1
            categories[category]['total_value'] += float(item.course.price or 0)
        
        # Price range analysis
        price_ranges = {
            'free': 0,
            'under_50': 0,
            'under_100': 0,
            'under_200': 0,
            'over_200': 0
        }
        
        for item in wishlist_items:
            price = float(item.course.price or 0)
            if price == 0:
                price_ranges['free'] += 1
            elif price <= 50:
                price_ranges['under_50'] += 1
            elif price <= 100:
                price_ranges['under_100'] += 1
            elif price <= 200:
                price_ranges['under_200'] += 1
            else:
                price_ranges['over_200'] += 1
        
        # Availability status
        available_count = sum(1 for item in wishlist_items if item.is_course_available)
        enrolled_count = sum(1 for item in wishlist_items if item.is_enrolled())
        
        return {
            'total_items': total_items,
            'total_value': total_value,
            'average_price': total_value / total_items if total_items > 0 else 0,
            'categories': [
                {'name': k, **v} for k, v in categories.items()
            ],
            'price_ranges': price_ranges,
            'availability_status': {
                'available': available_count,
                'enrolled': enrolled_count,
                'unavailable': total_items - available_count - enrolled_count
            }
        }
    
    @staticmethod
    def generate_wishlist_recommendations(user, tenant, limit=10):
        """Generate course recommendations based on wishlist items"""
        from .models import Wishlist
        
        wishlist_items = Wishlist.objects.filter(
            user=user,
            tenant=tenant
        ).select_related('course')
        
        if not wishlist_items.exists():
            # No wishlist items, return popular courses
            return Course.objects.filter(
                tenant=tenant,
                is_public=True
            ).annotate(
                enrollment_count=Count('enrollments'),
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating', '-enrollment_count')[:limit]
        
        # Get categories and instructors from wishlist
        wishlist_categories = set(item.course.category for item in wishlist_items)
        wishlist_instructors = set(item.course.instructor_id for item in wishlist_items)
        
        # Get courses already in wishlist or enrolled
        excluded_course_ids = set(item.course_id for item in wishlist_items)
        enrolled_course_ids = set(
            Enrollment.objects.filter(
                student=user,
                tenant=tenant
            ).values_list('course_id', flat=True)
        )
        excluded_course_ids.update(enrolled_course_ids)
        
        # Find similar courses
        similar_courses = Course.objects.filter(
            tenant=tenant,
            is_public=True
        ).exclude(
            id__in=excluded_course_ids
        ).annotate(
            enrollment_count=Count('enrollments'),
            avg_rating=Avg('reviews__rating')
        )
        
        # Score courses based on similarity
        recommendations = []
        
        # 1. Same category courses (high priority)
        category_courses = similar_courses.filter(
            category__in=wishlist_categories
        ).order_by('-avg_rating', '-enrollment_count')[:limit//2]
        
        for course in category_courses:
            recommendations.append({
                'course': course,
                'reason': f'Similar to your {course.category} interests',
                'score': 0.8
            })
        
        # 2. Same instructor courses (medium priority)
        instructor_courses = similar_courses.filter(
            instructor_id__in=wishlist_instructors
        ).exclude(
            id__in=[r['course'].id for r in recommendations]
        ).order_by('-avg_rating', '-enrollment_count')[:limit//4]
        
        for course in instructor_courses:
            recommendations.append({
                'course': course,
                'reason': f'From {course.instructor.get_full_name()}, whose courses you\'ve wishlisted',
                'score': 0.6
            })
        
        # 3. Popular courses (low priority)
        popular_courses = similar_courses.exclude(
            id__in=[r['course'].id for r in recommendations]
        ).order_by('-enrollment_count', '-avg_rating')[:limit//4]
        
        for course in popular_courses:
            recommendations.append({
                'course': course,
                'reason': 'Popular among other students',
                'score': 0.4
            })
        
        # Sort by score and return
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]
    
    @staticmethod
    def track_price_changes(tenant):
        """Track price changes for courses in wishlists and notify users"""
        from .models import Wishlist
        from apps.notifications.services import NotificationService
        
        # This would be called periodically (e.g., daily cron job)
        # For now, it's a placeholder for the price tracking logic
        
        wishlist_items = Wishlist.objects.filter(
            tenant=tenant,
            notify_price_change=True
        ).select_related('course', 'user')
        
        price_changes = []
        
        for item in wishlist_items:
            # In a real implementation, you'd compare with stored price history
            # For now, we'll just return the structure
            current_price = item.course.price
            # previous_price = get_previous_price(item.course)  # Would be implemented
            
            # if current_price != previous_price:
            #     price_changes.append({
            #         'wishlist_item': item,
            #         'old_price': previous_price,
            #         'new_price': current_price,
            #         'change_percentage': ((current_price - previous_price) / previous_price) * 100
            #     })
        
        return price_changes
    
    @staticmethod
    def bulk_enroll_from_wishlist(user, tenant, course_ids):
        """Enroll user in multiple courses from their wishlist"""
        from .models import Wishlist
        
        wishlist_items = Wishlist.objects.filter(
            user=user,
            tenant=tenant,
            course_id__in=course_ids
        ).select_related('course')
        
        successful_enrollments = []
        failed_enrollments = []
        
        for item in wishlist_items:
            try:
                # Check if can enroll
                can_enroll, message = CourseService.can_enroll_in_course(user, item.course)
                
                if can_enroll:
                    enrollment = EnrollmentService.enroll_student(user, item.course, tenant)
                    successful_enrollments.append({
                        'course': item.course,
                        'enrollment': enrollment
                    })
                    # Remove from wishlist after successful enrollment
                    item.delete()
                else:
                    failed_enrollments.append({
                        'course': item.course,
                        'reason': message
                    })
            except Exception as e:
                failed_enrollments.append({
                    'course': item.course,
                    'reason': str(e)
                })
        
        return {
            'successful': successful_enrollments,
            'failed': failed_enrollments,
            'total_enrolled': len(successful_enrollments),
            'total_failed': len(failed_enrollments)
        }