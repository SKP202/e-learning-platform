--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2025-06-16 19:02:24

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- TOC entry 234 (class 1259 OID 24763)
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_messages (
    id integer NOT NULL,
    course_id integer NOT NULL,
    user_id integer NOT NULL,
    message_text text NOT NULL,
    sent_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- TOC entry 233 (class 1259 OID 24762)
-- Name: chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5004 (class 0 OID 0)
-- Dependencies: 233
-- Name: chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_messages_id_seq OWNED BY public.chat_messages.id;


--
-- TOC entry 232 (class 1259 OID 24677)
-- Name: completed_courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.completed_courses (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    completed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- TOC entry 231 (class 1259 OID 24676)
-- Name: completed_courses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.completed_courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5005 (class 0 OID 0)
-- Dependencies: 231
-- Name: completed_courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.completed_courses_id_seq OWNED BY public.completed_courses.id;


--
-- TOC entry 224 (class 1259 OID 24588)
-- Name: courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text NOT NULL,
    structure jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by integer,
    badge_image_path character varying(255)
);


--
-- TOC entry 223 (class 1259 OID 24587)
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5006 (class 0 OID 0)
-- Dependencies: 223
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- TOC entry 220 (class 1259 OID 16413)
-- Name: enrollments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.enrollments (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    enrolled_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- TOC entry 219 (class 1259 OID 16412)
-- Name: enrollments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.enrollments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5007 (class 0 OID 0)
-- Dependencies: 219
-- Name: enrollments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.enrollments_id_seq OWNED BY public.enrollments.id;


--
-- TOC entry 226 (class 1259 OID 24632)
-- Name: exam_submissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.exam_submissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    chapter_idx integer NOT NULL,
    submission_type character varying(20) NOT NULL,
    submission_data text,
    submission_content text,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    submitted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filename character varying(255),
    file_path text,
    teacher_note text
);


--
-- TOC entry 225 (class 1259 OID 24631)
-- Name: exam_submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.exam_submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5008 (class 0 OID 0)
-- Dependencies: 225
-- Name: exam_submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.exam_submissions_id_seq OWNED BY public.exam_submissions.id;


--
-- TOC entry 228 (class 1259 OID 24644)
-- Name: issue_reports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.issue_reports (
    id integer NOT NULL,
    teacher_id integer NOT NULL,
    title character varying(255),
    description text NOT NULL,
    reported_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(20) DEFAULT 'open'::character varying NOT NULL
);


--
-- TOC entry 227 (class 1259 OID 24643)
-- Name: issue_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.issue_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5009 (class 0 OID 0)
-- Dependencies: 227
-- Name: issue_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.issue_reports_id_seq OWNED BY public.issue_reports.id;


--
-- TOC entry 230 (class 1259 OID 24660)
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL,
    is_read boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    link_url character varying(255)
);


--
-- TOC entry 229 (class 1259 OID 24659)
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5010 (class 0 OID 0)
-- Dependencies: 229
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- TOC entry 222 (class 1259 OID 24578)
-- Name: pending_courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pending_courses (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    requested_by character varying(255) NOT NULL
);


--
-- TOC entry 221 (class 1259 OID 24577)
-- Name: pending_courses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pending_courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5011 (class 0 OID 0)
-- Dependencies: 221
-- Name: pending_courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pending_courses_id_seq OWNED BY public.pending_courses.id;


--
-- TOC entry 218 (class 1259 OID 16390)
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    proof_path character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    verified boolean DEFAULT true,
    profile_pic character varying(255),
    proof_data bytea,
    can_create_course boolean DEFAULT false
);


--
-- TOC entry 217 (class 1259 OID 16389)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5012 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4802 (class 2604 OID 24766)
-- Name: chat_messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);


--
-- TOC entry 4800 (class 2604 OID 24680)
-- Name: completed_courses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.completed_courses ALTER COLUMN id SET DEFAULT nextval('public.completed_courses_id_seq'::regclass);


--
-- TOC entry 4789 (class 2604 OID 24591)
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- TOC entry 4786 (class 2604 OID 16416)
-- Name: enrollments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments ALTER COLUMN id SET DEFAULT nextval('public.enrollments_id_seq'::regclass);


--
-- TOC entry 4791 (class 2604 OID 24635)
-- Name: exam_submissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exam_submissions ALTER COLUMN id SET DEFAULT nextval('public.exam_submissions_id_seq'::regclass);


--
-- TOC entry 4794 (class 2604 OID 24647)
-- Name: issue_reports id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issue_reports ALTER COLUMN id SET DEFAULT nextval('public.issue_reports_id_seq'::regclass);


--
-- TOC entry 4797 (class 2604 OID 24663)
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- TOC entry 4788 (class 2604 OID 24581)
-- Name: pending_courses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pending_courses ALTER COLUMN id SET DEFAULT nextval('public.pending_courses_id_seq'::regclass);


