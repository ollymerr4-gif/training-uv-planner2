# Training UV Planner

Automatically checks the UV index during your scheduled training sessions (pulled from Google Calendar) and adds a UV summary event to your calendar, so you know how much sun exposure to expect.

## How it works

1. Connects to your Google Calendar and finds today's training sessions (events containing specific keywords, e.g. "ball", "om").
2. For each session, fetches the UV index at the start and end time using the WeatherAPI forecast.
3. Classifies UV risk (Low, Moderate, High, Very High, Extreme).
4. Creates a new calendar event summarising the UV levels for that session.

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/ollymerr4-gif/training-uv-planner2.git
cd training-uv-planner2
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install requests python-dotenv pytz google-auth google-auth-oauthlib google-api-python-client
```

### 4. Set up environment variables
Create a `.env` file in the project root:
