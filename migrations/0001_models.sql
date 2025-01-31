CREATE TABLE IF NOT EXISTS "main"."expenses" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR (255) NOT NULL,
    "price" INT NOT NULL
);
