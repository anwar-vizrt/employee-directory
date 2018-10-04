---- This file contains the constants to boostrap the system.
--INSERT INTO roles(roletype) VALUES ('manager');
--INSERT INTO roles(roletype) VALUES ('regular');
--
--INSERT INTO privilage(actiontype) VALUES ('create');
--INSERT INTO privilage(actiontype) VALUES ('view');
--INSERT INTO privilage(actiontype) VALUES ('delete');
--INSERT INTO privilage(actiontype) VALUES ('update');
--INSERT INTO privilage(actiontype) VALUES ('viewall');
--INSERT INTO privilage(actiontype) VALUES ('updateall');
--
--
--INSERT INTO permissions(role_id,privilage_id) VALUES (1,1);
--INSERT INTO permissions(role_id,privilage_id) VALUES (1,2);
--INSERT INTO permissions(role_id,privilage_id) VALUES (1,3);
--INSERT INTO permissions(role_id,privilage_id) VALUES (1,4);
--INSERT INTO permissions(role_id,privilage_id) VALUES (1,5);
--INSERT INTO permissions(role_id,privilage_id) VALUES (1,6);
--INSERT INTO permissions(role_id,privilage_id) VALUES (1,2);
--INSERT INTO permissions(role_id,privilage_id) VALUES (1,4);

INSERT INTO employees (
    email ,
    username ,
    firstname ,
    lastname ,
    birthdate ,
    hashed_password,
    phonenumber
) VALUES ('sk.anwarul.islam','anwar','Anwarul','Islam',  to_date('08-07-1987', 'DD-MM-YYY'), 'anwar123', '0123454')
