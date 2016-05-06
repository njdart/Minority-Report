CREATE TABLE IF NOT EXISTS session (
  id                 STRING PRIMARY KEY,
  topLeftX           STRING NOT NULL,
  topLeftY           STRING NOT NULL,
  topRightX          STRING NOT NULL,
  topRightY          STRING NOT NULL,
  bottomRightX       STRING NOT NULL,
  bottomRightY       STRING NOT NULL,
  bottomLeftX        STRING NOT NULL,
  bottomLeftY        STRING NOT NULL
);

CREATE TABLE IF NOT EXISTS images (
  id                 STRING PRIMARY KEY,
  timestamp          STRING NOT NULL
);

CREATE TABLE IF NOT EXISTS canvases (
  id                 STRING PRIMARY KEY,
  image              STRING,
  derivedFrom        STRING,
  derivedAt          STRING,
  canvasTopLeftX     INTEGER,
  canvasTopLeftY     INTEGER,
  canvasBottomLeftX  INTEGER,
  canvasBottomLeftY  INTEGER,
  canvasTopRightX    INTEGER,
  canvasTopRightY    INTEGER,
  canvasBottomRightX INTEGER,
  canvasBottomRightY INTEGER,

  FOREIGN KEY(image) REFERENCES images(id)
);

CREATE TABLE IF NOT EXISTS connections (
  id                 STRING PRIMARY KEY,
  start              STRING NOT NULL,
  finish             STRING NOT NULL,
  canvas             string NOT NULL,
  type               STRING,

  FOREIGN KEY(start) REFERENCES postits(id),
  FOREIGN Key(finish) REFERENCES postits(id),
  Foreign Key(canvas) REFERENCES canvases(id)
);

CREATE TABLE IF NOT EXISTS postits (
  id                 STRING PRIMARY KEY,
  canvas             STRING NOT NULL,
  topLeftX           INTEGER NOT NULL,
  topLeftY           INTEGER NOT NULL,
  topRightX          INTEGER NOT NULL,
  topRightY          INTEGER NOT NULL,
  bottomRightX       INTEGER NOT NULL,
  bottomRightY       INTEGER NOT NULL,
  bottomLeftX        INTEGER NOT NULL,
  bottomLeftY        INTEGER NOT NULL,
  colour             STRING NOT NULL,

  FOREIGN KEY(canvas) REFERENCES canvases(id)
);
