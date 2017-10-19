drop table if exists bins;
create table bins (
       id integer primary key autoincrement,
       name text unique not null,
       content text not null
);
