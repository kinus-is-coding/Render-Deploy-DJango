from rest_framework import serializers
from .models import Post, QuizQuestion

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question_text', 'choices_json', 'correct_choice_id']



class PostSerializer(serializers.ModelSerializer):
    questions = serializers.JSONField(write_only=True, required=False) 
    quiz_questions = QuizQuestionSerializer(many=True, read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'location', 'image_url', 'created_at', 
            'author_username', 'quiz_questions',
            'locker', 
            'questions' 
        ]
        read_only_fields = ['id', 'created_at', 'author_username', 'quiz_questions']
        


    def create(self, validated_data):
        questions_data = validated_data.pop('questions', []) or []
        post = Post.objects.create(**validated_data)
        
        for q_data in questions_data:
            QuizQuestion.objects.create(
                post=post,
                question_text=q_data.get('text'),
                choices_json=q_data.get('choices'),
                correct_choice_id=q_data.get('correctChoiceId')
            ) 
        return post