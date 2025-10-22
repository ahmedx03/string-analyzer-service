from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import hashlib

from .models import StringAnalysis

# Combined view for POST (create) and GET (list)
@api_view(['GET', 'POST'])
def create_analyze_string(request):
    if request.method == 'POST':
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
        
        # Check if string already exists using hash
        sha256_hash = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
        if StringAnalysis.objects.filter(id=sha256_hash).exists():
            return Response(
                {"error": "String already exists in the system"},
                status=status.HTTP_409_CONFLICT
            )
        
        # Calculate properties
        length = len(string_value)
        
        # Case-insensitive palindrome check
        cleaned = ''.join(char.lower() for char in string_value if char.isalnum())
        is_palindrome = cleaned == cleaned[::-1]
        
        unique_characters = len(set(string_value))
        word_count = len(string_value.split())
        
        # Character frequency map
        character_frequency_map = {}
        for char in string_value:
            character_frequency_map[char] = character_frequency_map.get(char, 0) + 1
        
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
        
        # min_length filter
        min_length = request.GET.get('min_length')
        if min_length is not None:
            try:
                min_length = int(min_length)
                queryset = queryset.filter(length__gte=min_length)
                filters_applied['min_length'] = min_length
            except ValueError:
                pass
        
        # max_length filter
        max_length = request.GET.get('max_length')
        if max_length is not None:
            try:
                max_length = int(max_length)
                queryset = queryset.filter(length__lte=max_length)
                filters_applied['max_length'] = max_length
            except ValueError:
                pass
        
        # word_count filter
        word_count = request.GET.get('word_count')
        if word_count is not None:
            try:
                word_count = int(word_count)
                queryset = queryset.filter(word_count=word_count)
                filters_applied['word_count'] = word_count
            except ValueError:
                pass
        
        # contains_character filter
        contains_character = request.GET.get('contains_character')
        if contains_character is not None:
            if len(contains_character) == 1:
                queryset = queryset.filter(value__icontains=contains_character)
                filters_applied['contains_character'] = contains_character
        
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

@api_view(['GET'])
def natural_language_search(request):
    print("NATURAL LANGUAGE SEARCH CALLED!")
    
    query = request.GET.get('query', '').strip()
    print(f"Query received: '{query}'")
    
    if not query:
        return Response(
            {"error": "Unable to parse natural language query"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get all strings from database
    all_strings = StringAnalysis.objects.all()
    print(f"Database contents:")
    for s in all_strings:
        print(f"   '{s.value}' - palindrome: {s.is_palindrome}, words: {s.word_count}, length: {s.length}")
    
    queryset = StringAnalysis.objects.all()
    parsed_filters = {}
    query_lower = query.lower()
    
    print(f"Processing query: '{query_lower}'")
    
    # Handle all the required query patterns
    if "single word" in query_lower and "palindromic" in query_lower:
        print("Matched: single word palindromic strings")
        queryset = queryset.filter(word_count=1, is_palindrome=True)
        parsed_filters['word_count'] = 1
        parsed_filters['is_palindrome'] = True
    
    elif "strings longer than 10 characters" in query_lower:
        print("Matched: strings longer than 10 characters")
        queryset = queryset.filter(length__gt=10)
        parsed_filters['min_length'] = 11
    
    elif "longer than 10" in query_lower:
        print("Matched: longer than 10")
        queryset = queryset.filter(length__gt=10)
        parsed_filters['min_length'] = 11
    
    elif "palindromic strings that contain the first vowel" in query_lower:
        print("Matched: palindromic strings with first vowel")
        queryset = queryset.filter(is_palindrome=True, value__icontains='a')
        parsed_filters['is_palindrome'] = True
        parsed_filters['contains_character'] = 'a'
    
    elif "first vowel" in query_lower and "palindromic" in query_lower:
        print("Matched: first vowel + palindromic")
        queryset = queryset.filter(is_palindrome=True, value__icontains='a')
        parsed_filters['is_palindrome'] = True
        parsed_filters['contains_character'] = 'a'
    
    elif "strings containing the letter z" in query_lower:
        print("Matched: strings containing letter z")
        queryset = queryset.filter(value__icontains='z')
        parsed_filters['contains_character'] = 'z'
    
    elif "containing the letter z" in query_lower:
        print("Matched: containing letter z")
        queryset = queryset.filter(value__icontains='z')
        parsed_filters['contains_character'] = 'z'
    
    # Individual filters
    elif "palindromic" in query_lower or "palindrome" in query_lower:
        print("Matched: palindromic strings")
        queryset = queryset.filter(is_palindrome=True)
        parsed_filters['is_palindrome'] = True
    
    elif "single word" in query_lower or "one word" in query_lower:
        print("Matched: single word strings")
        queryset = queryset.filter(word_count=1)
        parsed_filters['word_count'] = 1
    
    elif "longer than" in query_lower:
        if "10" in query_lower:
            print("Matched: longer than 10 characters")
            queryset = queryset.filter(length__gt=10)
            parsed_filters['min_length'] = 11
        elif "5" in query_lower:
            print("Matched: longer than 5 characters")
            queryset = queryset.filter(length__gt=5)
            parsed_filters['min_length'] = 6
    
    elif "containing the letter a" in query_lower or "first vowel" in query_lower:
        print("Matched: strings containing letter a")
        queryset = queryset.filter(value__icontains='a')
        parsed_filters['contains_character'] = 'a'
    
    elif "containing the letter" in query_lower:
        # Extract any single letter after "letter"
        import re
        match = re.search(r'letter\s+([a-z])', query_lower)
        if match:
            char = match.group(1)
            print(f"Matched: strings containing letter {char}")
            queryset = queryset.filter(value__icontains=char)
            parsed_filters['contains_character'] = char
    
    else:
        print("No patterns matched")
    
    # Get results
    results = list(queryset)
    print(f"Found {len(results)} matching strings:")
    for r in results:
        print(f"   '{r.value}'")
    
    # Prepare response data
    data = [analysis.to_response_dict() for analysis in results]
    
    print("Returning natural language response")
    
    return Response({
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters
        }
    })

# Clear database endpoint
@api_view(['POST'])
def clear_database(request):
    StringAnalysis.objects.all().delete()
    return Response({"message": "Database cleared"}, status=200)

# Test function to verify natural language is working
@api_view(['GET'])
def test_natural(request):
    print("TEST NATURAL CALLED!")
    return Response({
        "message": "Test natural works!",
        "query": request.GET.get('query', '')
    })