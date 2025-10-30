from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class UserPreferences(BaseModel):
    """Model for user preferences"""
    # Search preferences
    preferredLanguage: Literal['es', 'en'] = Field(default='es', alias='preferred_language')
    resultsPerPage: Literal[10, 25, 50] = Field(default=25, alias='results_per_page')
    defaultSort: Literal['relevance', 'date', 'author'] = Field(default='relevance', alias='default_sort')

    # Display preferences
    fontSize: Literal['small', 'normal', 'large'] = Field(default='normal', alias='font_size')
    theme: Literal['light', 'dark', 'system'] = Field(default='system', alias='theme')

    # Privacy settings
    saveSearchHistory: bool = Field(default=True, alias='save_search_history')
    historyRetention: Literal['1month', '3months', '6months', 'forever'] = Field(default='6months', alias='history_retention')
    anonymousStats: bool = Field(default=True, alias='anonymous_stats')

    class Config:
        populate_by_name = True  # Permite recibir ambos formatos (camelCase y snake_case)
        # Serializar usando los nombres de campo (camelCase) en lugar de los alias (snake_case)
        by_alias = False


class UserPreferencesUpdate(BaseModel):
    """Model for updating user preferences"""
    preferredLanguage: Optional[Literal['es', 'en']] = None
    resultsPerPage: Optional[Literal[10, 25, 50]] = None
    defaultSort: Optional[Literal['relevance', 'date', 'author']] = None
    fontSize: Optional[Literal['small', 'normal', 'large']] = None
    theme: Optional[Literal['light', 'dark', 'system']] = None
    saveSearchHistory: Optional[bool] = None
    historyRetention: Optional[Literal['1month', '3months', '6months', 'forever']] = None
    anonymousStats: Optional[bool] = None


class UserPreferencesInDB(UserPreferences):
    """Model for user preferences in database"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
