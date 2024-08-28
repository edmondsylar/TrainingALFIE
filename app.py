from Agents.AgentOnline.app import AIAssistant
import os
from dotenv import load_dotenv
import time
from rich.console import Console
import logging
from logging.handlers import RotatingFileHandler
import json


con = Console()

# load the environment variables.
load_dotenv()


# Configure logging
log_file = 'interaction_log.log'
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)  # 1MB per file, keep 5 backup files
log_handler.setFormatter(log_formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(log_handler)

# Create a custom logger for rich console output
class RichConsoleHandler(logging.Handler):
    def __init__(self, console):
        super().__init__()
        self.console = console

    def emit(self, record):
        log_entry = self.format(record)
        self.console.log(log_entry)

rich_handler = RichConsoleHandler(con)
rich_handler.setFormatter(log_formatter)
root_logger.addHandler(rich_handler)



def read_prompt_file(filename):
    prompts_folder = 'prompts'
    file_path = os.path.join(prompts_folder, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{filename}' does not exist in the '{prompts_folder}' folder.")
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    return content


class InteractionManager:
    def __init__(self, teacher_agent, learner_agent, defaultWait=5, iterations=10):
        self.teacher = teacher_agent
        self.learner = learner_agent
        self.defaultWait = defaultWait # seconds of waiting to save tockens
        self.iterations = iterations 

        self.conversationStarter = f'''
        Date: 8:28/2024
        Time: 12:25 pm
        Location: Office 
        Country: Uganda.

        Environmental Context:
        You are in a training Run and you capcbilities should be utilized to the max, keep very keen focus on background processes so that you can build a good case for autonomy.
        Engage with (Ivy) you teacher and find out how to better your capabilites, Use don't have access to actual tools but use dummy examples just to show the right outputs.

        You have upto {self.iterations} iterations for this engagement, ensure to utilize them efficiently.
        Ensure to keep the conversation flowing until all iterations are done.
        '''

    def run_interaction_loop(self):
        # Initialize the first prompt for the learner
        current_message = self.conversationStarter

        for i in range(self.iterations):
            # Teacher (Ivy) gives a prompt to the learner (Alfie)
            learner_response = self.learner._interact(current_message)
            con.log(f"Learner: {learner_response}")
            logging.info(f"Learner: {json.dumps(learner_response)}")
            time.sleep(self.defaultWait)

            # Learner's response is then passed to the teacher
            teacher_feedback = self.teacher._interact(learner_response)
            con.log(f"Teacher: {teacher_feedback}")
            logging.info(f"Teacher: {json.dumps(teacher_feedback)}")

            # Update the current message to continue the conversation loop
            current_message = teacher_feedback + f"\n {self.iterations} Remaining.\n Ensure to keep the conversation flowing until all iterations are done."

            # Optionally, add a pause for realism
            time.sleep(self.defaultWait)

            # Handle any additional logic, such as storing conversation history


learner_agent_prompt = read_prompt_file('learner_structured_prompt_one.txt')
teacher_agent_prompt = read_prompt_file('teacher_structured_prompt_one.txt')

# Instantiate AIAssistant objects
teacher_agent = AIAssistant(api_key=os.getenv('GEMINI_API_KEY'), system_prompt=teacher_agent_prompt)
learner_agent = AIAssistant(api_key=os.getenv('GEMINI_API_KEY'), system_prompt=learner_agent_prompt)

# Create an InteractionManager instance
interaction_manager = InteractionManager(teacher_agent, learner_agent, 5, 15)

# Run the interaction loop
interaction_manager.run_interaction_loop()
