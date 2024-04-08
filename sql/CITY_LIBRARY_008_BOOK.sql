CREATE TABLE BOOK (
    DOCID INT PRIMARY KEY,
    ISBN VARCHAR(255),
    FOREIGN KEY (DOCID) REFERENCES DOCUMENT(DOCID) ON UPDATE CASCADE ON DELETE CASCADE
);