import os
import google.generativeai as genai
import google
import logging
import time
import os
from dotenv import load_dotenv

# load environment variables.
load_dotenv()


class AIAssistant:
  def __init__(self, api_key, system_prompt=None):
    self.api_key = api_key
    genai.configure(api_key=self.api_key)
    self.model = None
    self.history = []
    self.system_prompt = system_prompt
    # validate availability of system_prompt.
    if self.system_prompt == None:
       raise ValueError('The Class requires that you pass a System Prompt to get running.')
       

    # start the agent.
    self.start_chat()

  def start_chat(self):
    # Initialize a chat session with the desired model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-8b-exp-0827", 
        generation_config={
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
            "response_mime_type": "application/json",
        },
        system_instruction=f'{self.system_prompt}',
    )
    self.model = model
    self.chat_session = model.start_chat(history=self.history)
    if self.model != None:
       print('Loaded Successfully')
    else:
       raise ValueError('Something wrong was provided, kindly check')

  def _interact(self, msg):
      try:
          response = self.chat_session.send_message(msg)
          return response.text
      except google.generativeai.types.generation_types.StopCandidateException as e:
          # Log the error details
          logging.error(f"StopCandidateException occurred: {e}")
          # Return a user-friendly message
          time.sleep(10)
          print('Waiting for Ten Seconds to retry after error.')
          return self._interact(f'you previous response retutrned an safety issue error, align your response and assist the user again, Error Encountered\n{e}')