CREATE TABLE valkrets(
    valkrets_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE parti(
    parti_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE ledamot(
    intressent_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    valkrets_id INT NOT NULL REFERENCES valkrets(valkrets_id),
    parti_id TEXT NOT NULL REFERENCES parti(parti_id)
);

CREATE TABLE utskott(
    utskott_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE arende(
    dok_id TEXT PRIMARY KEY,
    notation TEXT NOT NULL,
    
);
