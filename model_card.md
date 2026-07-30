# Model Card for VectorVibe

AI isn't just about what works -- it's about what's responsible. In this document I will reflect on my use of AI in this project.

## Limitations and Bias
"""What are the limitations or biases in your system?"""

## Misuse of the AI
"""Could your AI be misused, and how would you prevent that?"""

## Reliability
"""What surprised you while testing your AI's reliability?"""

## Collaboration
"""describe your collaboration with AI during this project. Identify one instance when the AI gave a helpful suggestion and one instance where its suggestion was flawed or incorrect."""

## Accountability and Responsible Disclosure
This is a list of all the prompts I made to Claude to complete this project

| Prompt |
| ------ |
| Can you review just my plan and tell me how feasible it would be to add these features for my music recommender. I have about 5-6 hours to spend and will be using your help to speed up some of the tasks. |
| I'm thinking of using this dataset from kaggle:\nhttps://www.kaggle.com/datasets/devdope/900k-spotify/data\n\nIt looks like it's about 500 thousand songs and has a lot of the same information and also includes lyrics, I was thinking of having it as a seperate required download to run the music recommender rather than uploading it to github.\n\nAs for the algorithm, I was thinking there may be a way to create a vector map from the lyric/ other data to use semantic search to get the closest songs to a user input such as \"High energy dance songs\" rather than having a user put in a bunch of target_energy or favorite genre variables, then use gemini API to feed the recommendations to gemini and prompt for specific reasons for each pick if possible" |
| I'm still new at semantic search but let me lay out how I would want the app to work, and you can tell me if it's possible.\nI want to overhaul the old algorithm, I want the app to basically just ask the user a general \"What kind of music would you like me to recommend?\" with a single input box. Then whatever needs to happen to embed the search, and compare it to the pre-embedded dataset to find close matches, and give those close matches to gemini with the prompt to recommend and give reasoning. |
| Yes, use ai-final-plan under the header ai implemenentation plan to help us figure out the steps needed to make this music recommender worthy of an AI Engineering final project |
| I've got the file downloaded and in the data/ directory, don't accidentally try to read it, as it is over 1 gigabyte and will probably overload my tokens available lol. The columns it has are:\n\nArtist(s)\nsong [title]\ntext [lyrics]\nLength\nemotion\nGenre\nAlbum\nRelease Date\nKey\nTempo\nLoudness (db)\nTime signature\nExplicit\nPopularity\nEnergy\nDanceability\nPositiveness\nSpeechiness\nLiveness\nAcousticness\nInstrumentalness\nGood for Party\nGood for Work/Study\nGood for Relaxation/Meditation\nGood for Exercise\nGood for Running\nGood for Yoga/Stretching\nGood for Driving\nGood for Social Gatherings\nGood for Morning Routine\nSimilar Artist 1\nSimilar Song 1\nSimilarity Score 1\nSimilar Artist 2\nSimilar Song 2\nSimilarity Score 2\nSimilar Artist 3\nSimilar Song 3\nSimilarity Score 3\n\n\nThe columns that I think will matter for semantic search are:\nArtist(s)\nsong\nemotion\ntext\nGenre\nEnergy\n\nDo you think thats enough to make a good semantic map? And also how are we ever going to pick which songs to pull from this dataset 😅 |
| Yes, let's start with 2,500 and I made sure to install pandas for use in data manipulation |
| Alright, lets continue to phase 3 |
| Yes, let's continue with phase 4 |
| Yes, let's go ahead with phase 5 we can start narrowing down how well the ideas work and make adjustments as we go |
| Yes, let's continue to the streamlit UI implementation as outlined. |
| I have one thing we should add before moving on, let's make sure we make note of whether gemini or the backup is giving the recommendations so the user can understand a bit better|
| I have an idea to make the UI more interactive, what if we use the deezer api to embed a preview of each song? Would that be possible with our current song data? |
| Ok the previews are excellent, thanks for helping with that! Let's move on to tests! |
| Would you say the system of semantic search -> AI refining, is a form of RAG? Could you give a summary of why it is or isn't? |
| Does our current recommender test the AI output to make sure that at least the songs that AI picks are all in the picks that we generated? |
| Perfect, that's the kind of RAG validation that will keep our AI tool from giving hallucinations, and shows that the project has guardrails against making up information! |
| Ok my plan for this is to break it up into smaller sections, I want to work on a large portion of documentation myself, so that I fully understand the inner workings and why/why nots of the project, but I still want to get your help refining and for checking my understanding, let's first focus on how the project is structured, do we need to make any changes for professional structure or does having all of the code in src make sense? let's make sure the file/program structure is set up well before we move on to making the mermaid diagram |
| Let's move to making the mermaid diagram |
| I moved the diagram to diagrams/
Could you generate a png of the diagram and store it under assets/images directory |
| Please verify requirements.txt against actual used modules before we write the setup guide |
| Would it be possible to add song cover-art from deezer API to the list of found songs? I added a default_cover.png for if there is no cover art, it would be great if it could be shown to the left of each song recommendation matching the sizing of those cards |
| I'm getting errors regarding torchvision module not found when running the streamlit app |
| Is it ok that we are getting warnings about unauthenticated requests t oHF Hub? |
| Next up, I need some help with setup, I need python setup, requirements, gemini api key, and downloading the dataset and running first time setup |
