-- Скрипт заполнения таблицы game_llm_models данными о LLM-моделях
-- Согласно разделу "5. LLM Manager - модуль управления LLM-моделями" в docs/specsBackend/02_requirements.md
-- Убедитесь, что расширение uuid-ossp включено:
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

INSERT INTO game_llm_models (id, model_key, name, description, model_type, manufacturer, release_date, enabled)
VALUES
 (gen_random_uuid(), 'gpt-4-turbo', 'GPT-4 Turbo', 'GPT-4 Turbo модель от OpenAI', 'non-reasoning', 'OpenAI', '2023-11-06', true),
 (gen_random_uuid(), 'gpt-4o-mini', 'GPT-4o Mini', 'GPT-4o Mini модель от OpenAI', 'non-reasoning', 'OpenAI', '2024-07-18', true),
 (gen_random_uuid(), 'o4-mini', 'O4 Mini', 'O4 Mini рассуждающая модель от OpenAI', 'reasoning', 'OpenAI', '2024-11-01', true),
 (gen_random_uuid(), 'gpt-4.1-mini', 'GPT-4.1 Mini', 'GPT-4.1 Mini модель от OpenAI', 'non-reasoning', 'OpenAI', '2024-04-14', true),
 (gen_random_uuid(), 'gpt-4.1', 'GPT-4.1', 'GPT-4.1 модель от OpenAI', 'non-reasoning', 'OpenAI', '2024-04-14', true),
 (gen_random_uuid(), 'claude-opus-4-6', 'Claude Opus 4.6', 'Claude Opus 4.6 модель от Anthropic', 'non-reasoning', 'Anthropic', '2024-08-15', true),
 (gen_random_uuid(), 'claude-sonnet-4-6', 'Claude Sonnet 4.6', 'Claude Sonnet 4.6 модель от Anthropic', 'non-reasoning', 'Anthropic', '2024-08-15', true),
 (gen_random_uuid(), 'claude-haiku-4-5', 'Claude Haiku 4.5', 'Claude Haiku 4.5 модель от Anthropic', 'non-reasoning', 'Anthropic', '2024-08-15', true),
 (gen_random_uuid(), 'gemini-2.5-flash', 'Gemini 2.5 Flash', 'Gemini 2.5 Flash модель от Google', 'non-reasoning', 'Google', '2024-10-10', true),
 (gen_random_uuid(), 'gemini-2.5-pro', 'Gemini 2.5 Pro', 'Gemini 2.5 Pro модель от Google', 'non-reasoning', 'Google', '2024-10-10', true)
ON CONFLICT (model_key) DO NOTHING;
