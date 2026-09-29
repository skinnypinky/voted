CREATE TABLE valkrets(
    valkrets_id INT PRIMARY KEY,
    valkrets_name TEXT UNIQUE NOT NULL
);

CREATE TABLE parti(
    parti_id TEXT PRIMARY KEY,
    parti_name TEXT
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
    utskott_name TEXT
);

CREATE TABLE arende(
    hangar_id TEXT PRIMARY KEY,
    notation TEXT NOT NULL,
    riksmote TEXT NOT NULL,
    title TEXT NOT NULL,
    utskott_id TEXT NOT NULL REFERENCES utskott(utskott_id),
    UNIQUE (notation, riksmote)
);

CREATE TABLE votering(
    votering_id TEXT PRIMARY KEY,
    hangar_id TEXT NOT NULL REFERENCES arende(hangar_id),
    point INT,
    title TEXT NOT NULL,
    description TEXT,
    votering_type TEXT,
    votering_date DATE NOT NULL
);

CREATE TABLE rost (
    votering_id TEXT NOT NULL REFERENCES votering(votering_id),
    intressent_id TEXT NOT NULL REFERENCES ledamot(intressent_id),
    rost TEXT NOT NULL CHECK (rost IN ('Ja', 'Nej', 'Avstår', 'Frånvarande')),
    parti_id TEXT REFERENCES parti(parti_id),
    valkrets_id INT REFERENCES valkrets(valkrets_id),
    PRIMARY KEY (votering_id, intressent_id)
);


