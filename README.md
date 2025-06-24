# Instagram Post Recommender

This application uses a multi-agent system to analyze your existing Instagram content and recommend specific next story and feed posts.

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

## Uploading to GitHub

1.  Create a new repository on GitHub.
2.  Initialize a Git repository in your project directory:

    ```bash
    git init
    ```

3.  Add the project files to the repository:

    ```bash
    git add .
    ```

4.  Commit the changes:

    ```bash
    git commit -m "Initial commit"
    ```

5.  Add the remote repository:

    ```bash
    git remote add origin <your_repository_url>
    ```

6.  Push the changes to GitHub:

    ```bash
    git push -u origin main
    ```

## Contributing

Feel free to contribute to this project by submitting pull requests.
