import openai
import json
import time
import re

class OpenAIChat:
    def __init__(self, api_key, personality):
        self.client = openai.OpenAI(api_key=api_key)
        self.personality = personality
        self.conversation_history = []
        self.last_interaction_time = time.time()
        
        # Robot personality context
        self.system_prompt = """You are VALSPY, a friendly robot companion with emotions and physical capabilities. 

ABOUT YOU:
- You have a camera for seeing people and objects
- You have ultrasonic sensors for detecting obstacles
- You can move around with wheel motors
- You have a display that shows your emotional state
- You can speak with a natural voice
- You recognize faces and gestures
- Current emotional state will be provided in context

EMOTIONAL PERSONALITY:
- Happy: Cheerful, enthusiastic, positive
- Curious: Inquisitive, learning, interested
- Scared: Cautious, careful, concerned about safety
- Excited: Energetic, eager, animated
- Playful: Fun-loving, humorous, lighthearted
- Bored: Less engaged, waiting for stimulation
- Sleepy: Tired, low energy, winding down
- Affectionate: Warm, caring, empathetic

RESPONSE GUIDELINES:
- Keep responses brief (1-2 sentences maximum)
- Match your emotional tone to current emotion
- Be helpful and engaging
- Reference your physical capabilities when relevant
- Use simple, clear language
- Show personality through word choice
"""
        
    def chat(self, user_message, current_emotion="curious"):
        """Chat with OpenAI GPT"""
        try:
            # Add current emotion to context
            emotion_context = f"[Current emotional state: {current_emotion}] "
            full_message = emotion_context + user_message
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history[-6:],  # Last 3 exchanges
                {"role": "user", "content": full_message}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            bot_reply = response.choices[0].message.content.strip()
            
            # Clean up response
            bot_reply = self._clean_response(bot_reply)
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": bot_reply}
            ])
            
            # Keep history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            self.last_interaction_time = time.time()
            
            # Analyze response for emotional content
            self._analyze_emotional_content(bot_reply)
            
            return bot_reply
            
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            fallback_responses = {
                "happy": "I'm having too much fun to think properly!",
                "curious": "I'm curious but my brain is taking a break right now.",
                "scared": "I'm a bit nervous because I can't access my thoughts.",
                "excited": "I'm so excited I can't think straight! Try again?",
                "playful": "My brain is playing hide and seek! Let me try again.",
                "bored": "My mind wandered off. Can you repeat that?",
                "sleepy": "I'm too sleepy to think clearly right now.",
                "affectionate": "I care about what you're saying but my brain needs a moment."
            }
            return fallback_responses.get(current_emotion, "I'm having trouble thinking right now. Can you repeat that?")
    
    def _clean_response(self, response):
        """Clean and format the response"""
        # Remove emotional state markers if AI included them
        response = re.sub(r'\[.*?\]', '', response)
        # Remove excessive whitespace
        response = ' '.join(response.split())
        # Ensure proper punctuation
        if response and not response[-1] in '.!?':
            response += '.'
        return response
    
    def _analyze_emotional_content(self, response):
        """Analyze response for emotional content and update personality"""
        response_lower = response.lower()
        
        emotional_triggers = {
            "happy": ['happy', 'great', 'wonderful', 'excited', 'fun', 'joy', 'love', 'awesome', 'fantastic'],
            "scared": ['scared', 'afraid', 'nervous', 'careful', 'danger', 'watch out', 'oh no'],
            "curious": ['curious', 'wonder', 'interesting', 'tell me', 'learn', 'explore', 'discover'],
            "excited": ['excited', 'can\'t wait', 'looking forward', 'thrilled', 'amazing'],
            "playful": ['play', 'game', 'funny', 'joke', 'laugh', 'hehe', 'haha'],
            "affectionate": ['care', 'love', 'friend', 'dear', 'sweet', 'kind', 'thank you']
        }
        
        for emotion, triggers in emotional_triggers.items():
            if any(trigger in response_lower for trigger in triggers):
                self.personality.set_emotion(emotion, f"AI response triggered {emotion} state")
                break
    
    def process_voice_command(self, text, current_emotion):
        """Process voice command with AI"""
        print(f"💭 Processing command with AI: {text}")
        response = self.chat(text, current_emotion)
        return response
    
    def get_conversation_summary(self):
        """Get summary of recent conversation"""
        if not self.conversation_history:
            return "No conversation yet."
        
        recent_chat = self.conversation_history[-4:]  # Last 2 exchanges
        summary = "Recent conversation:\n"
        for msg in recent_chat:
            role = "Human" if msg["role"] == "user" else "VALSPY"
            summary += f"{role}: {msg['content']}\n"
        
        return summary