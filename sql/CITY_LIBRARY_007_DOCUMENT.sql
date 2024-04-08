CREATE TABLE DOCUMENT (
    DOCID INT PRIMARY KEY,
    TITLE VARCHAR(255),
    PDATE DATE,
    PUBLISHERID INT,
    FOREIGN KEY (PUBLISHERID) REFERENCES PUBLISHER(PUBLISHERID) ON UPDATE CASCADE ON DELETE CASCADE
);