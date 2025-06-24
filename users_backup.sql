--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13
-- Dumped by pg_dump version 15.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: telegram_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.telegram_users (
    id integer NOT NULL,
    chat_id bigint NOT NULL,
    subscribed_at timestamp without time zone NOT NULL,
    unsubscribed_at timestamp without time zone,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.telegram_users OWNER TO postgres;

--
-- Name: telegram_users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.telegram_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.telegram_users_id_seq OWNER TO postgres;

--
-- Name: telegram_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.telegram_users_id_seq OWNED BY public.telegram_users.id;


--
-- Name: telegram_users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telegram_users ALTER COLUMN id SET DEFAULT nextval('public.telegram_users_id_seq'::regclass);


--
-- Data for Name: telegram_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.telegram_users (id, chat_id, subscribed_at, unsubscribed_at, is_active, created_at, updated_at) FROM stdin;
1	6186375028	2025-06-20 16:08:07.772882	\N	t	2025-06-20 11:45:17.592008	2025-06-20 16:08:07.772896
2	648502453	2025-06-20 16:41:06.740799	\N	t	2025-06-20 13:41:06.73474	2025-06-20 13:41:06.73474
3	502916506	2025-06-20 16:47:52.390423	\N	t	2025-06-20 13:47:52.388515	2025-06-20 13:47:52.388515
4	5153943111	2025-06-23 20:35:41.637438	\N	t	2025-06-23 17:35:41.635288	2025-06-23 17:35:41.635288
5	7610134614	2025-06-23 21:12:40.204716	2025-06-23 21:12:55.502261	f	2025-06-23 18:12:40.200942	2025-06-23 21:12:55.502271
6	6790554164	2025-06-23 21:14:37.652132	2025-06-23 21:15:09.273144	f	2025-06-23 18:14:37.650963	2025-06-23 21:15:09.273152
7	7012927015	2025-06-23 21:25:41.357934	\N	t	2025-06-23 18:25:41.354817	2025-06-23 18:25:41.354817
\.


--
-- Name: telegram_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.telegram_users_id_seq', 7, true);


--
-- Name: telegram_users telegram_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_pkey PRIMARY KEY (id);


--
-- Name: ix_telegram_users_chat_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_telegram_users_chat_id ON public.telegram_users USING btree (chat_id);


--
-- PostgreSQL database dump complete
--

