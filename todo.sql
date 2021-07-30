
create table if not exists tasks(
    pid integer primary key AUTOINCREMENT,
    user text not null ,
    content TEXT NOT NULL,
    done BOOLEAN,
    FOREIGN KEY (user) REFERENCES customer(name)
);