-- Table: public.user

DROP TABLE IF EXISTS public."user";

CREATE TABLE IF NOT EXISTS public."user"
(
    user_id bigint NOT NULL DEFAULT 'nextval('user_user_id_seq'::regclass)',
    user_name character varying(30) COLLATE pg_catalog."default" NOT NULL,
    user_surname character varying(30) COLLATE pg_catalog."default" NOT NULL,
    user_email character varying(100) COLLATE pg_catalog."default" NOT NULL,
    user_phone character varying(20) COLLATE pg_catalog."default" NOT NULL,
    bank_account character varying(16) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (user_id),
    CONSTRAINT email_unique UNIQUE (user_email)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."user"
    OWNER to postgres;

COMMENT ON TABLE public."user"
    IS 'A table for users (owners and buyers)';

DROP TABLE IF EXISTS public.property;

CREATE TABLE IF NOT EXISTS public.property
(
    property_id uuid NOT NULL DEFAULT 'gen_random_uuid()',
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    rooms integer NOT NULL,
    square_meters double precision NOT NULL,
    building_type character varying(20) COLLATE pg_catalog."default" NOT NULL,
    floor_value integer,
    floor_count integer,
    centre_distance double precision,
    owner_id bigint,
    build_year integer NOT NULL,
    city character varying(30) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT property_pkey PRIMARY KEY (property_id),
    CONSTRAINT user_fkey FOREIGN KEY (owner_id)
        REFERENCES public."user" (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.property
    OWNER to postgres;

COMMENT ON TABLE public.property
    IS 'A table for property objects ';

-- Table: public.listing

DROP TABLE IF EXISTS public.listing;

CREATE TABLE IF NOT EXISTS public.listing
(
    listing_id bigint NOT NULL DEFAULT 'nextval('listing_listing_id_seq'::regclass)',
    id_property uuid NOT NULL,
    listing_type character varying(4) COLLATE pg_catalog."default" NOT NULL,
    listing_price double precision NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT 'CURRENT_TIMESTAMP',
    listing_description text COLLATE pg_catalog."default",
    listing_status character varying(10) COLLATE pg_catalog."default" NOT NULL DEFAULT 'active'::character varying,
    id_user bigint NOT NULL DEFAULT 'nextval('listing_id_user_seq'::regclass)',
    CONSTRAINT listing_pkey PRIMARY KEY (listing_id),
    CONSTRAINT property_fkey FOREIGN KEY (id_property)
        REFERENCES public.property (property_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID,
    CONSTRAINT user_fkey FOREIGN KEY (id_user)
        REFERENCES public."user" (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.listing
    OWNER to postgres;

COMMENT ON TABLE public.listing
    IS 'A table for listing ads';

-- Table: public.application

DROP TABLE IF EXISTS public.application;

CREATE TABLE IF NOT EXISTS public.application
(
    application_id bigint NOT NULL DEFAULT 'nextval('application_application_id_seq'::regclass)',
    id_listing bigint NOT NULL DEFAULT 'nextval('application_listing_id_seq'::regclass)',
    id_user bigint,
    application_message text COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT 'CURRENT_TIMESTAMP',
    is_submitted boolean NOT NULL DEFAULT 'false',
    CONSTRAINT application_pkey PRIMARY KEY (application_id),
    CONSTRAINT listing_fkey FOREIGN KEY (id_listing)
        REFERENCES public.listing (listing_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID,
    CONSTRAINT user_fkey FOREIGN KEY (id_user)
        REFERENCES public."user" (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.application
    OWNER to postgres;

COMMENT ON TABLE public.application
    IS 'A table for users comments on listing';

-- Table: public.payment

DROP TABLE IF EXISTS public.payment;

CREATE TABLE IF NOT EXISTS public.payment
(
    payment_id bigint NOT NULL DEFAULT 'nextval('payment_payment_id_seq'::regclass)',
    payment_amount double precision NOT NULL,
    id_sender bigint NOT NULL,
    id_sale uuid NOT NULL,
    sent_at timestamp with time zone NOT NULL DEFAULT 'CURRENT_TIMESTAMP',
    CONSTRAINT payment_pkey PRIMARY KEY (payment_id),
    CONSTRAINT sale_fkey FOREIGN KEY (id_sale)
        REFERENCES public.sale (sale_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID,
    CONSTRAINT sender_fkey FOREIGN KEY (id_sender)
        REFERENCES public."user" (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.payment
    OWNER to postgres;

-- Trigger: after_payment_insert

DROP TRIGGER IF EXISTS after_payment_insert ON public.payment;

CREATE TRIGGER after_payment_insert
    AFTER INSERT
    ON public.payment
    FOR EACH ROW
    EXECUTE FUNCTION public.pay_for_sale();

-- Table: public.sale

DROP TABLE IF EXISTS public.sale;

CREATE TABLE IF NOT EXISTS public.sale
(
    sale_id uuid NOT NULL DEFAULT 'gen_random_uuid()',
    sale_status character varying(10) COLLATE pg_catalog."default" NOT NULL DEFAULT 'active'::character varying,
    sale_price double precision NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT 'CURRENT_TIMESTAMP',
    id_owner bigint DEFAULT 'nextval('sale_id_owner_seq'::regclass)',
    id_buyer bigint DEFAULT 'nextval('sale_id_buyer_seq'::regclass)',
    id_property uuid NOT NULL,
    id_listing bigint,
    termination_reason character varying(20) COLLATE pg_catalog."default",
    termination_details text COLLATE pg_catalog."default",
    terminated_at timestamp with time zone,
    CONSTRAINT sale_pkey PRIMARY KEY (sale_id),
    CONSTRAINT buyer_fkey FOREIGN KEY (id_buyer)
        REFERENCES public."user" (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
        NOT VALID,
    CONSTRAINT listing_fkey FOREIGN KEY (id_listing)
        REFERENCES public.listing (listing_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
        NOT VALID,
    CONSTRAINT owner_fkey FOREIGN KEY (id_owner)
        REFERENCES public."user" (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
        NOT VALID,
    CONSTRAINT property_fkey FOREIGN KEY (id_property)
        REFERENCES public.property (property_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.sale
    OWNER to postgres;

-- Table: public.rental

DROP TABLE IF EXISTS public.rental;

CREATE TABLE IF NOT EXISTS public.rental
(
    rental_id uuid NOT NULL DEFAULT 'gen_random_uuid()',
    start_date date NOT NULL DEFAULT 'CURRENT_DATE',
    end_date date NOT NULL DEFAULT 'CURRENT_DATE',
    rental_amount double precision NOT NULL,
    rental_status character varying(10) COLLATE pg_catalog."default" NOT NULL DEFAULT 'active'::character varying,
    id_landlord bigint,
    id_tenant bigint,
    id_property uuid NOT NULL,
    id_listing bigint,
    termination_reason character varying(20) COLLATE pg_catalog."default",
    termination_details text COLLATE pg_catalog."default",
    terminated_at timestamp with time zone,
    CONSTRAINT rental_pkey PRIMARY KEY (rental_id),
    CONSTRAINT landlord_fkey FOREIGN KEY (id_landlord)
        REFERENCES public."user" (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
        NOT VALID,
    CONSTRAINT listing_fkey FOREIGN KEY (id_listing)
        REFERENCES public.listing (listing_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
        NOT VALID,
    CONSTRAINT property_fkey FOREIGN KEY (id_property)
        REFERENCES public.property (property_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID,
    CONSTRAINT tenant_fkey FOREIGN KEY (id_tenant)
        REFERENCES public."user" (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.rental
    OWNER to postgres;

-- FUNCTION: public.initialize_rental(bigint, date, date)

DROP FUNCTION IF EXISTS public.initialize_rental(bigint, date, date);

CREATE OR REPLACE FUNCTION public.initialize_rental(
	app_id bigint,
	start_date date,
	end_date date)
    RETURNS void
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    _listing_id BIGINT;
    property_id UUID;
    landlord_id BIGINT;
	rental_amount DOUBLE PRECISION;
    tenant_id BIGINT;
BEGIN
    SELECT l.listing_id, l.id_property, l.id_user, a.id_user, l.listing_price
    INTO _listing_id, property_id, landlord_id, tenant_id, rental_amount
    FROM application a
    JOIN listing l ON a.id_listing = l.listing_id
    WHERE a.application_id = app_id;

    UPDATE application
    SET is_submitted = TRUE
    WHERE application_id = app_id;

    UPDATE listing
    SET listing_status = 'closed'
    WHERE listing_id = _listing_id;

    INSERT INTO rental (id_listing, id_property, id_landlord, id_tenant, start_date, end_date, rental_amount)
    VALUES (_listing_id, property_id, landlord_id, tenant_id, start_date, end_date, rental_amount);
END;
$BODY$;

ALTER FUNCTION public.initialize_rental(bigint, date, date)
    OWNER TO postgres;

-- FUNCTION: public.initialize_sale(bigint, timestamp with time zone)

DROP FUNCTION IF EXISTS public.initialize_sale(bigint, timestamp with time zone);

CREATE OR REPLACE FUNCTION public.initialize_sale(
	app_id bigint,
	sale_creation_date timestamp with time zone)
    RETURNS void
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    _listing_id BIGINT;
    property_id UUID;
    owner_id BIGINT;
    buyer_id BIGINT;
	listing_price DOUBLE PRECISION;
BEGIN

    SELECT l.listing_id, l.id_property, l.id_user, l.listing_price, a.id_user
    INTO _listing_id, property_id, owner_id, listing_price, buyer_id
    FROM application a
    JOIN listing l ON a.id_listing = l.listing_id
    WHERE a.application_id = app_id;
    
    UPDATE application
    SET is_submitted = TRUE
    WHERE application_id = app_id;

    UPDATE listing
    SET listing_status = 'closed'
    WHERE listing_id = _listing_id;

    INSERT INTO sale (id_listing, id_property, id_owner, id_buyer, created_at, sale_price)
    VALUES (_listing_id, property_id, owner_id, buyer_id, sale_creation_date, listing_price);
END;
$BODY$;

ALTER FUNCTION public.initialize_sale(bigint, timestamp with time zone)
    OWNER TO postgres;

-- FUNCTION: public.terminate_rental(uuid, character varying, text, timestamp with time zone)

DROP FUNCTION IF EXISTS public.terminate_rental(uuid, character varying, text, timestamp with time zone);

CREATE OR REPLACE FUNCTION public.terminate_rental(
	id_rental uuid,
	ter_reason character varying,
	ter_desc text,
	ter_at timestamp with time zone)
    RETURNS void
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
BEGIN
 UPDATE listing
    SET listing_status = 'active'
    WHERE listing_id = (
        SELECT id_listing
        FROM rental r
        WHERE r.rental_id = id_rental
    );

    UPDATE application
    SET is_submitted = FALSE
   WHERE id_listing = (
        SELECT id_listing
        FROM rental r
        WHERE r.rental_id = id_rental
    );

	UPDATE rental
	SET
	   	termination_reason = ter_reason,
        termination_details = ter_desc,
        terminated_at = ter_at,
        rental_status = 'terminated'
    WHERE rental_id = id_rental;
END;
$BODY$;

ALTER FUNCTION public.terminate_rental(uuid, character varying, text, timestamp with time zone)
    OWNER TO postgres;

-- FUNCTION: public.terminate_sale(uuid, character varying, text, timestamp with time zone)

DROP FUNCTION IF EXISTS public.terminate_sale(uuid, character varying, text, timestamp with time zone);

CREATE OR REPLACE FUNCTION public.terminate_sale(
	id_sale uuid,
	ter_reason character varying,
	ter_desc text,
	ter_at timestamp with time zone)
    RETURNS void
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
BEGIN
 UPDATE listing
    SET listing_status = 'active'
    WHERE listing_id = (
        SELECT id_listing
        FROM sale s
        WHERE s.sale_id = id_sale
    );

    UPDATE application
    SET is_submitted = FALSE
    WHERE id_listing = (
        SELECT id_listing
        FROM sale s
        WHERE s.sale_id = id_sale
    );

	UPDATE sale
	SET
	   	termination_reason = ter_reason,
        termination_details = ter_desc,
        terminated_at = ter_at,
        sale_status = 'terminated'
    WHERE sale_id = id_sale;
END;
$BODY$;

ALTER FUNCTION public.terminate_sale(uuid, character varying, text, timestamp with time zone)
    OWNER TO postgres;
