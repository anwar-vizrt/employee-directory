---- This file contains the constants to boostrap the system.
INSERT INTO privilage(actiontype) VALUES ('create');
INSERT INTO privilage(actiontype) VALUES ('view');
INSERT INTO privilage(actiontype) VALUES ('delete');
INSERT INTO privilage(actiontype) VALUES ('update');
INSERT INTO privilage(actiontype) VALUES ('viewall');
INSERT INTO privilage(actiontype) VALUES ('updateall');


INSERT INTO permissions(role_id,privilage_id) VALUES (1,1);
INSERT INTO permissions(role_id,privilage_id) VALUES (1,2);
INSERT INTO permissions(role_id,privilage_id) VALUES (1,3);
INSERT INTO permissions(role_id,privilage_id) VALUES (1,4);
INSERT INTO permissions(role_id,privilage_id) VALUES (1,5);
INSERT INTO permissions(role_id,privilage_id) VALUES (1,6);
INSERT INTO permissions(role_id,privilage_id) VALUES (1,2);
INSERT INTO permissions(role_id,privilage_id) VALUES (1,4);

INSERT INTO employees (
    email ,
    username ,
    firstname ,
    lastname ,
    birthdate ,
    hashed_password,
    type,
    phonenumber
) VALUES ('manager@exmaple.com','admin','qDXJ3ZYpRHRRZPSiI/tmYcDs609EVAOgyECA36gV7+I=','56nBwUl3Bc+qUrI7cxG2lAbcDULuJZt5VKzKnBZyb04=',  'a//bT5jvaNY+BU7vzp4V3noiJ9eQln7o1mpMheX1aZ0=' , '$2b$12$hg34JSZJGZxYHPORdmDxRO0YGHA.B25wSJbD3RYHQodm2ZWvpBJj2', 1, 'nC//uLPJRA1XIO8d449s9L9H23Alou/nO8w1cQoPo50=')
