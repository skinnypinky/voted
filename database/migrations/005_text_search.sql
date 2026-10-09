ALTER TABLE arende 
ADD COLUMN search_vector tsvector 
GENERATED ALWAYS AS (
    setweight(to_tsvector('swedish', coalesce(notisrubrik, '')), 'A') ||
    setweight(to_tsvector('swedish', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('swedish', coalesce(summary, '')), 'B') 
) STORED;

CREATE INDEX arende_search_vector_idx ON arende USING GIN (search_vector);