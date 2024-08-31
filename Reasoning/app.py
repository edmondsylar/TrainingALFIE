from Taskmanager import TaskManager  # Adjust the import based on your file structure
from Taskmanager import Task
import datetime
import os
from dotenv import load_dotenv
from rich.console import Console
from rich import inspect

con = Console()

load_dotenv()

import google.generativeai as genai

import logging
import google.generativeai as genai
from google.generativeai.types import content_types
from collections.abc import Iterable


task_manager = TaskManager(db_path='test_tasks.db')  # Use a separate test database

def create_task(task_description, due_date=None, user_id=None):
    """Create a new task."""
    try:
        task_id = task_manager.create_task(task_description, due_date, user_id)
        return f"Created Task ID: {task_id}"
    except Exception as e:
        return f"Error creating task: {str(e)}"

def get_task(task_id):
    """Retrieve a task by its ID."""
    try:
        task = task_manager.get_task(task_id)
        if task:
            return f"Retrieved Task: {task.task_description}, Status: {task.status}"
        else:
            return f"Task with ID {task_id} not found."
    except Exception as e:
        return f"Error retrieving task: {str(e)}"

def update_task(task_id, **kwargs):
    """Update an existing task."""
    try:
        success = task_manager.update_task(task_id, **kwargs)
        if success:
            updated_task = task_manager.get_task(task_id)
            return f"Updated Task: {updated_task.task_description}, Status: {updated_task.status}"
        else:
            return f"Task with ID {task_id} not found for update."
    except Exception as e:
        return f"Error updating task: {str(e)}"

def delete_task(task_id):
    """Delete a task by its ID."""
    try:
        success = task_manager.delete_task(task_id)
        if success:
            return f"Deleted Task with ID: {task_id}"
        else:
            return f"Task with ID {task_id} not found for deletion."
    except Exception as e:
        return f"Error deleting task: {str(e)}"
    

def get_top_pending_tasks(limit=5):
    """Retrieve the top N pending tasks."""
    try:
        pending_tasks = task_manager.session.query(Task).filter_by(status='Pending').limit(limit).all()
        if pending_tasks:
            return [f"ID: {t.task_id}, Description: {t.task_description}, Status: {t.status}" for t in pending_tasks]
        else:
            return "No pending tasks found."
    except Exception as e:
        return f"Error retrieving pending tasks: {str(e)}"

def get_top_completed_tasks(limit=5):
    """Retrieve the top N completed tasks."""
    try:
        completed_tasks = task_manager.session.query(Task).filter_by(status='Completed').limit(limit).all()
        if completed_tasks:
            return [f"ID: {t.task_id}, Description: {t.task_description}, Status: {t.status}" for t in completed_tasks]
        else:
            pass    
        return f"No completed tasks found."
    except Exception as e:
        return f"Error retrieving completed tasks: {str(e)}"

def get_top_tasks_by_status(status, limit=5):
    """Retrieve the top N tasks by status."""
    try:
        tasks = task_manager.session.query(Task).filter_by(status=status).limit(limit).all()
        return tasks
    except Exception as e:
        print(f"Error retrieving tasks with status '{status}': {str(e)}")
        return []

def TasksStats():
    """Generate a report of the top 5 tasks from each category."""
    report = ["### Systems Tasks Operations Report. ###"]

    # Get top 5 completed tasks
    completed_tasks = get_top_tasks_by_status('Completed')
    report.append("Top 5 Completed Tasks:")
    for task in completed_tasks:
        report.append(f"ID: {task.task_id}, Description: {task.task_description}, Status: {task.status}")
    
    # Get top 5 pending tasks
    pending_tasks = get_top_tasks_by_status('Pending')
    report.append("\nTop 5 Pending Tasks:")
    for task in pending_tasks:
        report.append(f"ID: {task.task_id}, Description: {task.task_description}, Status: {task.status}")

    # Get top 5 dropped tasks (assuming 'Dropped' is a valid status)
    dropped_tasks = get_top_tasks_by_status('Dropped')
    report.append("\nTop 5 Dropped Tasks:")
    for task in dropped_tasks:
        report.append(f"ID: {task.task_id}, Description: {task.task_description}, Status: {task.status}")

    # Get all tasks
    all_tasks = task_manager.get_all_tasks()
    report.append("\nAll Tasks:")
    for task in all_tasks[:5]:  # Limit to top 5 for display
        report.append(f"ID: {task.task_id}, Description: {task.task_description}, Status: {task.status}")

    return "\n".join(report)


genai.configure(api_key="AIzaSyD9dVpTJRwaITfJ-nD4AKvA4BByIK44evs")


def enable_lights():
    """Turn on the lighting system."""
    return "LIGHTBOT: Lights enabled."


def set_light_color(rgb_hex: str):
    """Set the light color. Lights must be enabled for this to work."""
    return f"LIGHTBOT: Lights set to {rgb_hex}."


def stop_lights():
    """Stop flashing lights."""
    return "LIGHTBOT: Lights turned off."


def tool_config_from_mode(mode: str, fns: Iterable[str] = ()):
    """Create a tool config with the specified function calling mode."""
    return content_types.to_tool_config(
        {"function_calling_config": {"mode": mode, "allowed_function_names": fns}}
    )


