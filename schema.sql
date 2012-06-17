CREATE TABLE mindcrackers (
	username		text		PRIMARY KEY,
	url				text
);

CREATE TABLE videos (
	video_id		text		PRIMARY KEY,
	title			text,
	duration		integer,
	uploader		text		REFERENCES mindcrackers(username) ON DELETE CASCADE,
	uploaded		timestamp,
	description		text,
	thumbnail		text
);

CREATE INDEX upload_date ON videos(uploaded);

CREATE TABLE series (
	series_name		text,
	video_id		text		REFERENCES videos(video_id),
	PRIMARY KEY(series_name, video_id)
);

CREATE INDEX series_name on series(series_name);