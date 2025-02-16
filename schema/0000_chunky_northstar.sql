CREATE TABLE "instructions" (
	"id" uuid PRIMARY KEY NOT NULL,
	"text" varchar NOT NULL,
	"recipe" uuid NOT NULL,
	"position" integer NOT NULL,
	CONSTRAINT "instructions_recipe_position_unique" UNIQUE("recipe","position")
);
--> statement-breakpoint
CREATE TABLE "recipes" (
	"id" uuid PRIMARY KEY NOT NULL,
	"user" varchar NOT NULL,
	"title" varchar NOT NULL,
	"slug" varchar NOT NULL,
	"description" varchar,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "recipes_slug_user_unique" UNIQUE("slug","user")
);
--> statement-breakpoint
ALTER TABLE "instructions" ADD CONSTRAINT "instructions_recipe_recipes_id_fk" FOREIGN KEY ("recipe") REFERENCES "public"."recipes"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "slug_idx" ON "recipes" USING btree ("slug");