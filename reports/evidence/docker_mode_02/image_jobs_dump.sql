--
-- PostgreSQL database dump
--

\restrict IUUKCWNZZ8gjlHumH3AwiVVG6fg5p8F0bxyBz7XETt0qzxnwzNtF7yschvSlpsH

-- Dumped from database version 17.11
-- Dumped by pg_dump version 17.11

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

--
-- Data for Name: image_jobs; Type: TABLE DATA; Schema: public; Owner: vision_user
--

INSERT INTO public.image_jobs VALUES (1, '10efee405cd94d08b8f12fb94564b955.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.6051397323608398, '[{"label": "bean_rust", "score": 0.6051397323608398}, {"label": "healthy", "score": 0.2607002258300781}, {"label": "angular_leaf_spot", "score": 0.13415999710559845}]', 2214.16, false, NULL, '2026-11-04 02:09:20.318518+00', '2026-11-04 02:09:22.597558+00');
INSERT INTO public.image_jobs VALUES (2, '1f49c5bd237c4c7795a470b50113641a.bin', 'done', 'artifacts/beans_resnet18', 'angular_leaf_spot', 0.3825364112854004, '[{"label": "angular_leaf_spot", "score": 0.3825364112854004}, {"label": "healthy", "score": 0.3227664828300476}, {"label": "bean_rust", "score": 0.2946971356868744}]', 16.9, false, NULL, '2026-11-04 02:09:22.759201+00', '2026-11-04 02:09:22.788987+00');
INSERT INTO public.image_jobs VALUES (3, '2a2298c8445b45e6b85ffe1f27f82dc9.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.49997395277023315, '[{"label": "bean_rust", "score": 0.49997395277023315}, {"label": "healthy", "score": 0.32026687264442444}, {"label": "angular_leaf_spot", "score": 0.17975914478302002}]', 17.88, false, NULL, '2026-11-04 02:09:22.875718+00', '2026-11-04 02:09:22.905636+00');
INSERT INTO public.image_jobs VALUES (4, '434d49da360e46918c1d8c402e5388e6.bin', 'done', 'artifacts/beans_resnet18', 'angular_leaf_spot', 0.5795527100563049, '[{"label": "angular_leaf_spot", "score": 0.5795527100563049}, {"label": "bean_rust", "score": 0.34941303730010986}, {"label": "healthy", "score": 0.07103423774242401}]', 21.02, false, NULL, '2026-11-04 02:09:22.997388+00', '2026-11-04 02:09:23.031101+00');
INSERT INTO public.image_jobs VALUES (5, '5366e47d2c6a454789a1fc39c01e2b7d.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.5910789966583252, '[{"label": "bean_rust", "score": 0.5910789966583252}, {"label": "angular_leaf_spot", "score": 0.2602975368499756}, {"label": "healthy", "score": 0.14862346649169922}]', 18.2, false, NULL, '2026-11-04 02:09:23.118984+00', '2026-11-04 02:09:23.14978+00');
INSERT INTO public.image_jobs VALUES (6, '9e222a496d9648d49870b26e4038a68d.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.8477829694747925, '[{"label": "healthy", "score": 0.8477829694747925}, {"label": "bean_rust", "score": 0.07835608720779419}, {"label": "angular_leaf_spot", "score": 0.07386096566915512}]', 19.79, false, NULL, '2026-11-04 02:09:23.239869+00', '2026-11-04 02:09:23.271869+00');
INSERT INTO public.image_jobs VALUES (7, '5928652a86ed47cab7685509fe617b51.bin', 'done', 'artifacts/beans_resnet18', 'angular_leaf_spot', 0.3825364112854004, '[{"label": "angular_leaf_spot", "score": 0.3825364112854004}, {"label": "healthy", "score": 0.3227664828300476}, {"label": "bean_rust", "score": 0.2946971356868744}]', NULL, true, NULL, '2026-11-04 02:09:23.361019+00', '2026-11-04 02:09:23.370865+00');
INSERT INTO public.image_jobs VALUES (8, 'cef9b2587ea64e03b7d85782863b6201.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.49997395277023315, '[{"label": "bean_rust", "score": 0.49997395277023315}, {"label": "healthy", "score": 0.32026687264442444}, {"label": "angular_leaf_spot", "score": 0.17975914478302002}]', NULL, true, NULL, '2026-11-04 02:09:23.482547+00', '2026-11-04 02:09:23.492454+00');
INSERT INTO public.image_jobs VALUES (9, '758ee1ecc5e7410082ca16530b000f26.bin', 'done', 'artifacts/beans_resnet18', 'angular_leaf_spot', 0.5795527100563049, '[{"label": "angular_leaf_spot", "score": 0.5795527100563049}, {"label": "bean_rust", "score": 0.34941303730010986}, {"label": "healthy", "score": 0.07103423774242401}]', NULL, true, NULL, '2026-11-04 02:09:23.599896+00', '2026-11-04 02:09:23.610859+00');
INSERT INTO public.image_jobs VALUES (10, '8cbb2f8434094ead816637f8da54da5e.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.5910789966583252, '[{"label": "bean_rust", "score": 0.5910789966583252}, {"label": "angular_leaf_spot", "score": 0.2602975368499756}, {"label": "healthy", "score": 0.14862346649169922}]', NULL, true, NULL, '2026-11-04 02:09:23.71988+00', '2026-11-04 02:09:23.729728+00');
INSERT INTO public.image_jobs VALUES (11, 'a0b360a3b8504627a7aa32fb31e0175b.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.8477829694747925, '[{"label": "healthy", "score": 0.8477829694747925}, {"label": "bean_rust", "score": 0.07835608720779419}, {"label": "angular_leaf_spot", "score": 0.07386096566915512}]', NULL, true, NULL, '2026-11-04 02:09:23.835632+00', '2026-11-04 02:09:23.845177+00');
INSERT INTO public.image_jobs VALUES (12, '4928c994ac984f49a482d18ae3af6a09.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.6522662043571472, '[{"label": "healthy", "score": 0.6522662043571472}, {"label": "bean_rust", "score": 0.17907971143722534}, {"label": "angular_leaf_spot", "score": 0.16865405440330505}]', 2413.05, false, NULL, '2026-11-04 02:09:51.771602+00', '2026-11-04 02:10:02.29805+00');
INSERT INTO public.image_jobs VALUES (13, 'd9cd7d9c06d94475a26d72578e49db64.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.48154979944229126, '[{"label": "bean_rust", "score": 0.48154979944229126}, {"label": "angular_leaf_spot", "score": 0.37498733401298523}, {"label": "healthy", "score": 0.14346285164356232}]', 22.78, false, NULL, '2026-11-04 02:36:09.255138+00', '2026-11-04 02:36:09.294808+00');


--
-- Name: image_jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vision_user
--

SELECT pg_catalog.setval('public.image_jobs_id_seq', 13, true);


--
-- PostgreSQL database dump complete
--

\unrestrict IUUKCWNZZ8gjlHumH3AwiVVG6fg5p8F0bxyBz7XETt0qzxnwzNtF7yschvSlpsH

