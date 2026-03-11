# -*- coding: utf-8 -*-
import openai
import base64


class LLM:
    """
    A class to interact with the LLM API using OpenAI client.
    """
    
    def __init__(self, api_key="sk-2YyulB0ZcUW55t96dI9t-w", base_url="https://llm.505labs.ai", model="gpt-5-mini"):
        """
        Initialize the LLM client.
        
        Args:
            api_key (str): API key for authentication
            base_url (str): Base URL for the API endpoint
            model (str): Model name to use for completions
        """
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
    
    def respond(self, text, stream=False, conversation_history=None):
        """
        Respond to input text.
        
        Args:
            text (str): Input text to respond to
            stream (bool): Whether to stream the response (default: False)
            conversation_history (list): Optional list of previous messages for context
        
        Returns:
            str: The response text if stream=False
            generator: A generator yielding response chunks if stream=True
        """
        # Build messages list
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current user message
        messages.append({
            "role": "user",
            "content": text
        })
        
        # Create the completion request
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream
        )
        
        if stream:
            # Return a generator for streaming responses
            return self._stream_response(response)
        else:
            # Return the full response text
            return response.choices[0].message.content
    
    def _stream_response(self, stream):
        """
        Generator function to yield streaming response chunks.
        
        Args:
            stream: The streaming response object
        
        Yields:
            str: Response text chunks
        """
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    
    def encode_image(self, image_path):
        """
        Helper function to encode images to base64.
        
        Args:
            image_path (str): Path to the image file
        
        Returns:
            str: Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def respond_with_image(self, text, image_path, stream=False):
        """
        Respond to input text with an image context.
        
        Args:
            text (str): Input text to respond to
            image_path (str): Path to the image file
            stream (bool): Whether to stream the response (default: False)
        
        Returns:
            str: The response text if stream=False
            generator: A generator yielding response chunks if stream=True
        """
        base64_file = self.encode_image(image_path)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_file}"
                        }
                    }
                ]
            }
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream
        )
        
        if stream:
            return self._stream_response(response)
        else:
            return response.choices[0].message.content
