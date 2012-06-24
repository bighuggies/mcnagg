CREATE TABLE mindcrackers (
	username		text		PRIMARY KEY,
	name			text		UNIQUE NOT NULL,
);

CREATE TABLE videos (
	video_id		text		PRIMARY KEY,
	title			text		NOT NULL,
	duration		integer		NOT NULL,
	uploader		text		REFERENCES mindcrackers(username) ON DELETE CASCADE,
	uploaded		timestamp	NOT NULL,
	description		text,
	thumbnail		text		NOT NULL
);

CREATE INDEX upload_date ON videos(uploaded);

CREATE TABLE series (
	series_name		text,
	video_id		text		REFERENCES videos(video_id),
	PRIMARY KEY(series_name, video_id)
);

CREATE INDEX series_name on series(series_name);