--
-- TOC entry 4782 (class 2604 OID 16393)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4998 (class 0 OID 24763)
-- Dependencies: 234
-- Data for Name: chat_messages; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4996 (class 0 OID 24677)
-- Dependencies: 232
-- Data for Name: completed_courses; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4988 (class 0 OID 24588)
-- Dependencies: 224
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4984 (class 0 OID 16413)
-- Dependencies: 220
-- Data for Name: enrollments; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4990 (class 0 OID 24632)
-- Dependencies: 226
-- Data for Name: exam_submissions; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4992 (class 0 OID 24644)
-- Dependencies: 228
-- Data for Name: issue_reports; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4994 (class 0 OID 24660)
-- Dependencies: 230
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4986 (class 0 OID 24578)
-- Dependencies: 222
-- Data for Name: pending_courses; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4982 (class 0 OID 16390)
-- Dependencies: 218
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.users VALUES (9, 'admin', 'admin@example.com', 'admin', 'admin', NULL, '2025-05-28 16:52:13.379173', true, 'images.jpg', NULL, false);


--
-- TOC entry 5013 (class 0 OID 0)
-- Dependencies: 233
-- Name: chat_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.chat_messages_id_seq', 28, true);


--
-- TOC entry 5014 (class 0 OID 0)
-- Dependencies: 231
-- Name: completed_courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.completed_courses_id_seq', 3, true);


--
-- TOC entry 5015 (class 0 OID 0)
-- Dependencies: 223
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.courses_id_seq', 6, true);


--
-- TOC entry 5016 (class 0 OID 0)
-- Dependencies: 219
-- Name: enrollments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.enrollments_id_seq', 10, true);


--
-- TOC entry 5017 (class 0 OID 0)
-- Dependencies: 225
-- Name: exam_submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.exam_submissions_id_seq', 24, true);


--
-- TOC entry 5018 (class 0 OID 0)
-- Dependencies: 227
-- Name: issue_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.issue_reports_id_seq', 6, true);


--
-- TOC entry 5019 (class 0 OID 0)
-- Dependencies: 229
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notifications_id_seq', 57, true);


--
-- TOC entry 5020 (class 0 OID 0)
-- Dependencies: 221
-- Name: pending_courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pending_courses_id_seq', 12, true);


--
-- TOC entry 5021 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 26, true);


--
-- TOC entry 4827 (class 2606 OID 24771)
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- TOC entry 4823 (class 2606 OID 24683)
-- Name: completed_courses completed_courses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.completed_courses
    ADD CONSTRAINT completed_courses_pkey PRIMARY KEY (id);


--
-- TOC entry 4825 (class 2606 OID 24685)
-- Name: completed_courses completed_courses_user_id_course_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.completed_courses
    ADD CONSTRAINT completed_courses_user_id_course_id_key UNIQUE (user_id, course_id);


--
-- TOC entry 4815 (class 2606 OID 24596)
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- TOC entry 4809 (class 2606 OID 16419)
-- Name: enrollments enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_pkey PRIMARY KEY (id);


--
-- TOC entry 4811 (class 2606 OID 16421)
-- Name: enrollments enrollments_user_id_course_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_user_id_course_id_key UNIQUE (user_id, course_id);


--
-- TOC entry 4817 (class 2606 OID 24641)
-- Name: exam_submissions exam_submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exam_submissions
    ADD CONSTRAINT exam_submissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4819 (class 2606 OID 24653)
-- Name: issue_reports issue_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issue_reports
    ADD CONSTRAINT issue_reports_pkey PRIMARY KEY (id);


--
-- TOC entry 4821 (class 2606 OID 24669)
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- TOC entry 4813 (class 2606 OID 24585)
-- Name: pending_courses pending_courses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pending_courses
    ADD CONSTRAINT pending_courses_pkey PRIMARY KEY (id);


--
-- TOC entry 4805 (class 2606 OID 16398)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4807 (class 2606 OID 16400)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 4829 (class 2606 OID 24618)
-- Name: courses courses_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 4828 (class 2606 OID 16422)
-- Name: enrollments enrollments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4834 (class 2606 OID 24772)
-- Name: chat_messages fk_course_chat; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT fk_course_chat FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- TOC entry 4832 (class 2606 OID 24691)
-- Name: completed_courses fk_course_completed; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.completed_courses
    ADD CONSTRAINT fk_course_completed FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- TOC entry 4830 (class 2606 OID 24654)
-- Name: issue_reports fk_teacher; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issue_reports
    ADD CONSTRAINT fk_teacher FOREIGN KEY (teacher_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 4835 (class 2606 OID 24777)
-- Name: chat_messages fk_user_chat; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT fk_user_chat FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4833 (class 2606 OID 24686)
-- Name: completed_courses fk_user_completed; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.completed_courses
    ADD CONSTRAINT fk_user_completed FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4831 (class 2606 OID 24670)
-- Name: notifications fk_user_notification; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT fk_user_notification FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


-- Completed on 2025-06-16 19:02:24

--
-- PostgreSQL database dump complete
--

