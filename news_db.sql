CREATE SCHEMA test
  AUTHORIZATION postgres;

GRANT ALL ON SCHEMA test TO postgres;



CREATE TABLE test.news_rss
(
  id serial NOT NULL,
  guid text,
  title text,
  link text,
  description text,
  pub_date text,
  type text,
  is_localized boolean,
  debug_output text,
  phrases text,
  CONSTRAINT news_rss_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE test.news_rss
  OWNER TO postgres;

  
  

CREATE TABLE test.news_locations
(
  id serial NOT NULL,
  rss_id integer,
  guid text,
  lat real,
  lon real,
  pub_date timestamp without time zone,
  type text,
  user_flags integer,
  url text,
  title text,
  description text,
  phrases text,
  class integer,
  photo text,
  cluster_id integer,
  CONSTRAINT news_locations_pkey PRIMARY KEY (id),
  CONSTRAINT news_locations_rss_id_fkey FOREIGN KEY (rss_id)
      REFERENCES test.news_rss (id) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE test.news_locations
  OWNER TO postgres;

CREATE INDEX idx_news_locations_rss_id
  ON test.news_locations
  USING btree
  (rss_id);
