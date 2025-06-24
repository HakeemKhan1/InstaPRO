## Overview

InstaPRO is an application designed to provide recommendations for your next Instagram story and feed posts. By leveraging a multi-agent system and analyzing your existing content, InstaPRO helps you optimize your posting strategy to maximize engagement and growth.

## Features

-   **Multi-Agent System:** Employs three specialized AI agents to provide comprehensive content recommendations.
    -   **Story Specialist:** Focuses on analyzing story posting patterns and recommending engaging story content.
    -   **Feed Specialist:** Concentrates on feed performance, suggesting optimal feed post content and timing.
    -   **Content Coordinator:** Ensures seamless integration between story and feed strategies y.
-   **Content Analysis:** Analyzes your existing Instagram content to identify trends and opportunities.
-   **Personalized Recommendations:** Provides specific, actionable recommendations tailored to your unique content and audience.
-   **Content Gap Analysis:** Identifies content types, helping you diversify your content strategy.
-   **Posting Rhythm Analysis:** Analyzes your posting frequency and timing patterns to determine the optimal time to post for maximum engagement.

![image](https://github.com/user-attachments/assets/9dcb384e-00ee-47a9-b912-e1d9b694108c)

![image](https://github.com/user-attachments/assets/907c0882-662f-498e-9d56-e93365ceec46)

![image](https://github.com/user-attachments/assets/abf7acd5-3e45-425e-b46c-6fa0ab1f7297)

## Setup

1.  Create a virtual environment:

    ```bash
    python -m venv .venv
    ```

2.  Activate the virtual environment:

    ```bash
    .venv\Scripts\activate
    ```

3.  Install the required Python packages:

    ```bash
    pip install -r Requirements.txt
    ```

2.  Set the `OPENAI_API_KEY` environment variable:

    ```bash
    export OPENAI_API_KEY=<your_openai_api_key>
    ```

## Usage

1.  Add your existing posts to the database:

    ```bash
    python app.py add "Your post caption" "post_type" engagement "#hashtags" days_ago
    ```

    *   `post_type`: Type of post (satisfying\_video, promotion, educational, behind\_scenes).
    *   `engagement`: Total engagement (likes + comments + saves).
    *   `#hashtags`: Comma-separated hashtags.
    *   `days_ago`: How many days ago was this posted?

    Example:

    ```bash
    python app.py add "Epic storefront transformation! 3 hours of work for this amazing result" "satisfying_video" 3200 "#windowcleaning,#satisfying,#transformation,#commercial" 2
    ```

2.  Alternatively, add sample posts to test the system immediately:

    ```bash
    python app.py quick-setup
    ```

3.  Get AI recommendations for your next Instagram story and feed post:

    ```bash
    python app.py next
    ```

    You can also provide a context for the recommendations:

    ```bash
    python app.py next --context "launching new service"
    ```

## Database

The application uses ChromaDB to store the Instagram post data. The database is stored in the `./chroma_db` directory.

## Multi-Agent System

The application uses a multi-agent system with three specialized agents:

*   **Story Specialist:** Analyzes story posting patterns and recommends specific story content.
*   **Feed Specialist:** Analyzes feed posting patterns and recommends specific feed post content.
*   **Content Coordinator:** Ensures story and feed recommendations work together strategically.

## Running the App

To start the application, run the following command:

```bash
python app.py next
```

