import stripe
import requests
import base64
from decimal import Decimal
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from .models import Payment, Invoice, Subscription, InvoiceLineItem


class StripeService:
    """Stripe payment processing service"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def create_payment_intent(self, amount, currency='usd', metadata=None):
        """Create Stripe payment intent for one-time payments"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            return intent
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    def confirm_payment(self, payment_intent_id):
        """Confirm payment intent"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent.status == 'succeeded'
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    def create_customer(self, email, name=None, metadata=None):
        """Create Stripe customer for subscriptions"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    def create_subscription(self, customer_id, price_id, metadata=None):
        """Create Stripe subscription"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                metadata=metadata or {},
                expand=['latest_invoice.payment_intent']
            )
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    def cancel_subscription(self, subscription_id):
        """Cancel Stripe subscription"""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    def retrieve_subscription(self, subscription_id):
        """Retrieve Stripe subscription"""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")


class PayPalService:
    """PayPal payment processing service"""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.base_url = getattr(settings, 'PAYPAL_BASE_URL', 'https://api.sandbox.paypal.com')
        self.access_token = None
    
    def get_access_token(self):
        """Get PayPal access token"""
        if self.access_token:
            return self.access_token
        
        url = f"{self.base_url}/v1/oauth2/token"
        
        # Encode credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = 'grant_type=client_credentials'
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            return self.access_token
            
        except requests.RequestException as e:
            raise Exception(f"PayPal authentication error: {str(e)}")
    
    def create_order(self, amount, currency='USD', description="Course Payment", custom_id=None):
        """Create PayPal order"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/v2/checkout/orders"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'PayPal-Request-Id': str(timezone.now().timestamp())
        }
        
        purchase_unit = {
            'amount': {
                'currency_code': currency,
                'value': str(amount)
            },
            'description': description
        }
        
        # Add custom_id for tracking
        if custom_id:
            purchase_unit['custom_id'] = str(custom_id)
        
        order_data = {
            'intent': 'CAPTURE',
            'purchase_units': [purchase_unit],
            'application_context': {
                'return_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/payment/success",
                'cancel_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/payment/cancel"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=order_data)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise Exception(f"PayPal order creation error: {str(e)}")
    
    def capture_order(self, order_id):
        """Capture PayPal order"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            
            capture_data = response.json()
            return capture_data.get('status') == 'COMPLETED'
            
        except requests.RequestException as e:
            raise Exception(f"PayPal capture error: {str(e)}")


class BankTransferService:
    """Bank transfer payment handling service"""
    
    @staticmethod
    def create_bank_transfer_payment(user, amount, course=None, subscription=None, tenant=None):
        """Create bank transfer payment record"""
        payment = Payment.objects.create(
            user=user,
            course=course,
            subscription=subscription,
            amount=amount,
            payment_method='bank_transfer',
            status='pending',
            tenant=tenant,
            description=f"Bank transfer payment for {course.title if course else 'subscription'}"
        )
        
        # Generate bank transfer reference
        payment.bank_transfer_reference = f"BT-{payment.id.hex[:8].upper()}"
        payment.save()
        
        return payment
    
    @staticmethod
    def approve_bank_transfer(payment_id, approved_by):
        """Approve bank transfer payment"""
        try:
            payment = Payment.objects.get(id=payment_id, payment_method='bank_transfer')
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.bank_transfer_approved_by = approved_by
            payment.save()
            
            return True
        except Payment.DoesNotExist:
            return False
    
    @staticmethod
    def reject_bank_transfer(payment_id, reason=""):
        """Reject bank transfer payment"""
        try:
            payment = Payment.objects.get(id=payment_id, payment_method='bank_transfer')
            payment.status = 'failed'
            payment.failed_at = timezone.now()
            payment.metadata['rejection_reason'] = reason
            payment.save()
            
            return True
        except Payment.DoesNotExist:
            return False


class SubscriptionService:
    """Subscription billing service"""
    
    # Subscription pricing (in USD)
    SUBSCRIPTION_PRICES = {
        'basic': {'monthly': Decimal('29.00'), 'yearly': Decimal('290.00')},
        'pro': {'monthly': Decimal('99.00'), 'yearly': Decimal('990.00')},
        'enterprise': {'monthly': Decimal('299.00'), 'yearly': Decimal('2990.00')},
    }
    
    @staticmethod
    def create_subscription(organization, plan, billing_cycle='monthly', payment_method='stripe'):
        """Create new subscription for organization"""
        if plan not in SubscriptionService.SUBSCRIPTION_PRICES:
            raise ValueError(f"Invalid plan: {plan}")
        
        if billing_cycle not in ['monthly', 'yearly']:
            raise ValueError(f"Invalid billing cycle: {billing_cycle}")
        
        amount = SubscriptionService.SUBSCRIPTION_PRICES[plan][billing_cycle]
        
        # Calculate billing period
        start_date = timezone.now()
        if billing_cycle == 'monthly':
            end_date = start_date + timedelta(days=30)
        else:  # yearly
            end_date = start_date + timedelta(days=365)
        
        subscription = Subscription.objects.create(
            organization=organization,
            tenant=organization,  # Organization is the tenant
            plan=plan,
            billing_cycle=billing_cycle,
            amount=amount,
            current_period_start=start_date,
            current_period_end=end_date,
            status='active'
        )
        
        if payment_method == 'stripe':
            stripe_service = StripeService()
            
            # Create Stripe customer if not exists
            if not subscription.stripe_customer_id:
                customer = stripe_service.create_customer(
                    email=organization.name + '@organization.com',  # Use org email if available
                    name=organization.name,
                    metadata={'organization_id': str(organization.id)}
                )
                subscription.stripe_customer_id = customer.id
                subscription.save()
        
        return subscription
    
    @staticmethod
    def process_subscription_payment(subscription, payment_method='stripe'):
        """Process subscription payment"""
        payment = Payment.objects.create(
            user=None,  # Subscription payments are organization-level
            subscription=subscription,
            payment_type='subscription',
            amount=subscription.amount,
            payment_method=payment_method,
            tenant=subscription.tenant,
            description=f"{subscription.plan.title()} subscription - {subscription.billing_cycle}"
        )
        
        try:
            if payment_method == 'stripe':
                stripe_service = StripeService()
                intent = stripe_service.create_payment_intent(
                    amount=subscription.amount,
                    metadata={
                        'payment_id': str(payment.id),
                        'subscription_id': str(subscription.id),
                        'organization_id': str(subscription.organization.id)
                    }
                )
                payment.stripe_payment_intent_id = intent.id
                payment.save()
                
                return {
                    'payment_id': payment.id,
                    'client_secret': intent.client_secret
                }
            
            elif payment_method == 'bank_transfer':
                return BankTransferService.create_bank_transfer_payment(
                    user=None,
                    amount=subscription.amount,
                    subscription=subscription,
                    tenant=subscription.tenant
                )
                
        except Exception as e:
            payment.mark_failed(str(e))
            raise e
    
    @staticmethod
    def renew_subscription(subscription):
        """Renew subscription for next billing period"""
        if subscription.billing_cycle == 'monthly':
            subscription.current_period_start = subscription.current_period_end
            subscription.current_period_end = subscription.current_period_end + timedelta(days=30)
        else:  # yearly
            subscription.current_period_start = subscription.current_period_end
            subscription.current_period_end = subscription.current_period_end + timedelta(days=365)
        
        subscription.save()
        
        # Create payment for renewal
        return SubscriptionService.process_subscription_payment(subscription)


class PDFInvoiceService:
    """PDF invoice generation service"""
    
    @staticmethod
    def generate_invoice_pdf(invoice):
        """Generate PDF for invoice"""
        try:
            # Try to import reportlab for PDF generation
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from io import BytesIO
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph(f"Invoice {invoice.invoice_number}", title_style))
            story.append(Spacer(1, 20))
            
            # Company info
            company_info = [
                ["Edurise Learning Management System"],
                ["support@edurise.com"],
                ["www.edurise.com"]
            ]
            company_table = Table(company_info, colWidths=[4*inch])
            company_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            story.append(company_table)
            story.append(Spacer(1, 20))
            
            # Invoice details
            details_data = [
                ["Bill To:", f"Invoice Date: {invoice.issue_date.strftime('%B %d, %Y')}"],
                [invoice.billing_name, f"Due Date: {invoice.due_date.strftime('%B %d, %Y')}"],
                [invoice.billing_email, f"Status: {invoice.get_status_display()}"],
            ]
            
            if invoice.billing_address_line1:
                details_data.append([invoice.billing_address_line1, ""])
                if invoice.billing_address_line2:
                    details_data.append([invoice.billing_address_line2, ""])
                details_data.append([
                    f"{invoice.billing_city}, {invoice.billing_state} {invoice.billing_postal_code}",
                    ""
                ])
                details_data.append([invoice.billing_country, ""])
            
            details_table = Table(details_data, colWidths=[3*inch, 3*inch])
            details_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(details_table)
            story.append(Spacer(1, 30))
            
            # Line items
            items_data = [["Description", "Quantity", "Unit Price", "Total"]]
            for item in invoice.line_items.all():
                items_data.append([
                    item.description,
                    str(item.quantity),
                    f"${item.unit_price}",
                    f"${item.total_price}"
                ])
            
            # Add totals
            items_data.append(["", "", "Subtotal:", f"${invoice.subtotal}"])
            if invoice.tax_amount > 0:
                items_data.append(["", "", "Tax:", f"${invoice.tax_amount}"])
            if invoice.discount_amount > 0:
                items_data.append(["", "", "Discount:", f"-${invoice.discount_amount}"])
            items_data.append(["", "", "Total:", f"${invoice.total_amount} {invoice.currency}"])
            
            items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Description column left-aligned
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -4), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(items_table)
            
            # Notes
            if invoice.notes:
                story.append(Spacer(1, 20))
                story.append(Paragraph("Notes:", styles['Heading3']))
                story.append(Paragraph(invoice.notes, styles['Normal']))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_text = "Thank you for choosing Edurise!"
            story.append(Paragraph(footer_text, styles['Normal']))
            
            doc.build(story)
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except ImportError:
            # If reportlab is not available, return None
            return None
    
    @staticmethod
    def save_invoice_pdf(invoice):
        """Generate and save PDF for invoice"""
        pdf_content = PDFInvoiceService.generate_invoice_pdf(invoice)
        
        if pdf_content:
            filename = f"invoice_{invoice.invoice_number}.pdf"
            invoice.pdf_file.save(
                filename,
                ContentFile(pdf_content),
                save=True
            )
            return True
        return False


class InvoiceService:
    """Invoice generation and management service"""
    
    @staticmethod
    def get_billing_address(payment):
        """Get billing address from user profile or organization"""
        billing_address = {
            'address_line1': '',
            'address_line2': '',
            'city': '',
            'state': '',
            'postal_code': '',
            'country': 'US'
        }
        
        try:
            if payment.subscription and payment.subscription.organization:
                # Get organization billing address
                org = payment.subscription.organization
                if hasattr(org, 'billing_address'):
                    billing_address.update({
                        'address_line1': getattr(org.billing_address, 'address_line1', ''),
                        'address_line2': getattr(org.billing_address, 'address_line2', ''),
                        'city': getattr(org.billing_address, 'city', ''),
                        'state': getattr(org.billing_address, 'state', ''),
                        'postal_code': getattr(org.billing_address, 'postal_code', ''),
                        'country': getattr(org.billing_address, 'country', 'US'),
                    })
            elif payment.user:
                # Get user billing address from profile
                try:
                    profile = payment.user.profile
                    if hasattr(profile, 'billing_address'):
                        billing_address.update({
                            'address_line1': getattr(profile.billing_address, 'address_line1', ''),
                            'address_line2': getattr(profile.billing_address, 'address_line2', ''),
                            'city': getattr(profile.billing_address, 'city', ''),
                            'state': getattr(profile.billing_address, 'state', ''),
                            'postal_code': getattr(profile.billing_address, 'postal_code', ''),
                            'country': getattr(profile.billing_address, 'country', 'US'),
                        })
                except:
                    pass
        except:
            pass
        
        return billing_address
    
    @staticmethod
    def create_invoice_for_payment(payment):
        """Create invoice for a payment"""
        if payment.course:
            billing_name = payment.user.get_full_name() or payment.user.email
            billing_email = payment.user.email
            description = f"Course: {payment.course.title}"
        elif payment.subscription:
            billing_name = payment.subscription.organization.name
            billing_email = f"billing@{payment.subscription.organization.subdomain}.com"
            description = f"{payment.subscription.plan.title()} Subscription - {payment.subscription.billing_cycle}"
        else:
            billing_name = payment.user.get_full_name() or payment.user.email
            billing_email = payment.user.email
            description = "Payment"
        
        # Calculate due date (immediate for completed payments, 30 days for pending)
        if payment.status == 'completed':
            due_date = timezone.now().date()
        else:
            due_date = timezone.now().date() + timedelta(days=30)
        
        # Get billing address from user profile or organization
        billing_address = InvoiceService.get_billing_address(payment)
        
        invoice = Invoice.objects.create(
            user=payment.user,
            organization=payment.subscription.organization if payment.subscription else None,
            invoice_type='subscription' if payment.subscription else 'payment',
            payment=payment,
            subscription=payment.subscription,
            subtotal=payment.amount,
            total_amount=payment.amount,
            currency=payment.currency,
            due_date=due_date,
            description=description,
            billing_name=billing_name,
            billing_email=billing_email,
            billing_address_line1=billing_address.get('address_line1', ''),
            billing_address_line2=billing_address.get('address_line2', ''),
            billing_city=billing_address.get('city', ''),
            billing_state=billing_address.get('state', ''),
            billing_postal_code=billing_address.get('postal_code', ''),
            billing_country=billing_address.get('country', 'US'),
            tenant=payment.tenant
        )
        
        # Calculate tax based on billing location
        invoice.calculate_tax()
        
        # Create line item
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description=description,
            quantity=Decimal('1.00'),
            unit_price=payment.amount,
            total_price=payment.amount,
            course=payment.course
        )
        
        return invoice
    
    @staticmethod
    def send_invoice(invoice):
        """Send invoice via email"""
        subject = f"Invoice {invoice.invoice_number} from Edurise"
        
        context = {
            'invoice': invoice,
            'line_items': invoice.line_items.all(),
            'frontend_url': settings.FRONTEND_URL
        }
        
        html_message = render_to_string('emails/invoice.html', context)
        plain_message = render_to_string('emails/invoice.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invoice.billing_email],
            fail_silently=False
        )
        
        invoice.sent_at = timezone.now()
        invoice.status = 'sent'
        invoice.save()
        
        # Generate and save PDF
        try:
            PDFInvoiceService.save_invoice_pdf(invoice)
        except Exception:
            # PDF generation is optional, don't fail if it doesn't work
            pass
        
        return True
    
    @staticmethod
    def mark_invoice_paid(invoice):
        """Mark invoice as paid"""
        invoice.mark_paid()
        
        # If associated payment exists, mark it as completed
        if invoice.payment and invoice.payment.status != 'completed':
            invoice.payment.mark_completed()


class PaymentService:
    """Main payment processing service"""
    
    @staticmethod
    def process_course_payment(user, course, amount, payment_method, tenant):
        """Process payment for course enrollment"""
        payment = Payment.objects.create(
            user=user,
            course=course,
            payment_type='course',
            amount=amount,
            payment_method=payment_method,
            tenant=tenant,
            description=f"Course enrollment: {course.title}"
        )
        
        try:
            if payment_method == 'stripe':
                stripe_service = StripeService()
                intent = stripe_service.create_payment_intent(
                    amount=amount,
                    metadata={
                        'payment_id': str(payment.id),
                        'course_id': str(course.id),
                        'user_id': str(user.id)
                    }
                )
                payment.stripe_payment_intent_id = intent.id
                payment.save()
                
                return {
                    'payment_id': payment.id,
                    'client_secret': intent.client_secret
                }
                
            elif payment_method == 'paypal':
                paypal_service = PayPalService()
                order = paypal_service.create_order(
                    amount=amount,
                    description=f"Course: {course.title}",
                    custom_id=str(payment.id)  # Include payment ID for tracking
                )
                payment.paypal_order_id = order.get('id')
                payment.save()
                
                return {
                    'payment_id': payment.id,
                    'order_id': order.get('id'),
                    'approval_url': next(
                        (link['href'] for link in order.get('links', []) 
                         if link['rel'] == 'approve'), None
                    )
                }
                
            elif payment_method == 'bank_transfer':
                return BankTransferService.create_bank_transfer_payment(
                    user=user,
                    amount=amount,
                    course=course,
                    tenant=tenant
                )
                
        except Exception as e:
            payment.mark_failed(str(e))
            raise e
    
    @staticmethod
    def confirm_payment(payment_id):
        """Confirm payment completion"""
        try:
            payment = Payment.objects.get(id=payment_id)
            
            if payment.payment_method == 'stripe' and payment.stripe_payment_intent_id:
                stripe_service = StripeService()
                if stripe_service.confirm_payment(payment.stripe_payment_intent_id):
                    payment.mark_completed()
                    
                    # Create and send invoice
                    invoice = InvoiceService.create_invoice_for_payment(payment)
                    InvoiceService.send_invoice(invoice)
                    
                    return True
                    
            elif payment.payment_method == 'paypal' and payment.paypal_order_id:
                paypal_service = PayPalService()
                if paypal_service.capture_order(payment.paypal_order_id):
                    payment.mark_completed()
                    
                    # Create and send invoice
                    invoice = InvoiceService.create_invoice_for_payment(payment)
                    InvoiceService.send_invoice(invoice)
                    
                    return True
                    
            return False
            
        except Payment.DoesNotExist:
            return False