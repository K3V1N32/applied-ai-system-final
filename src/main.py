"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs, UserProfile

#####################################
##        Sample Profiles          ##
#####################################

## Intense Rock ##
intense_rock = UserProfile(
    favorite_genre="rock",
    favorite_mood="intense",
    target_energy=0.9,
    target_valence=0.2,
    likes_acoustic=False,
)

## Chill Lofi ##
chill_lofi = UserProfile(
    favorite_genre="lofi",
    favorite_mood="chill",
    target_energy=0.3,
    target_valence=0.5,
    likes_acoustic=True,
)

##  Angry metal ##
angry_metal = UserProfile(
    favorite_genre="metal",
    favorite_mood="angry",
    target_energy=0.8,
    target_valence=0.1,
    likes_acoustic=False,
)

## Happy pop ##
happy_pop = UserProfile(
    favorite_genre="pop",
    favorite_mood="happy",
    target_energy=0.8,
    target_valence=0.8,
    likes_acoustic=True,
)

## Moody Synthwave ##
moody_synthwave = UserProfile(
    favorite_genre="synthwave",
    favorite_mood="moody",
    target_energy=0.6,
    target_valence=0.4,
    likes_acoustic=False,
)

#################################
##   format_recommendation     ##
#################################

def format_recommendation(recommendations: list[tuple], profile_name: str) -> str:
    result = ""
    result += f"""
    #####################################
    #   {profile_name} Recommendations  #
    #####################################
    """
    for rec in recommendations:
        song, score, explanation = rec
        result += f"\n{song['title']} - Score: {score:.2f}\n"
        result += f"Selection Reasoning:\n"
        for reason in explanation.split("; "):
            result += f"  - {reason}\n"
    return result


def main() -> None:
    songs = load_songs("../data/songs.csv")
    # Added validation that songs are loaded, along with a print statement to show the number of songs loaded.
    if not songs:
        print("Error: No songs loaded.")
        return
    print(
        """
          #####################################
          #   Music Recommender Simulation    #
          #####################################
        """
    )
    print(f"> Loaded {len(songs)} songs from the dataset.")

    ## Profile Testing ##
    
    print(format_recommendation(recommend_songs(intense_rock, songs, k=5), "Intense Rock"))
    print(format_recommendation(recommend_songs(chill_lofi, songs, k=5), "Chill Lofi"))
    print(format_recommendation(recommend_songs(angry_metal, songs, k=5), "Angry Metal"))
    print(format_recommendation(recommend_songs(happy_pop, songs, k=5), "Happy Pop"))
    print(format_recommendation(recommend_songs(moody_synthwave, songs, k=5), "Moody Synthwave"))

    print("> Music Recommender Simulation completed.")


if __name__ == "__main__":
    main()
