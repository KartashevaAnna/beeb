SET TIME ZONE "Europe/Moscow";

CREATE TABLE IF NOT EXISTS "main"."category" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR (255) NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS "main"."expenses" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR (255) NOT NULL,
    "price" INT NOT NULL,
    "category_id" INT NOT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);