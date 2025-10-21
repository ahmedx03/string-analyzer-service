from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import hashlib
import re

from .models import StringAnalysis

# Combined view for POST (create) and GET (list)
@api_view(['GET', 'POST'])
def create_analyze_string(request):
    if request.method == 'POST':
        # Handle POST - Create new string analysis
        if 'value' not in request.data:
            return Response(
                {"error": "Invalid request body or missing 'value' field"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        string_value = request.data['value']
        
        if not isinstance(string_value, str):
            return Response(
                {"error": "Invalid data type for 'value' (must be string)"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        string_value = string_value.strip()
        if not string_value:
            return Response(
                {"error": "Invalid request body or missing 'value' field"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if string already exists
        if StringAnalysis.objects.filter(value=string_value).exists():
            return Response(
                {"error": "String already exists in the system"},
                status=status.HTTP_409_CONFLICT
            )
        
        # Calculate properties
        length = len(string_value)
        
        # Case-insensitive palindrome check (ignore non-alphanumeric)
        cleaned = ''.join(char.lower() for char in string_value if char.isalnum())
        is_palindrome = cleaned == cleaned[::-1]
        
        unique_characters = len(set(string_value))
        word_count = len(string_value.split())
        
        # Character frequency map
        character_frequency_map = {}
        for char in string_value:
            character_frequency_map[char] = character_frequency_map.get(char, 0) + 1
        
        # SHA-256 hash
        sha256_hash = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
        
        # Create and save analysis
        analysis = StringAnalysis(
            id=sha256_hash,
            value=string_value,
            length=length,
            is_palindrome=is_palindrome,
            unique_characters=unique_characters,
            word_count=word_count,
            character_frequency=character_frequency_map
        )
        analysis.save()
        
        return Response(analysis.to_response_dict(), status=status.HTTP_201_CREATED)
    
    elif request.method == 'GET':
        # Handle GET - Get all strings with filtering
        queryset = StringAnalysis.objects.all()
        filters_applied = {}
        
        # is_palindrome filter
        is_palindrome = request.GET.get('is_palindrome')
        if is_palindrome is not None:
            if is_palindrome.lower() in ['true', '1']:
                queryset = queryset.filter(is_palindrome=True)
                filters_applied['is_palindrome'] = True
            elif is_palindrome.lower() in ['false', '0']:
                queryset = queryset.filter(is_palindrome=False)
                filters_applied['is_palindrome'] = False
            else:
                return Response(
                    {"error": "Invalid query parameter values or types"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # min_length filter
        min_length = request.GET.get('min_length')
        if min_length is not None:
            try:
                min_length = int(min_length)
                queryset = queryset.filter(length__gte=min_length)
                filters_applied['min_length'] = min_length
            except ValueError:
                return Response(
                    {"error": "Invalid query parameter values or types"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # max_length filter
        max_length = request.GET.get('max_length')
        if max_length is not None:
            try:
                max_length = int(max_length)
                queryset = queryset.filter(length__lte=max_length)
                filters_applied['max_length'] = max_length
            except ValueError:
                return Response(
                    {"error": "Invalid query parameter values or types"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # word_count filter
        word_count = request.GET.get('word_count')
        if word_count is not None:
            try:
                word_count = int(word_count)
                queryset = queryset.filter(word_count=word_count)
                filters_applied['word_count'] = word_count
            except ValueError:
                return Response(
                    {"error": "Invalid query parameter values or types"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # contains_character filter
        contains_character = request.GET.get('contains_character')
        if contains_character is not None:
            if len(contains_character) == 1:
                queryset = queryset.filter(value__icontains=contains_character)
                filters_applied['contains_character'] = contains_character
            else:
                return Response(
                    {"error": "Invalid query parameter values or types"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        data = [analysis.to_response_dict() for analysis in queryset]
        
        return Response({
            "data": data,
            "count": len(data),
            "filters_applied": filters_applied
        })

# Combined view for GET and DELETE on specific strings
@api_view(['GET', 'DELETE'])
def string_detail(request, string_value):
    analysis = get_object_or_404(StringAnalysis, value=string_value)
    
    if request.method == 'GET':
        return Response(analysis.to_response_dict())
    
    elif request.method == 'DELETE':
        analysis.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Natural Language Filtering
@api_view(['GET'])
def filter_by_natural_language(request):
    query = request.GET.get('query', '').strip()
    
    if not query:
        return Response(
            {"error": "Unable to parse natural language query"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    queryset = StringAnalysis.objects.all()
    parsed_filters = {}
    
    try:
        query_lower = query.lower()
        
        # Parse natural language query
        # "all single word palindromic strings"
        if 'single word' in query_lower or 'one word' in query_lower:
            parsed_filters['word_count'] = 1
            queryset = queryset.filter(word_count=1)
        
        # "palindromic strings" or "palindromic"
        if 'palindromic' in query_lower or 'palindrome' in query_lower:
            parsed_filters['is_palindrome'] = True
            queryset = queryset.filter(is_palindrome=True)
        
        # "longer than X characters" or "more than X characters"
        longer_match = re.search(r'longer than (\d+)|more than (\d+)', query_lower)
        if longer_match:
            min_len = int(longer_match.group(1) or longer_match.group(2))
            parsed_filters['min_length'] = min_len + 1
            queryset = queryset.filter(length__gt=min_len)
        
        # "strings containing the letter X" or "containing X"
        contains_match = re.search(r'containing (?:the letter )?([a-zA-Z])|contains ([a-zA-Z])', query_lower)
        if contains_match:
            char = (contains_match.group(1) or contains_match.group(2)).lower()
            parsed_filters['contains_character'] = char
            queryset = queryset.filter(value__icontains=char)
        
        # "first vowel" heuristic
        if 'first vowel' in query_lower:
            parsed_filters['contains_character'] = 'a'
            queryset = queryset.filter(value__icontains='a')
        
        data = [analysis.to_response_dict() for analysis in queryset]
        
        return Response({
            "data": data,
            "count": len(data),
            "interpreted_query": {
                "original": query,
                "parsed_filters": parsed_filters
            }
        })
        
    except Exception:
        return Response(
            {"error": "Unable to parse natural language query"},
            status=status.HTTP_400_BAD_REQUEST
        )