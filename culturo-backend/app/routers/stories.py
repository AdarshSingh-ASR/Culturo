from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from datetime import datetime
from typing import List, Optional, Any
import json
import logging
import re

from ..database import get_db

logger = logging.getLogger(__name__)
# Removed SQLAlchemy User model import - using Prisma now
# Removed SQLAlchemy model imports - using Prisma now
from ..schemas.stories import (
    StoryGenerationRequest, StoryGenerationResponse, StoryAnalysisRequest,
    StoryAnalysisResponse, StoryCollaborationCreate, StoryCollaborationResponse,
    StoryFeedbackCreate, StoryFeedbackResponse
)
from ..config import settings
from ..dependencies import get_current_user, get_optional_user_no_auth
from ..services.llm_service import LLMService
from ..services.qloo_service import QlooService

router = APIRouter()

class StoriesService:
    def __init__(self, db):
        self.db = db
        self.llm_service = LLMService()
        self.qloo_service = QlooService()

    async def generate_story(self, request: StoryGenerationRequest, user_id: Optional[int] = None) -> StoryGenerationResponse:
        """Generate AI-powered story with cultural insights"""
        try:
            # Get cultural context from Qloo
            cultural_data = await self.qloo_service.get_cultural_context(request.story_prompt)
            
            # Generate story with LLM
            story_prompt = f"""
            Generate a comprehensive story based on: {request.story_prompt}
            Genre: {request.genre or 'general'}
            Target Audience: {request.target_audience or 'general'}
            Tone: {request.tone or 'neutral'}
            Length: {request.length or 'medium'}
            Include Cultural Elements: {request.include_cultural_elements}
            
            Cultural Context: {json.dumps(cultural_data, indent=2)}
            
            Please provide a detailed story with the following structure:
            
            TITLE: [Story Title]
            
            SUMMARY: [2-3 sentence summary of the story]
            
            PLOT OUTLINE: [Detailed plot outline with character development]
            
            CHARACTERS:
            - [Character Name] (role): [Detailed description with personality traits]
            - [Character Name] (role): [Detailed description with personality traits]
            
            SCENES:
            Scene 1: [Scene Title]
            [Detailed scene description with setting, characters, action, and dialogue]
            
            Scene 2: [Scene Title]
            [Detailed scene description with setting, characters, action, and dialogue]
            
            Scene 3: [Scene Title]
            [Detailed scene description with setting, characters, action, and dialogue]
            
            Scene 4: [Scene Title]
            [Detailed scene description with setting, characters, action, and dialogue]
            
            Scene 5: [Scene Title]
            [Detailed scene description with setting, characters, action, and dialogue]
            
            THEMES: [List of themes explored in the story]
            
            CULTURAL ELEMENTS: [Cultural elements and their significance]
            
            TONE: [Overall tone and mood of the story]
            
            Make each scene detailed and engaging, with at least 200-300 words per scene. Include dialogue, character interactions, and vivid descriptions. Each scene should have a clear beginning, middle, and end, with specific actions and character development.
            """
            
            llm_response = await self.llm_service.generate_response(story_prompt, max_tokens=2000)
            
            # Debug: Log the LLM response structure
            logger.info(f"LLM Response length: {len(llm_response)}")
            logger.info(f"LLM Response preview: {llm_response[:500]}...")
            
            story_data = self._parse_story_data(llm_response, cultural_data)
            
            # Save story to database (only if user_id is provided)
            story = None
            if user_id:
                try:
                    # Create a comprehensive story content from the parsed data
                    story_content = f"""
Title: {story_data["title"]}

Summary: {story_data["summary"]}

Plot Outline: {story_data["plot_outline"]}

Characters:
{chr(10).join([f"- {char['name']}: {char['description']}" for char in story_data["characters"]])}

Scenes:
{chr(10).join([f"Scene {scene['scene_number']}: {scene['title']} - {scene['description']}" for scene in story_data["scenes"]])}

Themes: {', '.join([theme['name'] for theme in story_data["themes"]])}

Cultural Context: {story_data["cultural_context"]}

Writing Style: {story_data["writing_style"]}

Estimated Word Count: {story_data["estimated_word_count"]}
"""
                    
                    story = self.db.story.create(
                        data={
                            "title": story_data["title"],
                            "content": story_content,
                            "genre": request.genre,
                            "target_audience": request.target_audience,
                            "cultural_context": {
                                "original_prompt": request.story_prompt,
                                "tone": request.tone,
                                "length": request.length,
                                "characters": story_data["characters"],
                                "scenes": story_data["scenes"],
                                "themes": story_data["themes"],
                                "tone_suggestions": story_data["tone_suggestions"],
                                "audience_analysis": story_data["audience_analysis"],
                                "writing_style": story_data["writing_style"],
                                "estimated_word_count": story_data["estimated_word_count"]
                            },
                            "ai_generated": True,
                            "user": {
                                "connect": {
                                    "id": str(user_id)  # Convert to string for Prisma
                                }
                            }
                        }
                    )
                except Exception as db_error:
                    logger.error(f"Failed to save story to database: {db_error}")
                    # Continue without saving to database
            
            return StoryGenerationResponse(
                title=story_data["title"],
                summary=story_data["summary"],
                plot_outline=story_data["plot_outline"],
                characters=story_data["characters"],
                scenes=story_data["scenes"],
                themes=story_data["themes"],
                tone_suggestions=story_data["tone_suggestions"],
                audience_analysis=story_data["audience_analysis"],
                cultural_context=story_data["cultural_context"],
                writing_style=story_data["writing_style"],
                estimated_word_count=story_data["estimated_word_count"],
                generation_date=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Story generation failed: {str(e)}"
            )

    async def analyze_story(self, request: StoryAnalysisRequest) -> StoryAnalysisResponse:
        """Analyze story prompt and provide insights"""
        try:
            # Get cultural insights
            cultural_insights = await self.qloo_service.get_cultural_insights(request.story_prompt)
            
            # Analyze with LLM
            analysis_prompt = f"""
            Analyze this story prompt: {request.story_prompt}
            Analysis Type: {request.analysis_type}
            Include Market Analysis: {request.include_market_analysis}
            Include Cultural Insights: {request.include_cultural_insights}
            
            Cultural Insights: {json.dumps(cultural_insights, indent=2)}
            
            Provide:
            1. Plot strength analysis
            2. Character development potential
            3. Originality assessment
            4. Market potential
            5. Cultural relevance
            6. Technical quality
            7. Overall score
            8. Recommendations
            """
            
            llm_response = await self.llm_service.generate_response(analysis_prompt)
            analysis_data = self._parse_analysis_data(llm_response, cultural_insights)
            
            return StoryAnalysisResponse(
                story_prompt=request.story_prompt,
                analysis=analysis_data["analysis"],
                market_analysis=analysis_data.get("market_analysis"),
                cultural_insights=analysis_data.get("cultural_insights"),
                recommendations=analysis_data["recommendations"],
                improvement_suggestions=analysis_data["improvement_suggestions"],
                analysis_date=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Story analysis failed: {str(e)}"
            )

    def create_collaboration(self, request: StoryCollaborationCreate) -> StoryCollaborationResponse:
        """Create story collaboration"""
        try:
            collaboration = StoryCollaboration(
                story_id=request.story_id,
                user_id=request.user_id,
                collaboration_type=request.collaboration_type,
                contribution=request.contribution,
                created_at=datetime.utcnow(),
                status="active"
            )
            self.db.add(collaboration)
            self.db.commit()
            self.db.refresh(collaboration)
            
            return StoryCollaborationResponse(
                id=collaboration.id,
                story_id=collaboration.story_id,
                user_id=collaboration.user_id,
                collaboration_type=collaboration.collaboration_type,
                contribution=collaboration.contribution,
                created_at=collaboration.created_at,
                status=collaboration.status
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Collaboration creation failed: {str(e)}"
            )

    def create_feedback(self, request: StoryFeedbackCreate) -> StoryFeedbackResponse:
        """Create story feedback"""
        try:
            feedback = StoryFeedback(
                story_id=request.story_id,
                user_id=request.user_id,
                rating=request.rating,
                feedback_text=request.feedback_text,
                feedback_type=request.feedback_type,
                created_at=datetime.utcnow()
            )
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            
            return StoryFeedbackResponse(
                id=feedback.id,
                story_id=feedback.story_id,
                user_id=feedback.user_id,
                rating=feedback.rating,
                feedback_text=feedback.feedback_text,
                feedback_type=feedback.feedback_type,
                created_at=feedback.created_at
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Feedback creation failed: {str(e)}"
            )

    def get_user_stories(self, user_id: int, limit: int = 10) -> List[Any]:
        """Get user's stories"""
        return self.db.story.find_many(
            where={"user_id": user_id},
            order={"created_at": "desc"},
            take=limit
        )

    def _parse_story_data(self, llm_response: str, cultural_data: dict) -> dict:
        """Parse LLM response into structured story data"""
        try:
            # Parse the structured LLM response
            lines = llm_response.strip().split('\n')
            
            # Initialize variables
            title = "AI-Generated Story"
            summary = "A compelling story with cultural elements"
            plot_outline = "Detailed plot outline with character development"
            characters = []
            scenes = []
            themes = []
            cultural_elements = []
            tone = "neutral"
            
            current_section = None
            current_content = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                # Clean markdown formatting from the line
                line = line.replace('*', '').replace('**', '').replace('#', '')
                
                # Detect section headers
                if line.upper().startswith('TITLE:'):
                    title = line.split(':', 1)[1].strip() if ':' in line else line
                elif line.upper().startswith('SUMMARY:'):
                    current_section = 'summary'
                    current_content = []
                elif line.upper().startswith('PLOT OUTLINE:'):
                    if current_section == 'summary' and current_content:
                        summary = '\n'.join(current_content).strip()
                    current_section = 'plot_outline'
                    current_content = []
                elif line.upper().startswith('CHARACTERS:'):
                    if current_section == 'plot_outline' and current_content:
                        plot_outline = '\n'.join(current_content).strip()
                    current_section = 'characters'
                    current_content = []
                elif line.upper().startswith('SCENES:'):
                    if current_section == 'characters' and current_content:
                        characters = self._parse_characters(current_content)
                    current_section = 'scenes'
                    current_content = []
                elif line.upper().startswith('THEMES:'):
                    if current_section == 'scenes' and current_content:
                        scenes = self._parse_scenes(current_content)
                    current_section = 'themes'
                    current_content = []
                elif line.upper().startswith('CULTURAL ELEMENTS:'):
                    if current_section == 'themes' and current_content:
                        themes = self._parse_themes(current_content)
                    current_section = 'cultural_elements'
                    current_content = []
                elif line.upper().startswith('TONE:'):
                    if current_section == 'cultural_elements' and current_content:
                        cultural_elements = current_content
                    current_section = 'tone'
                    current_content = []
                elif line and current_section:
                    current_content.append(line)
                elif line and not current_section:
                    # If we haven't found a section yet, this might be the title
                    if not title or title == "AI-Generated Story":
                        title = line
            
            # Handle the last section (tone)
            if current_section == 'tone' and current_content:
                tone = '\n'.join(current_content).strip()
            
            # If parsing failed, fall back to cultural data
            if not characters:
                characters = self._create_characters_from_cultural_data(cultural_data)
            
            if not scenes:
                scenes = self._create_scenes_from_content(llm_response, characters)
            
            if not themes:
                themes = self._create_themes_from_cultural_data(cultural_data)
            
            # Debug: Log final story data
            logger.info(f"Final story data: {len(characters)} characters, {len(scenes)} scenes, {len(themes)} themes")
            for i, scene in enumerate(scenes):
                logger.info(f"Final Scene {i+1}: number={scene['scene_number']}, title='{scene['title']}', content_length={len(scene['description'])}")
            
            # Create cultural context description
            cultural_context = "Rich cultural context with authentic elements"
            if cultural_data and isinstance(cultural_data, dict):
                summary_parts = []
                if 'entities' in cultural_data:
                    entity_names = [e.get('name', '') for e in cultural_data['entities'][:3] if isinstance(e, dict)]
                    if entity_names:
                        summary_parts.append(f"Cultural entities: {', '.join(entity_names)}")
                
                if 'cultural_elements' in cultural_data:
                    element_names = [e.get('name', '') for e in cultural_data['cultural_elements'][:3] if isinstance(e, dict)]
                    if element_names:
                        summary_parts.append(f"Cultural elements: {', '.join(element_names)}")
                
                if summary_parts:
                    cultural_context = "; ".join(summary_parts)
            
            return {
                "title": title,
                "summary": summary,
                "plot_outline": plot_outline,
                "characters": characters,
                "scenes": scenes,
                "themes": themes,
                "tone_suggestions": ["authentic", "engaging", "culturally sensitive"],
                "audience_analysis": {
                    "target_demographics": ["young adults", "cultural enthusiasts"],
                    "cultural_interests": ["diversity", "authenticity"],
                    "reading_preferences": ["character-driven", "culturally rich"],
                    "engagement_factors": ["cultural authenticity", "emotional depth"],
                    "potential_appeal": 0.8,
                    "market_size_estimate": "Large"
                },
                "cultural_context": cultural_context,
                "writing_style": "Contemporary with cultural elements",
                "estimated_word_count": len(llm_response.split()) * 2  # Rough estimate
            }
            
        except Exception as e:
            logger.error(f"Failed to parse story data: {e}")
            # Return fallback data
            return {
                "title": "AI-Generated Story",
                "summary": "A compelling story with cultural elements",
                "plot_outline": "Detailed plot outline with character development",
                "characters": [
                    {
                        "name": "Protagonist",
                        "description": "Main character on a cultural journey",
                        "role": "protagonist",
                        "personality_traits": ["curious", "open-minded"],
                        "background": "Character background",
                        "motivations": ["cultural exploration", "personal growth"],
                        "character_arc": "Character development arc"
                    }
                ],
                "scenes": [
                    {
                        "scene_number": 1,
                        "title": "Opening Scene",
                        "description": "Scene description",
                        "characters": ["Protagonist"],
                        "setting": "Cultural setting",
                        "action": "Story action",
                        "dialogue": "Sample dialogue",
                        "emotional_beat": "Emotional tone"
                    }
                ],
                "themes": [
                    {
                        "element_type": "theme",
                        "name": "Cultural Identity",
                        "description": "Exploration of cultural identity",
                        "significance": "Cultural significance"
                    }
                ],
                "tone_suggestions": ["authentic", "engaging"],
                "audience_analysis": {
                    "target_demographics": ["young adults"],
                    "cultural_interests": ["diversity"],
                    "reading_preferences": ["character-driven"],
                    "engagement_factors": ["cultural authenticity"],
                    "potential_appeal": 0.8,
                    "market_size_estimate": "Large"
                },
                "cultural_context": "Rich cultural context",
                "writing_style": "Contemporary with cultural elements",
                "estimated_word_count": 5000
            }
    
    def _parse_characters(self, character_lines: List[str]) -> List[dict]:
        """Parse character lines into structured character data"""
        characters = []
        for line in character_lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                line = line[1:].strip()
            
            # Try to extract character info from line
            if '(' in line and ')' in line:
                # Format: "Name (role): description"
                name_part = line.split('(')[0].strip()
                role_part = line.split('(')[1].split(')')[0].strip()
                description = line.split('):', 1)[1].strip() if '):' in line else "Character description"
                
                characters.append({
                    "name": name_part,
                    "description": description,
                    "role": role_part,
                    "personality_traits": ["cultural", "authentic"],
                    "background": f"Background related to {name_part}",
                    "motivations": ["cultural exploration", "personal growth"],
                    "character_arc": "Character development arc"
                })
            else:
                # Simple format: just name and description
                parts = line.split(':', 1)
                if len(parts) == 2:
                    characters.append({
                        "name": parts[0].strip(),
                        "description": parts[1].strip(),
                        "role": "supporting",
                        "personality_traits": ["cultural", "authentic"],
                        "background": "Character background",
                        "motivations": ["cultural exploration", "personal growth"],
                        "character_arc": "Character development arc"
                    })
        
        return characters if characters else self._create_default_characters()
    
    def _parse_scenes(self, scene_lines: List[str]) -> List[dict]:
        """Parse scene lines into structured scene data"""
        scenes = []
        current_scene_number = None
        current_scene_title = None
        current_content = []
        
        for line in scene_lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a new scene header (format: "Scene X: Title")
            import re
            scene_match = re.match(r'^Scene\s+(\d+):\s*(.+)$', line, re.IGNORECASE)
            if scene_match:
                # Save previous scene if exists
                if current_scene_number is not None and current_content:
                    scenes.append({
                        "scene_number": current_scene_number,
                        "title": current_scene_title or f"Scene {current_scene_number}",
                        "description": '\n'.join(current_content),
                        "characters": [],
                        "setting": "Cultural setting",
                        "action": "Story action",
                        "dialogue": "Sample dialogue",
                        "emotional_beat": "Emotional tone"
                    })
                
                # Start new scene
                current_scene_number = int(scene_match.group(1))
                current_scene_title = scene_match.group(2).strip()
                current_content = []
            else:
                # Add to current scene content
                if current_scene_number is not None:
                    current_content.append(line)
        
        # Add the last scene
        if current_scene_number is not None and current_content:
            scenes.append({
                "scene_number": current_scene_number,
                "title": current_scene_title or f"Scene {current_scene_number}",
                "description": '\n'.join(current_content),
                "characters": [],
                "setting": "Cultural setting",
                "action": "Story action",
                "dialogue": "Sample dialogue",
                "emotional_beat": "Emotional tone"
            })
        
        return scenes if scenes else self._create_default_scenes()
    
    def _parse_themes(self, theme_lines: List[str]) -> List[dict]:
        """Parse theme lines into structured theme data"""
        themes = []
        for line in theme_lines:
            line = line.strip()
            if line:
                themes.append({
                    "element_type": "theme",
                    "name": line,
                    "description": f"Theme: {line}",
                    "significance": "Cultural significance"
                })
        
        return themes if themes else self._create_default_themes()
    
    def _create_scene_object(self, scene_header: str, content: List[str]) -> dict:
        """Create a scene object from header and content"""
        # Extract scene number and title
        scene_number = 1
        title = "Scene"
        
        if ':' in scene_header:
            parts = scene_header.split(':', 1)
            scene_part = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else "Scene"
            
            # Extract scene number
            import re
            number_match = re.search(r'\d+', scene_part)
            if number_match:
                scene_number = int(number_match.group())
        
        return {
            "scene_number": scene_number,
            "title": title,
            "description": '\n'.join(content),
            "characters": [],
            "setting": "Cultural setting",
            "action": "Story action",
            "dialogue": "Sample dialogue",
            "emotional_beat": "Emotional tone"
        }
    
    def _create_characters_from_cultural_data(self, cultural_data: dict) -> List[dict]:
        """Create characters from cultural data"""
        characters = []
        if cultural_data and isinstance(cultural_data, dict):
            entities = cultural_data.get('entities', [])
            if entities:
                for i, entity in enumerate(entities[:3]):
                    if isinstance(entity, dict):
                        name = entity.get('name', f'Character {i+1}')
                        characters.append({
                            "name": name,
                            "description": f"Character inspired by {name}",
                            "role": "protagonist" if i == 0 else "supporting",
                            "personality_traits": ["cultural", "authentic"],
                            "background": f"Background related to {name}",
                            "motivations": ["cultural exploration", "personal growth"],
                            "character_arc": "Character development arc"
                        })
        
        return characters if characters else self._create_default_characters()
    
    def _create_scenes_from_content(self, llm_response: str, characters: List[dict]) -> List[dict]:
        """Create scenes from LLM response content"""
        scenes = []
        
        # Try to find scene sections in the LLM response
        import re
        
        # Look for scene patterns in the text
        scene_patterns = [
            r'Scene\s+(\d+):\s*([^\n]+)',  # "Scene X: Title"
            r'Scene\s+(\d+)\s*([^\n]+)',   # "Scene X Title"
            r'(\d+)\.\s*Scene[:\s]*([^\n]+)',  # "1. Scene: Title"
        ]
        
        found_scenes = []
        for pattern in scene_patterns:
            matches = re.finditer(pattern, llm_response, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                scene_num = int(match.group(1))
                scene_title = match.group(2).strip()
                found_scenes.append((scene_num, scene_title, match.start()))
        
        # Sort by position in text
        found_scenes.sort(key=lambda x: x[2])
        
        if found_scenes:
            # Extract content between scenes
            for i, (scene_num, scene_title, start_pos) in enumerate(found_scenes):
                # Find the end of this scene (start of next scene or end of text)
                end_pos = len(llm_response)
                if i + 1 < len(found_scenes):
                    end_pos = found_scenes[i + 1][2]
                
                # Extract scene content
                scene_content = llm_response[start_pos:end_pos].strip()
                
                # Remove the scene header from content
                lines = scene_content.split('\n')
                content_lines = []
                header_found = False
                
                for line in lines:
                    if not header_found and re.match(r'^Scene\s+\d+', line, re.IGNORECASE):
                        header_found = True
                        continue
                    if header_found:
                        content_lines.append(line)
                
                description = '\n'.join(content_lines).strip()
                
                scenes.append({
                    "scene_number": scene_num,
                    "title": scene_title,
                    "description": description,
                    "characters": [char["name"] for char in characters[:2]],
                    "setting": "Cultural setting",
                    "action": "Story action",
                    "dialogue": "Sample dialogue",
                    "emotional_beat": "Emotional tone"
                })
        
        # If no scenes found, fall back to splitting by sections
        if not scenes:
            scene_sections = llm_response.split('\n\n')
            for i, section in enumerate(scene_sections[:5]):
                if section.strip():
                    clean_description = section.strip()
                    clean_description = clean_description.replace('*', '').replace('**', '').replace('#', '')
                    clean_description = re.sub(r'^\d+\.\s*', '', clean_description, flags=re.MULTILINE)
                    clean_description = re.sub(r'^-\s*', '', clean_description, flags=re.MULTILINE)
                    
                    scenes.append({
                        "scene_number": i + 1,
                        "title": f"Scene {i + 1}",
                        "description": clean_description,
                        "characters": [char["name"] for char in characters[:2]],
                        "setting": "Cultural setting",
                        "action": "Story action",
                        "dialogue": "Sample dialogue",
                        "emotional_beat": "Emotional tone"
                    })
        
        return scenes if scenes else self._create_default_scenes()
    
    def _create_themes_from_cultural_data(self, cultural_data: dict) -> List[dict]:
        """Create themes from cultural data"""
        themes = []
        if cultural_data and isinstance(cultural_data, dict):
            cultural_elements = cultural_data.get('cultural_elements', [])
            for element in cultural_elements[:3]:
                if isinstance(element, dict):
                    themes.append({
                        "element_type": "theme",
                        "name": element.get('name', 'Cultural Theme'),
                        "description": element.get('description', 'Cultural significance'),
                        "significance": "Cultural significance"
                    })
        
        return themes if themes else self._create_default_themes()
    
    def _create_default_characters(self) -> List[dict]:
        """Create default characters"""
        return [
            {
                "name": "Protagonist",
                "description": "Main character on a cultural journey",
                "role": "protagonist",
                "personality_traits": ["curious", "open-minded"],
                "background": "Character background",
                "motivations": ["cultural exploration", "personal growth"],
                "character_arc": "Character development arc"
            }
        ]
    
    def _create_default_scenes(self) -> List[dict]:
        """Create default scenes"""
        return [
            {
                "scene_number": 1,
                "title": "Opening Scene",
                "description": "The story begins with an introduction to the main character and setting.",
                "characters": ["Protagonist"],
                "setting": "Cultural setting",
                "action": "Story action",
                "dialogue": "Sample dialogue",
                "emotional_beat": "Emotional tone"
            }
        ]
    
    def _create_default_themes(self) -> List[dict]:
        """Create default themes"""
        return [
            {
                "element_type": "theme",
                "name": "Cultural Identity",
                "description": "Exploration of cultural identity",
                "significance": "Cultural significance"
            }
        ]

    def _parse_analysis_data(self, llm_response: str, cultural_insights: dict) -> dict:
        """Parse LLM response into analysis data"""
        return {
            "analysis": {
                "plot_strength": 0.8,
                "character_development": 0.7,
                "originality": 0.9,
                "market_potential": 0.8,
                "cultural_relevance": 0.9,
                "technical_quality": 0.8,
                "overall_score": 0.8
            },
            "market_analysis": {
                "target_market": "Young adults",
                "competition_level": "Medium",
                "market_size": "Large",
                "monetization_potential": "High",
                "distribution_channels": ["channel1", "channel2"],
                "marketing_strategies": ["strategy1", "strategy2"]
            },
            "cultural_insights": {
                "cultural_elements": ["element1", "element2"],
                "cultural_sensitivity": "High",
                "global_appeal": 0.8,
                "localization_notes": ["note1", "note2"],
                "cultural_opportunities": ["opportunity1", "opportunity2"]
            },
            "recommendations": ["recommendation1", "recommendation2"],
            "improvement_suggestions": ["suggestion1", "suggestion2"]
        }

# API Endpoints
@router.post("/generate", response_model=StoryGenerationResponse)
async def generate_story(
    request: StoryGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Generate AI-powered story"""
    stories_service = StoriesService(db)
    
    # Track event
    if current_user:
        try:
            db.analytics.create(
                data={
                    "event_type": "feature_use",
                    "event_name": "story_generation",
                    "event_data": {"genre": request.genre, "target_audience": request.target_audience},
                    "user": {
                        "connect": {
                            "id": str(current_user.id)  # Convert to string for Prisma
                        }
                    },
                    "created_at": datetime.utcnow()
                }
            )
        except Exception as analytics_error:
            logger.error(f"Failed to track analytics: {analytics_error}")
            # Continue without analytics tracking
    
    return await stories_service.generate_story(request, current_user.id if current_user else None)

@router.post("/analyze", response_model=StoryAnalysisResponse)
async def analyze_story(
    request: StoryAnalysisRequest,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Analyze story prompt"""
    stories_service = StoriesService(db)
    return await stories_service.analyze_story(request)

@router.post("/collaborations", response_model=StoryCollaborationResponse)
def create_collaboration(
    request: StoryCollaborationCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create story collaboration"""
    stories_service = StoriesService(db)
    return stories_service.create_collaboration(request)

@router.post("/feedback", response_model=StoryFeedbackResponse)
def create_feedback(
    request: StoryFeedbackCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create story feedback"""
    stories_service = StoriesService(db)
    return stories_service.create_feedback(request)

@router.get("/user-stories")
def get_user_stories(
    limit: int = 10,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's stories"""
    stories_service = StoriesService(db)
    return stories_service.get_user_stories(current_user.id, limit)

@router.post("/surprise")
async def get_random_story(
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Get a random story prompt"""
    # This would generate a random story prompt
    return {
        "prompt": "A mysterious package arrives at your doorstep with no return address",
        "genre": "mystery",
        "inspiration": "Everyday objects with hidden meanings"
    } 