
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route, renderer_classes, authentication_classes, permission_classes
from rest_framework_recursive.fields import RecursiveField

from organisation.models import Location, OrgUnit, DepartmentUser


class DepartmentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentUser
        fields = ('id', 'name', 'preferred_name', 'email', 'username', 'title', 'employee_id', 'telephone', 'extension', 'mobile_phone', 'location', 'photo_ad', 'org_unit_chain', 'manager_chain')


class DepartmentUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DepartmentUser.objects.filter(**DepartmentUser.ACTIVE_FILTER).exclude(account_type__in=DepartmentUser.ACCOUNT_TYPE_EXCLUDE)
    serializer_class = DepartmentUserSerializer


class DepartmentTreeSerializer(serializers.ModelSerializer):
    children = serializers.ListField(source='children_filtered', child=RecursiveField())
    class Meta:
        model = DepartmentUser
        fields = ('id', 'name', 'title', 'children')


class DepartmentTreeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DepartmentUser.objects.filter(**DepartmentUser.ACTIVE_FILTER).exclude(account_type__in=DepartmentUser.ACCOUNT_TYPE_EXCLUDE).filter(parent__isnull=True)
    serializer_class = DepartmentTreeSerializer


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'point', 'manager', 'address', 'pobox', 'phone', 'fax', 'email', 'url', 'bandwidth_url')


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.filter(active=True)
    serializer_class = LocationSerializer


class OrgUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgUnit
        fields = ('id', 'name', 'acronym', 'unit_type', 'manager', 'parent', 'location')


class OrgUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrgUnit.objects.filter(active=True)
    serializer_class = OrgUnitSerializer


class OrgTreeSerializer(serializers.ModelSerializer):
    children = serializers.ListField(source='children.all', child=RecursiveField())
    class Meta:
        model = OrgUnit
        fields = ('id', 'name', 'children')


class OrgTreeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrgUnit.objects.filter(active=True, parent__isnull=True)
    serializer_class = OrgTreeSerializer
