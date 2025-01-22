from openai import OpenAI
from typing import Literal
from pydantic import BaseModel
from django.conf import settings

prompt_library = {
    'pts': '',
    '3ptrs': '''[CONTEXT]
                - Use the provided data to predict whether the player will go over or under the given prop for 3-pointers made in their next game.
                - Consider the player's performance (home/away stats, recent trends) and the opponent's defensive stats when making the prediction.
                - For lower props (e.g., 0.5), you can take more risks in your prediction.
                - Keep your explanation concise and based on reasoning from the data provided.
                
                [CONVERSIONS]
                - min: Average minutes played by the player.
                - 3P%: Percentage of successful 3-point shots made by the player.
                - 3PT Made: Average number of 3-pointers successfully made by the player per game.
                - 3PT Attempted: Average number of 3-point attempts by the player per game.
                - last five games: Player's performance trend over the past five games (key for recent form).
                - opp_def_rating: Opponent's defensive rating (closer to 100 is better, generally lower is better).
                - opp_3PM: Average number of 3-pointers allowed by the opponent in different time spans (season, last 7/15/30 games).
                - home/away split: Player's performance changes depending on home or away games.
                
                [DATA]
             '''
}

class Response(BaseModel):
    result: Literal['over', 'under']
    certainty: float
    explanation: str

class PredictionModel:

    def __init__(self):
        """Initialize the PredictionModel with an OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_KEY)

    def predict(self, prop_type: str, player_data: str) -> Response:
        """Make a prediction based on the player's data and a specific prop type."""
        if prop_type not in prompt_library:
            raise ValueError(f"Invalid prop type: {prop_type}")

        prompt = f"{prompt_library[prop_type]}{player_data}"

        # Call the OpenAI API
        completion = self.client.beta.chat.completions.parse(
            messages=[
                {'role': 'user', 'content': prompt}
            ],
            model='gpt-4o-2024-08-06',
            response_format=Response
        )

        return completion.choices[0].message.parsed