tool_config = tool_config_from_mode("auto")


light_controls = [enable_lights, set_light_color, stop_lights]
instruction = """
You are alfie, an home assistant bot with the capacity to assit in the house and still developing.

for those requiring no tool call, your response must be formated as the JSON style below:
```json
{
    "Screetext":"response from your operations and any details the user might want to see. return None for nothing",
    "speech":"Narator/Guide style speech that helps the use understand what the screenText is about or a speech like response to the request"
}

"""


# check if the result is a function call
def has_function_call(response):
    if not response or not response._result or not response._result.candidates:
        return False

    for candidate in response._result.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                
                # parts_list = [str(part) for part in candidate.content.parts]
                # if any("text" in str(part) for part in parts_list):
                #     return False
                # if any("function_call" in str(part) for part in parts_list):
                #     # print('function_call returned')
                #     return True, part

                parts_list = [str(part) for part in candidate.content.parts]
                if any("text" in str(part) for part in parts_list):
                    return False
                if any("function_call" in str(part) for part in parts_list):
                    return True # Still return True to indicate a function call

    return False


def extract_function_call(response):
    if not has_function_call(response):
        return None
    
    for candidate in response._result.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "function_call"):
                    return part
    return None


def executor(function_call_part):
    """
    Executes the function specified in the function_call_part and returns the response.

    Args:
        function_call_part: The part object containing the function call information.

    Returns:
        The response from the executed function.
    """
    function_name = function_call_part.function_call.name
    # Use the items() method to get the fields
    function_args = dict(function_call_part.function_call.args.items()) 

    # Find the corresponding function in your light_controls list
    for function in light_controls:
        if function.__name__ == function_name:
            # Extract argument values
            kwargs = {}
            for arg_name, arg_value in function_args.items():
                if isinstance(arg_value, str):  # Check if it's a string
                    kwargs[arg_name] = arg_value
                elif arg_value.WhichOneof("kind") == "string_value":
                    kwargs[arg_name] = arg_value.string_value
                # Add other type handling if needed (e.g., for integers)

            # Execute the function
            try:
                response = function(**kwargs)
                return response
            except Exception as e:
                return f"Error executing function: {e}"  # Handle errors gracefully
    
    return f"Function '{function_name}' not found." # Function not found 


# Set up logging
logging.basicConfig(filename='alfie_interactions.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AlfieLightingAssistant:
    def __init__(self, tools, tool_config):
        """
        Initializes the Alfie assistant with the specified tools and tool config.

        Args:
            tools: A list of tool functions.
            tool_config: The tool configuration for Gemini.
        """
        self.tools = tools
        self.tool_config = tool_config
        self.model = genai.GenerativeModel(
            "models/gemini-1.5-flash", 
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
                # "response_mime_type": "application/json",
            },
            tools=tools, tool_config=tool_config, 
            system_instruction=instruction
        )
        self.chat = self.model.start_chat(history=[])
        self.task_manager = TaskManager(db_path='test_tasks.db')

    def _interact(self, user_message):
        """
        Handles user interaction, executes tool calls, and returns a response.

        Args:
            user_message: The user's input message.

        Returns:
            A string response, without tool call information.
        """

        response = self.chat.send_message(user_message)
        logger.info(f"Assistant Response: {response}")

        if has_function_call(response):
            function_call_part = extract_function_call(response)
            if function_call_part:
                tool_response = self.executor(function_call_part)
                logger.info(f"Tool Response: {tool_response}")

                # Add feedback loop, if needed
                response_feedback = self.chat.send_message(
                    f"response from Function call::\n{tool_response}\n\nNotify the user or make another tool call if completion needed"
                )
                logger.info(f"Feedback Response: {response_feedback}")

                if has_function_call(response_feedback):
                    # loop to complete the tool calls.
                    return self._interact(f"response from Function call::\n{tool_response}\n\n Notify the user or make another tool call if completion needed")
                else:
                    return response_feedback

        else:
            logger.info("No tool call in the response.")
            return response  # Return the non-tool-call response


    def executor(self, function_call_part):
        """
        Executes the function specified in the function_call_part and returns the response.

        Args:
            function_call_part: The part object containing the function call information.

        Returns:
            The response from the executed function.
        """
        function_name = function_call_part.function_call.name
        function_args = dict(function_call_part.function_call.args.items())

        for function in self.tools:
            if function.__name__ == function_name:
                kwargs = {}
                for arg_name, arg_value in function_args.items():
                    if isinstance(arg_value, str):
                        kwargs[arg_name] = arg_value
                    elif arg_value.WhichOneof("kind") == "string_value":
                        kwargs[arg_name] = arg_value.string_value

                try:
                    response = function(**kwargs)
                    print(f'Executed function {function_name}\n\n')
                    return response
                except Exception as e:
                    return f"Error executing function: {e}"

        return f"Function '{function_name}' not found."


# ... (Initialize your tools and tool config) ...
alfie = AlfieLightingAssistant(light_controls, tool_config)

while True:
    user_message = input("Enter your command (or type 'exit' to terminate): \n")
    if user_message.lower() == 'exit':
        break
    response = alfie._interact(user_message)  # Use the _interact method
    print(response.text)
