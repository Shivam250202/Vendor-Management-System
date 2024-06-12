# vendors/models.py

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F, Avg, Count

class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=100, unique=True)
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)

    def clean(self):
        if self.on_time_delivery_rate < 0 or self.on_time_delivery_rate > 100:
            raise ValidationError('On-time delivery rate must be between 0 and 100.')
        if self.quality_rating_avg < 0 or self.quality_rating_avg > 5:
            raise ValidationError('Quality rating must be between 0 and 5.')
        if self.average_response_time < 0:
            raise ValidationError('Average response time must be non-negative.')
        if self.fulfillment_rate < 0 or self.fulfillment_rate > 100:
            raise ValidationError('Fulfillment rate must be between 0 and 100.')

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    po_number = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(default=timezone.now)
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.quality_rating is not None and (self.quality_rating < 0 or self.quality_rating > 5):
            raise ValidationError('Quality rating must be between 0 and 5.')
        if self.quantity <= 0:
            raise ValidationError('Quantity must be a positive integer.')

    def __str__(self):
        return self.po_number

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

    def __str__(self):
        return f"{self.vendor.name} - {self.date}"

# Signals for updating Vendor performance metrics
@receiver(post_save, sender=PurchaseOrder)
def update_vendor_metrics(sender, instance, **kwargs):
    vendor = instance.vendor

    # On-Time Delivery Rate
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
    on_time_orders = completed_orders.filter(delivery_date__lte=F('order_date'))
    vendor.on_time_delivery_rate = (on_time_orders.count() / completed_orders.count() * 100) if completed_orders.exists() else 0

    # Quality Rating Average
    total_quality_rating = completed_orders.aggregate(Avg('quality_rating'))['quality_rating__avg']
    vendor.quality_rating_avg = total_quality_rating if total_quality_rating else 0

    # Average Response Time
    acknowledged_orders = completed_orders.filter(acknowledgment_date__isnull=False)
    total_response_time = sum((order.acknowledgment_date - order.issue_date).total_seconds() for order in acknowledged_orders)
    vendor.average_response_time = (total_response_time / acknowledged_orders.count()) if acknowledged_orders.exists() else 0

    # Fulfillment Rate
    successful_orders = completed_orders.exclude(status='canceled')
    vendor.fulfillment_rate = (successful_orders.count() / completed_orders.count() * 100) if completed_orders.exists() else 0

    vendor.save()

    # Store historical performance data
    HistoricalPerformance.objects.create(
        vendor=vendor,
        on_time_delivery_rate=vendor.on_time_delivery_rate,
        quality_rating_avg=vendor.quality_rating_avg,
        average_response_time=vendor.average_response_time,
        fulfillment_rate=vendor.fulfillment_rate
    )
