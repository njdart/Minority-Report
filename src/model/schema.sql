CREATE TABLE IF NOT EXISTS session (
  id                        TEXT PRIMARY KEY,
  name                      TEXT NOT NULL,
  description               TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS instanceConfiguration (
  id                        TEXT PRIMARY KEY,
  sessionId                 TEXT NOT NULL,
  userId                    TEXT NOT NULL,
  topLeftX                  NUMERIC,
  topLeftY                  NUMERIC,
  topRightX                 NUMERIC,
  topRightY                 NUMERIC,
  bottomRightX              NUMERIC,
  bottomRightY              NUMERIC,
  bottomLeftX               NUMERIC,
  bottomLeftY               NUMERIC,
  cameraHost                TEXT NOT NULL,
  kinectHost                TEXT NOT NULL,
  cameraPort                INTEGER NOT NULL,
  kinectPort                INTEGER NOT NULL,

  FOREIGN KEY(sessionId) REFERENCES session(id),
  FOREIGN KEY(userId) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS users (
  id                        TEXT PRIMARY KEY,
  name                      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS images (
  id                        TEXT PRIMARY KEY,
  timestamp                 TEXT NOT NULL,
  instanceConfigurationId   TEXT NOT NULL,

  FOREIGN KEY(instanceConfigurationId) REFERENCES instanceConfiguration(id)
);

CREATE TABLE IF NOT EXISTS canvases (
  id                        TEXT PRIMARY KEY,
  session                   TEXT NOT NULL,
  derivedFrom               TEXT,
  derivedAt                 TEXT NOT NULL,
  height                    INTEGER NOT NULL,
  width                     INTEGER NOT NULL,

  FOREIGN KEY(session) REFERENCES session(id)
);

CREATE TABLE IF NOT EXISTS connections (
  id                        TEXT PRIMARY KEY,
  start                     TEXT NOT NULL,
  finish                    TEXT NOT NULL,
  canvas                    TEXT NOT NULL,
  type                      TEXT,

  FOREIGN KEY(start) REFERENCES postits(id),
  FOREIGN Key(finish) REFERENCES postits(id),
  Foreign Key(canvas) REFERENCES canvases(id)
);

CREATE TABLE IF NOT EXISTS postits (
  id                        TEXT PRIMARY KEY,
  canvas                    TEXT NOT NULL,
  physicalFor               TEXT,
  topLeftX                  INTEGER NOT NULL,
  topLeftY                  INTEGER NOT NULL,
  topRightX                 INTEGER NOT NULL,
  topRightY                 INTEGER NOT NULL,
  bottomRightX              INTEGER NOT NULL,
  bottomRightY              INTEGER NOT NULL,
  bottomLeftX               INTEGER NOT NULL,
  bottomLeftY               INTEGER NOT NULL,
  displayPosX               INTEGER NOT NULL,
  displayPosY               INTEGER NOT NULL,
  colour                    TEXT NOT NULL,
  image                     TEXT NOT NULL,

  FOREIGN KEY(canvas) REFERENCES canvases(id)
);
