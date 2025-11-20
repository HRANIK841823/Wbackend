from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField

# Patch Django's default auto field
models.AutoField = ObjectIdAutoField
models.BigAutoField = ObjectIdAutoField
