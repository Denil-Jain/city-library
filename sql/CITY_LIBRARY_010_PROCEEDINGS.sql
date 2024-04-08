CREATE TABLE PROCEEDINGS (
    DOCID INT PRIMARY KEY,
    CDATE DATE,
    CLOCATION VARCHAR(255),
    CEDITOR VARCHAR(255),
    FOREIGN KEY (DOCID) REFERENCES DOCUMENT(DOCID) ON UPDATE CASCADE ON DELETE CASCADE
);