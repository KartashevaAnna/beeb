SET TIME ZONE "Europe/Moscow";

CREATE TABLE IF NOT EXISTS "main"."category" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR (255) NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "user_id" INT NOT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP WITH TIME ZONE
);


CREATE TABLE IF NOT EXISTS "main"."payments" (
    "id" SERIAL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "name" VARCHAR (255) NOT NULL,
    "grams" INT,
    "quantity" INT,
    "amount" INT NOT NULL,
    "category_id" INT NOT NULL,
    "user_id" INT NOT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "main"."income" (
    "id" SERIAL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "name" VARCHAR (255) NOT NULL,
    "amount" INT NOT NULL,
    "user_id" INT NOT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "main"."users"(
    "id" SERIAL PRIMARY KEY,
    "username" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash_sum" bytea NOT NULL 
);