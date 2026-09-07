from rest_framework import serializers
from apps.interviews.models import Category, Tag, Company, Interview, InterviewRound, Question, CodingProblem, Note

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class InterviewRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewRound
        fields = '__all__'
        read_only_fields = ['interview']

class InterviewSerializer(serializers.ModelSerializer):
    rounds = InterviewRoundSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Interview
        fields = '__all__'
        read_only_fields = ['user']

class CodingProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingProblem
        fields = '__all__'
        read_only_fields = ['question']

class QuestionSerializer(serializers.ModelSerializer):
    coding_details = CodingProblemSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['user', 'slug']

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ['user']
