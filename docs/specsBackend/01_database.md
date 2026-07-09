# Database Structure for Tic-Tac-Toe AI

## IDM

### Users Table
```sql
CREATE TABLE idm_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_idm_user_email ON idm_user(email);
CREATE INDEX idx_idm_user_username ON idm_user(username);
```

### User Settings

Настройки пользователя вынесены в отдельную таблицу. Предполагается, что они будут меняться гораздо чаще, чем основные данные.
Также это сделано для того, чтобы не объединять данные, которые влияют на ИБ, с данными которые отвечают за предпочтения пользователя.

```sql
CREATE TABLE idm_user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES idm_user(id),
    theme_preference VARCHAR(10) DEFAULT 'dark',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_idm_user_settings_user_id ON idm_user_settings(user_id);
```


### User sessions
```sql
CREATE TABLE idm_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES idm_user(id),
    guest_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address varchar(255) NULL,
);

CREATE INDEX idx_idm_session_user_id ON idm_session(user_id);
```

### User Events
```sql
CREATE TABLE idm_event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	session_id UUID REFERENCES idm_session(id),
    user_id UUID REFERENCES idm_user(id),
	event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	event_type NOT NULL varchar(255) NULL,
    error varchar(255) NULL,
	details_json JSONB
);

CREATE INDEX idx_idm_even_event_time ON idm_event(event_time);
CREATE INDEX idx_idm_even_session_id ON idm_event(session_id);
CREATE INDEX idx_idm_even_user_id ON idm_event(user_id);
```


## Games

### LLM Models Table
```sql
CREATE TABLE game_llm_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_key VARCHAR(50) UNIQUE NOT NULL, -- 'gpt-4o', 'claude-3.5-sonnet', etc.
    name VARCHAR(100) NOT NULL,
    description TEXT,
    model_type VARCHAR(20) NOT NULL CHECK (model_type IN ('reasoning', 'non-reasoning')),
    manufacturer VARCHAR(100),
    release_date DATE,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Games Table
```sql
CREATE TABLE game (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    board_size INTEGER NOT NULL CHECK (board_size IN (3, 5, 10, 30)),
    win_sequence INTEGER NOT NULL CHECK (win_sequence IN (3, 4, 5)),
    game_mode VARCHAR(20) NOT NULL CHECK (game_mode IN ('computer', 'friend')),
    game_status VARCHAR(20) NOT NULL CHECK (game_status IN ('waiting', 'in_progress', 'finished')),
    model_id UUID REFERENCES game_llm_models(id) ON DELETE SET NULL,
    difficulty VARCHAR(20)
        CHECK (
            (game_mode = 'computer' AND difficulty IN ('easy', 'medium', 'hard')) OR 
            (game_mode = 'friend' AND difficulty IS NULL)
        ),
    winner VARCHAR(5) CHECK (winner IN ('X', 'O', 'draw')),    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP
);
```

### Game Players Table

В данной таблице хранятся данные об игроках:
- first_player - пользователь, который создает игру;
- second_player - пользователь, который подключается к игре по ссылке.

При этом возможны различные комбинации:
- Оба пользователя зарегистрированы;
- Оба пользователя не зарегистрированы;
- Первый игрок зарегистрирован, второй нет;
- Первый игрок не зарегистрирован, второй зарегистрирован.

Если игрок зарегистрирован, то user_id - NOT NULL, а guest_name - NULL.
Если игрок не зарегистрирован, то user_id - NULL, а guest_name - NOT NULL.

При этом ссылка на сессию (session_id) присутствует всегда.

```sql
CREATE TABLE game_player (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES game(id),
    user_id UUID NULL REFERENCES idm_user(id),
    guest_name VARCHAR(100),
    session_id UUID NOT NULL REFERENCES idm_session(id),
    player_type VARCHAR(20) CHECK (player_type IN ('first_player', 'second_player')),
    player_sign VARCHAR(1) NOT NULL CHECK (player_sign IN ('X', 'O')),
    player_name NOT NULL VARCHAR(100)
);

CREATE INDEX idx_game_player_game_id ON game_player(game_id);
CREATE INDEX idx_game_player_user_id ON game_player(user_id);
CREATE UNIQUE INDEX idx_game_player_game_sign ON game_player(game_id, player_sign);
```

### Game board state
```sql
CREATE TABLE game_board (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID UNIQUE NOT NULL REFERENCES game(id),
    board JSONB NOT NULL, -- 2D array: [["X"|"O"|null]]
    move_count INTEGER DEFAULT 0,
    current_turn VARCHAR(1) CHECK (current_turn IN ('X', 'O')),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_game_board_game_id ON game_board(game_id);
```

### Game Moves Table
```sql
CREATE TABLE game_moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES game(id),
    player_id UUID NOT NULL REFERENCES game_player(id),
    row_position INTEGER NOT NULL,
    col_position INTEGER NOT NULL,
    move_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (game_id, move_number)
);

CREATE INDEX idx_game_moves_game_id ON game_moves(game_id);
```

### Game Winning Cells Table
```sql
CREATE TABLE game_winning_cells (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES game(id),
    row_position INTEGER NOT NULL,
    col_position INTEGER NOT NULL
);

CREATE INDEX idx_game_winning_cells_game_id ON game_winning_cells(game_id);
```


## Key Design Decisions

1. **UUID for Primary Keys**: All tables use UUID for distributed systems compatibility and security.

2. **JSONB for Board State**: The game board is stored as JSONB for flexibility and fast updates.

3. **Session ID as Unique Identifier**: Each game has a unique session_id for WebSocket connections.

4. **Audit Logging**: Complete tracking of user actions for security and debugging.

5. **Foreign Key Relationships**: Proper relationships for data integrity.

6. **Indexing Strategy**: Optimized indexes for common queries and filters.

## Migration Notes

1. Enable UUID extension: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`
2. Create tables in order of dependencies (users first, then games, etc.)
3. Add foreign key constraints after creating all tables
4. Set up regular backups
