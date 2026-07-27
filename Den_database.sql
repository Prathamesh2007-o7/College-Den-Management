use den_sys;

create table CMPN_TT(
	day_of_week varchar(11) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    lecture_name varchar(50) NOT NULL
);

INSERT INTO CMPN_TT (day_of_week, start_time, end_time, lecture_name) VALUES
("Monday", "11:15:00", "13:15:00", "DBMS"),
("Monday", "13:45:00", "15:45:00", "Lab"),
("Tuesday", "11:15:00", "13:15:00", "Lab"),
("Tuesday", "13:45:00", "15:45:00", "DT"),
("Tuesday", "15:45:00", "17:45:00", "MDM"),
("Wednesday", "09:00:00", "11:00:00", "MP"),
("Wednesday", "11:00:00", "13:15:00", "AOA"),
("Wednesday", "13:45:00", "14:45:00", "EM3"),
("Wednesday", "14:45:00", "15:45:00", "DT"),
("Wednesday", "15:45:00", "17:45:00", "MDM"),
("Thursday", "09:00:00", "11:00:00", "Lab"),
("Thursday", "11:00:00", "13:15:00", "Lab"),
("Thursday", "13:45:00", "15:45:00", "EM3"),
("Friday", "09:00:00", "11:00:00", "MDM"),
("Friday", "11:00:00", "13:15:00", "MDM"),
("Friday", "13:45:00", "15:45:00", "MDM");


TRUNCATE TABLE CMPN_TT;
select * from CMPN_TT;

create table IT_TT (
	day_of_week varchar(11) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    lecture_name varchar(50) NOT NULL
);

alter table student
drop column section;
select * from den_entry_log;



insert into student (roll_no, name, department_name) values
("25102C0059", "Pratham", "CMPN"),
("25102C0060", "Hello", "CMPN");

