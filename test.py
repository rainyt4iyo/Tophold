'''

create table gym_projects(
    id serial primary key,
    gym_id integer not null,
    project_name text not null,
    description text,
    project_type text,
    tie_breaker boolean,
    limit_people integer,
    deadline date,
    schedule date);


'''