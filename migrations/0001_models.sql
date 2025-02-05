CREATE TABLE IF NOT EXISTS "main"."expenses" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR (255) NOT NULL,
    "price" INT NOT NULL
);
