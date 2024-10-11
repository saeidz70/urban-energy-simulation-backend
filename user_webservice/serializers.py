from rest_framework import serializers


class MapCenterSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    zoom = serializers.IntegerField()


class CensusSerializer(serializers.Serializer):
    data = serializers.DictField()
    configuration = serializers.DictField()


class HeightSerializer(serializers.Serializer):
    data = serializers.DictField()
    configuration = serializers.DictField()


class BuildingUseSerializer(serializers.Serializer):
    data = serializers.JSONField()  # Assuming GeoJSON format
    configuration = serializers.DictField()


class ProjectDataSerializer(serializers.Serializer):
    projectName = serializers.CharField(max_length=100)
    polygonArray = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField()
        )
    )
    mapCenter = MapCenterSerializer()
    scenarioList = serializers.ListField(child=serializers.CharField())
    crs = serializers.IntegerField()
    Census = CensusSerializer()
    Height = HeightSerializer()
    BuildingUse = BuildingUseSerializer()
