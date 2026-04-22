from enum import Enum


class PublicationStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class InquiryStatus(str, Enum):
    new = "new"
    triaged = "triaged"
    responded = "responded"
    closed = "closed"
    spam = "spam"


class OutboxStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class StaffRole(str, Enum):
    super_admin = "super_admin"
    sales_admin = "sales_admin"
    content_admin = "content_admin"
    recruiter = "recruiter"
    viewer = "viewer"


class TaxonomyGroup(str, Enum):
    framework_or_standard = "framework_or_standard"
    regulation = "regulation"
    capability = "capability"
    audience = "audience"
    product_vendor_line = "product_vendor_line"