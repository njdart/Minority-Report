CREATE TABLE IF NOT EXISTS users (
  id       INTEGER PRIMARY KEY autoincrement,
  username TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS images (
  id                STRING PRIMARY KEY,
  user              INTEGER NOT NULL,
  timestamp         STRING NOT NULL,

  FOREIGN KEY(user) REFERENCES users(id)
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
  id     STRING PRIMARY KEY,
  canvas STRING,
  height INTEGER NOT NULL,
  width  INTEGER NOT NULL,
  realX  INTEGER NOT NULL,
  realY  INTEGER NOT NULL,
  colour STRING NOT NULL,
  keystone1X NOT NULL,
  keystone1Y NOT NULL,
  keystone2X NOT NULL,
  keystone2Y NOT NULL,
  keystone3X NOT NULL,
  keystone3Y NOT NULL,
  keystone4X NOT NULL,
  keystone4Y NOT NULL,

  FOREIGN KEY(canvas) REFERENCES canvases(id)
);
