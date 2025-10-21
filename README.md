# String Analyzer Service

Backend Wizards Stage 1 Task - A RESTful API that analyzes strings and stores computed properties.

## Features

- Analyze strings for length, palindrome, unique characters, word count, character frequency, and SHA-256 hash
- Filter strings by various properties
- Natural language query support
- RESTful API endpoints

## API Endpoints

- **POST /strings** - Analyze a new string
- **GET /strings/{value}** - Get specific string analysis  
- **GET /strings** - Get all strings (with optional filters)
- **DELETE /strings/{value}** - Delete a string
- **GET /strings/filter-by-natural-language** - Natural language search

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
2. **Setup database**
3. **Install dependencies**
4. **Run migrations**
5. **Run the development server**
6. **Test your API**

## Dependencies
Django==4.2.7
djangorestframework==3.14.0

## Error Handling
400 Bad Request - Invalid request body or query parameters
404 Not Found - String does not exist in the system
409 Conflict - String already exists
422 Unprocessable Entity - Invalid data type for value

## Deployment

Deployed on Railway: `https://web-production-632a4.up.railway.app`
