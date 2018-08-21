drop table if exists schedule;

create table schedule (
    handle varchar(30) unique not null,
    name varchar(50) not null,
    A varchar(30) not null,
    B varchar(30) not null,
    C varchar(30) not null,
    D varchar(30) not null,
    E varchar(30) not null,
    F varchar(30) not null,
    G varchar(30) not null
);