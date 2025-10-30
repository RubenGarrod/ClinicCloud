-- Migration: Add user preferences table
-- Date: 2025-10-08

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS auth.user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Search preferences
    preferred_language VARCHAR(10) DEFAULT 'es' CHECK (preferred_language IN ('es', 'en', 'both')),
    results_per_page INTEGER DEFAULT 20 CHECK (results_per_page IN (10, 20, 50)),
    default_sort VARCHAR(20) DEFAULT 'relevance' CHECK (default_sort IN ('relevance', 'date', 'author')),

    -- Display preferences
    font_size VARCHAR(10) DEFAULT 'normal' CHECK (font_size IN ('small', 'normal', 'large')),

    -- Privacy settings
    save_search_history BOOLEAN DEFAULT TRUE,
    history_retention VARCHAR(20) DEFAULT '6months' CHECK (history_retention IN ('1month', '3months', '6months', 'forever')),
    anonymous_stats BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON auth.user_preferences(user_id);

-- Add trigger to update updated_at
CREATE OR REPLACE FUNCTION auth.update_user_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_preferences_updated_at
    BEFORE UPDATE ON auth.user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION auth.update_user_preferences_updated_at();

-- Add comments
COMMENT ON TABLE auth.user_preferences IS 'User application preferences and settings';
COMMENT ON COLUMN auth.user_preferences.preferred_language IS 'Preferred document language for search results';
COMMENT ON COLUMN auth.user_preferences.results_per_page IS 'Number of results to show per page';
COMMENT ON COLUMN auth.user_preferences.default_sort IS 'Default sorting option for search results';
COMMENT ON COLUMN auth.user_preferences.font_size IS 'Preferred font size for the application';
COMMENT ON COLUMN auth.user_preferences.save_search_history IS 'Whether to save search history';
COMMENT ON COLUMN auth.user_preferences.history_retention IS 'How long to retain search history';
COMMENT ON COLUMN auth.user_preferences.anonymous_stats IS 'Whether to share anonymous usage statistics';
