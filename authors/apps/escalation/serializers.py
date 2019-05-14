from .models import EscalationModel

from rest_framework import serializers


class EscalationSerializer(serializers.ModelSerializer):
    """
    Escalation serializer
    """
    # reporter = serializers.ReadOnlyField()
    article = serializers.ReadOnlyField(source='get_articles_details')
    reason = serializers.ChoiceField(
        choices=['Plagiarism', 'Rule Violation', 'Spam'])

    class Meta:
        model = EscalationModel
        fields = ('article', 'reason', 'description')
