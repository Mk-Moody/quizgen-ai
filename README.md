# QuizGen AI

A simple web application for generating quizzes from uploaded documents using the OpenAI API.

## Features

- Upload PDF, audio, or video files.
- File size limits based on plan:
  - Free: 1 MB
  - Pro: 5 MB
  - Premium: 10 MB
- Free plan generates 15 questions.
- Pro and Premium plans generate questions based on file length and allow selecting difficulty level.
- Each question has four answer options.
- Results page shows your score and highlights the correct answers after the quiz.

## Running

1. Install dependencies:
   ```bash
   pip install flask openai
   ```
2. Set `OPENAI_API_KEY` environment variable with your OpenAI API key.
3. Run the application:
   ```bash
   python -m app.app
   ```
4. Open your browser at `http://localhost:5000`.

This is a basic demonstration and can be extended with authentication, better parsing of uploaded files, and improved styling.
