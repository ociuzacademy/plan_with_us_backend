from pyexpat import features
from rest_framework import serializers
from .models import tbl_register, tbl_engineer

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_register
        fields = '__all__'


from rest_framework import serializers
from .models import tbl_engineer
class EngineerSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)
    id_proof = serializers.FileField(required=False)

    class Meta:
        model = tbl_engineer
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if instance.profile_image:
            rep['profile_image'] = instance.profile_image.url  # returns "/media/..."
        if instance.id_proof:
            rep['id_proof'] = instance.id_proof.url

        return rep

class EngineerLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_engineer
        fields = ['email', 'password']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        try:
            engineer = tbl_engineer.objects.get(email=email, password=password)
        except tbl_engineer.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        return engineer
    
class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_register
        fields = ['email', 'password']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        try:
            user = tbl_register.objects.get(email=email, password=password)
        except tbl_register.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        return user
    



# serializers.py
from rest_framework import serializers
from adminapp.models import Category
from .models import UserRequest
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

from houseprojectapp.models import tbl_register   # import your user model
from rest_framework import serializers
from houseprojectapp.models import tbl_register
from .models import UserRequest
from adminapp.models import Category

class UserRequestSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source='user',
        queryset=tbl_register.objects.all(),
        required=True
    )
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = UserRequest
        fields = ['id', 'user_id', 'category', 'cent', 'sqft', 'expected_amount', 'created_at']





from rest_framework import serializers
from adminapp.models import Category





# serializers.py
# Profile Serializer
class EngineerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_engineer
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'password',
            'profile_image', 'id_proof', 'status', 'user_type', 'available'
        ]

from rest_framework import serializers
from .models import tbl_engineer

class AvailableStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_engineer
        fields = ['available']



from rest_framework import serializers
from adminapp.models import ProductCategory

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name']



from rest_framework import serializers
from adminapp.models import Products
class productSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'name', 'image', 'price', 'quantity', 'description', 'created_at']
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url  # returns "/media/..."
        return rep
    


    # serializers.py



from rest_framework import serializers
from .models import Work, WorkImage
from adminapp.models import HouseFeature, Category
from .models import tbl_engineer  # adjust import if needed

class WorkImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = WorkImage
        fields = ['id', 'image']

    def get_image(self, obj):
        return f"/media/{obj.image}" if obj.image else None

# houseprojectapp/serializers.py
from rest_framework import serializers
from .models import Work, WorkImage
from adminapp.models import HouseFeature, Category

class WorkSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True),
        write_only=True,
        required=False
    )

    additional_features = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )


    class Meta:
        model = Work
        fields = [
            'id', 'engineer', 'project_name', 'category', 'cent', 'squarefeet',
            'expected_amount', 'additional_amount', 'total_amount',
            'additional_features', 'time_duration',
            'property_image', 'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        features = validated_data.pop('additional_features', [])

        # store features as comma separated string
        validated_data['additional_features'] = ",".join(map(str, features))

        work = Work.objects.create(**validated_data)

        for img in images:
            WorkImage.objects.create(work=work, image=img)

        return work
    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        features = validated_data.pop('additional_features', None)

        # Update normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

            # Update additional features (convert list to comma string)
        if features is not None:
            instance.additional_features = ",".join(map(str, features))

        instance.save()

    # If new images provided, add them
        if images:
            for img in images:
                WorkImage.objects.create(work=instance, image=img)

        return instance


class WorkReadSerializer(serializers.ModelSerializer):
    engineer = serializers.CharField(source='engineer.name')
    category = serializers.CharField(source='category.name')
    additional_features = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    property_image = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            'id', 'engineer','engineer_id', 'project_name', 'category', 'cent', 'squarefeet',
            'expected_amount', 'additional_amount', 'total_amount',
            'additional_features', 'time_duration',
            'property_image', 'images'
        ]

    def get_additional_features(self, obj):
        ids = obj.get_feature_list()
        return list(HouseFeature.objects.filter(id__in=ids).values_list("name", flat=True))

    def get_images(self, obj):
        return [f"/media/{img.image}" for img in obj.images.all()]

    def get_property_image(self, obj):
        return f"/media/{obj.property_image}" if obj.property_image else None


class HouseFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseFeature
        fields = ['id', 'name']
        





from rest_framework import serializers
from .models import EngineerBooking
from rest_framework import serializers
from .models import EngineerBooking

from rest_framework import serializers
from .models import EngineerBooking
from adminapp.models import HouseFeature
import json
from datetime import datetime


class EngineerBookingSerializer(serializers.ModelSerializer):
    cent = serializers.CharField(read_only=True)
    sqft = serializers.CharField(read_only=True)
    expected_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    features = serializers.PrimaryKeyRelatedField(
        many=True, queryset=HouseFeature.objects.all()
    )

    class Meta:
        model = EngineerBooking
        fields = '__all__'

    # ✅ Convert input (POST/PUT/PATCH)
    def to_internal_value(self, data):
        data = data.dict()   # now it's a normal dict

        # --- handle features ---
        raw = data.get('features')
        parsed = None

        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, list):
                    parsed = [parsed]
            except json.JSONDecodeError:
                parsed = [int(x.strip()) for x in raw.split(',') if x.strip().isdigit()]

        elif isinstance(raw, list):
            parsed = []
            for item in raw:
                if isinstance(item, str) and item.startswith('['):
                    try:
                        res = json.loads(item)
                        if isinstance(res, list):
                            parsed.extend(res)
                        else:
                            parsed.append(res)
                    except Exception:
                        pass
                else:
                    try:
                        parsed.append(int(item))
                    except Exception:
                        pass

        elif isinstance(raw, int):
            parsed = [raw]

        # ✅ FIX HERE
        if parsed is not None:
            data['features'] = parsed

        # --- date conversion ---
        date_fields = ['start_date', 'end_date']
        for field in date_fields:
            val = data.get(field)
            if val:
                try:
                    parsed_date = datetime.strptime(val, '%d-%m-%Y').date()
                    data[field] = parsed_date.isoformat()
                except ValueError:
                    pass

        return super().to_internal_value(data)
    # ✅ Convert output (GET)
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Format suggestion file URL
        if instance.suggestion:
            rep['suggestion'] = instance.suggestion.url

        # Format dates to dd/mm/yyyy for response
        date_fields = ['start_date', 'end_date']
        for field in date_fields:
            val = getattr(instance, field)
            if val:
                rep[field] = val.strftime('%d-%m-%Y')

        return rep

class EngineerBookingReadSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    engineer_name = serializers.CharField(source='engineer.name', read_only=True)
    engineer_phone = serializers.CharField(source='engineer.phone', read_only=True)
    features = serializers.StringRelatedField(many=True, read_only=True)
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = EngineerBooking
        fields = [
            'id', 'user_name', 'user_phone', 'engineer_id', 'engineer_name', 'engineer_phone',
            'address', 'start_date', 'end_date', 'suggestion',
            'cent', 'sqft', 'expected_amount', 'features', 'created_at', 'status',
            'user_request','reject_reason','advance_booking','payment_status'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Format suggestion
        if instance.suggestion:
            rep['suggestion'] = instance.suggestion.url

        # ✅ Format date fields
        for field in ['start_date', 'end_date']:
            val = getattr(instance, field)
            if val:
                rep[field] = val.strftime('%d-%m-%Y')

        return rep
    def get_payment_status(self, obj):
        if hasattr(obj, 'payment') and obj.payment:
            return obj.payment.status
        return None

from .models import EngineerBookingPayment
from .serializers import *
class AdvanceBookingPaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    engineer_name = serializers.CharField(source='booking.engineer.name', read_only=True)

    class Meta:
        model = EngineerBookingPayment
        fields = [
            'id', 'booking', 'user', 'user_name', 'engineer_name',
            'payment_type', 'status',
            'card_holder_name', 'card_number', 'expiry_date', 'cvv',
            'total_amount', 'created_at','payment_type'
        ]

from rest_framework import serializers
from .models import EngineerBooking, EngineerBookingPayment

from rest_framework import serializers
from .models import EngineerBooking, EngineerBookingPayment


class EngineerBookingPaymentNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngineerBookingPayment
        fields = '__all__'


class EngineerBookingWithPaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    engineer_name = serializers.CharField(source='engineer.name', read_only=True)
    engineer_phone = serializers.CharField(source='engineer.phone', read_only=True)

    features = serializers.StringRelatedField(many=True, read_only=True)

    payment = EngineerBookingPaymentNestedSerializer(read_only=True)

    # ✅ ADD THIS
    additional_amount = serializers.SerializerMethodField()

    class Meta:
        model = EngineerBooking
        fields = '__all__'   # no need to manually add

    def get_additional_amount(self, obj):
        from houseprojectapp.models import Work

        work = Work.objects.filter(
            engineer=obj.engineer
        ).order_by('-created_at').first()

        if work:
            return work.additional_amount

        return 0

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Format dates
        for field in ['start_date', 'end_date']:
            val = getattr(instance, field)
            if val:
                rep[field] = val.strftime('%d/%m/%Y')

        if instance.suggestion:
            rep['suggestion'] = instance.suggestion.url

        return rep

from rest_framework import serializers
from .models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    engineer_name = serializers.CharField(source='engineer.name', read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id',
            'user',
            'engineer',
            'user_name',
            'engineer_name',
            'rating',
            'comments',
            'created_at'
        ]
        read_only_fields = ['created_at']





from .serializers import *
from .models import *
# cart and booking serializers
# -----------------------------
# Booking & Cart Serializers
# -----------------------------
from rest_framework import serializers
from .models import ProductBookings

from rest_framework import serializers
from .models import ProductBookings

class ProductBookingSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.FloatField(required=True)  # ✅ Must be sent by Flutter

    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = ProductBookings
        fields = [
            'id', 'user_id', 'user_name',
            'product_id', 'product_name',
            'category_name', 'quantity',
            'total_price', 'status', 'booking_date'
        ]

class CartSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'user_id', 'product_id',
            'product_name','product_image', 'category_name',
            'quantity', 'total_price', 'status', 'created_at'
        ]
    def to_representation(self, instance): 
        rep = super().to_representation(instance)
        
        if instance.product.image:
            rep['product_image'] = instance.product.image.url  # returns "/media/..."
        return rep

from rest_framework import serializers
from .models import BookingPayment

class BookingPaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    product_name = serializers.CharField(source='booking.product.name', read_only=True)

    class Meta:
        model = BookingPayment
        fields = [
            'id', 'booking', 'user', 'user_name', 'product_name',
            'payment_type', 'status', 'upi_id',
            'card_holder_name', 'card_number', 'expiry_date', 'cvv',
            'total_amount', 'created_at','payment_choice'
        ]

from rest_framework import serializers
from .models import CartPayment

class CartPaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = CartPayment
        fields = [
            'id', 'user', 'user_name', 'cart_ids',
            'payment_type', 'status', 'upi_id',
            'card_holder_name', 'card_number', 'expiry_date', 'cvv',
            'total_amount', 'created_at','payment_choice'
        ]
