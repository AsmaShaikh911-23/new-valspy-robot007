import pygame
import os
import time

class DisplayManager:
    def __init__(self):
        self.screen = None
        self.current_emotion = "neutral"
        self.emotion_faces = {
            "happy": "😊",
            "curious": "🤔", 
            "bored": "😐",
            "scared": "😨",
            "excited": "😃",
            "neutral": "😐"
        }
        
    def start(self):
        """Initialize display"""
        try:
            os.putenv('SDL_FBDEV', '/dev/fb1')
            pygame.init()
            self.screen = pygame.display.set_mode((320, 240))
            pygame.display.set_caption("VALSPY Robot")
            pygame.mouse.set_visible(False)
            
            print("✅ Display initialized")
            
        except Exception as e:
            print(f"❌ Display error: {e}")
    
    def show_emotion(self, emotion):
        """Display emotion as face"""
        if emotion.name != self.current_emotion:
            self.current_emotion = emotion.name
            self._draw_face(emotion.name)
    
    def _draw_face(self, emotion):
        """Draw face expression on display"""
        if not self.screen:
            return
            
        try:
            self.screen.fill((0, 0, 0))  # Clear screen
            
            # Draw face circle
            pygame.draw.circle(self.screen, (255, 255, 255), (160, 120), 80)
            
            # Draw eyes based on emotion
            if emotion == "happy":
                # Happy eyes
                pygame.draw.circle(self.screen, (0, 0, 0), (130, 100), 10)
                pygame.draw.circle(self.screen, (0, 0, 0), (190, 100), 10)
                # Smile
                pygame.draw.arc(self.screen, (0, 0, 0), (140, 130, 80, 40), 0, 3.14, 3)
                
            elif emotion == "scared":
                # Wide eyes
                pygame.draw.circle(self.screen, (0, 0, 0), (130, 100), 15)
                pygame.draw.circle(self.screen, (0, 0, 0), (190, 100), 15)
                # Small mouth
                pygame.draw.circle(self.screen, (0, 0, 0), (160, 150), 5)
                
            elif emotion == "curious":
                # Curious eyes (squinted)
                pygame.draw.ellipse(self.screen, (0, 0, 0), (120, 95, 20, 10))
                pygame.draw.ellipse(self.screen, (0, 0, 0), (180, 95, 20, 10))
                # Thinking mouth
                pygame.draw.line(self.screen, (0, 0, 0), (140, 150), (180, 150), 2)
                
            else:  # neutral
                pygame.draw.circle(self.screen, (0, 0, 0), (130, 100), 8)
                pygame.draw.circle(self.screen, (0, 0, 0), (190, 100), 8)
                pygame.draw.line(self.screen, (0, 0, 0), (140, 150), (180, 150), 3)
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Display drawing error: {e}")
    
    def update_frame(self, frame):
        """Update display with camera frame"""
        # Optional: Show camera feed on display
        pass
    
    def stop(self):
        """Cleanup display"""
        if self.screen:
            pygame.quit()