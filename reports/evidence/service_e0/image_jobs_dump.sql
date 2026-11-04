--
-- PostgreSQL database dump
--

\restrict 2SeWvZCa9dca0sAn1ykmDlDbEF5ChzcjQwJzwzHEDgqniwhq1tljK3FM44Pu21d

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

INSERT INTO public.image_jobs VALUES (1, '8147b940ac16401591718c808bbdea30.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.43387433886528015, '[{"label": "healthy", "score": 0.43387433886528015}, {"label": "angular_leaf_spot", "score": 0.28658926486968994}, {"label": "bean_rust", "score": 0.2795363664627075}]', 2739.24, false, NULL, '2026-11-04 03:10:21.328018+00', '2026-11-04 03:10:24.149655+00');
INSERT INTO public.image_jobs VALUES (2, '16ff7c918bfb42fd8f4db8ac158b7607.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.4297408163547516, '[{"label": "bean_rust", "score": 0.4297408163547516}, {"label": "healthy", "score": 0.36878353357315063}, {"label": "angular_leaf_spot", "score": 0.20147566497325897}]', 18.32, false, NULL, '2026-11-04 03:10:24.283249+00', '2026-11-04 03:10:24.313906+00');
INSERT INTO public.image_jobs VALUES (3, '66a3644c5a214096ba7b58152628f702.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.7168291807174683, '[{"label": "healthy", "score": 0.7168291807174683}, {"label": "bean_rust", "score": 0.208942249417305}, {"label": "angular_leaf_spot", "score": 0.07422858476638794}]', 19.06, false, NULL, '2026-11-04 03:10:24.400955+00', '2026-11-04 03:10:24.431461+00');
INSERT INTO public.image_jobs VALUES (4, '106ca451fada47a5beca2d1cc5cb626b.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.4477872848510742, '[{"label": "bean_rust", "score": 0.4477872848510742}, {"label": "angular_leaf_spot", "score": 0.27800148725509644}, {"label": "healthy", "score": 0.27421119809150696}]', 19.76, false, NULL, '2026-11-04 03:10:24.519611+00', '2026-11-04 03:10:24.551034+00');
INSERT INTO public.image_jobs VALUES (5, '83591ddf1ce54a40b40f362274957ba2.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.4930386543273926, '[{"label": "healthy", "score": 0.4930386543273926}, {"label": "bean_rust", "score": 0.3378326892852783}, {"label": "angular_leaf_spot", "score": 0.1691286265850067}]', 18.85, false, NULL, '2026-11-04 03:10:24.639222+00', '2026-11-04 03:10:24.669638+00');
INSERT INTO public.image_jobs VALUES (6, '75e15cd0530944c0abc1fda8cffe0275.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.7436167597770691, '[{"label": "healthy", "score": 0.7436167597770691}, {"label": "bean_rust", "score": 0.1829194873571396}, {"label": "angular_leaf_spot", "score": 0.07346376031637192}]', 17.75, false, NULL, '2026-11-04 03:10:24.754035+00', '2026-11-04 03:10:24.783954+00');
INSERT INTO public.image_jobs VALUES (7, '6697ac96a4dc49de99c8dc7fe362e817.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.4297408163547516, '[{"label": "bean_rust", "score": 0.4297408163547516}, {"label": "healthy", "score": 0.36878353357315063}, {"label": "angular_leaf_spot", "score": 0.20147566497325897}]', NULL, true, NULL, '2026-11-04 03:10:24.870447+00', '2026-11-04 03:10:24.87989+00');
INSERT INTO public.image_jobs VALUES (8, 'ebdc2c5adae64a9faa47ba3c21844ede.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.7168291807174683, '[{"label": "healthy", "score": 0.7168291807174683}, {"label": "bean_rust", "score": 0.208942249417305}, {"label": "angular_leaf_spot", "score": 0.07422858476638794}]', NULL, true, NULL, '2026-11-04 03:10:24.985111+00', '2026-11-04 03:10:24.993983+00');
INSERT INTO public.image_jobs VALUES (9, '74850351dba94222b8191323c152f05c.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.4477872848510742, '[{"label": "bean_rust", "score": 0.4477872848510742}, {"label": "angular_leaf_spot", "score": 0.27800148725509644}, {"label": "healthy", "score": 0.27421119809150696}]', NULL, true, NULL, '2026-11-04 03:10:25.102904+00', '2026-11-04 03:10:25.112883+00');
INSERT INTO public.image_jobs VALUES (10, 'c6cb71eb32864a4f8e7c0c93532d3bd7.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.4930386543273926, '[{"label": "healthy", "score": 0.4930386543273926}, {"label": "bean_rust", "score": 0.3378326892852783}, {"label": "angular_leaf_spot", "score": 0.1691286265850067}]', NULL, true, NULL, '2026-11-04 03:10:25.222578+00', '2026-11-04 03:10:25.232299+00');
INSERT INTO public.image_jobs VALUES (11, '12601798ba564d01b25ba9ab6c97687a.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.7436167597770691, '[{"label": "healthy", "score": 0.7436167597770691}, {"label": "bean_rust", "score": 0.1829194873571396}, {"label": "angular_leaf_spot", "score": 0.07346376031637192}]', NULL, true, NULL, '2026-11-04 03:10:25.338988+00', '2026-11-04 03:10:25.348386+00');
INSERT INTO public.image_jobs VALUES (12, '802761615a3d4a96ad5424c707707760.bin', 'done', 'artifacts/beans_resnet18', 'healthy', 0.8513124585151672, '[{"label": "healthy", "score": 0.8513124585151672}, {"label": "bean_rust", "score": 0.0959252119064331}, {"label": "angular_leaf_spot", "score": 0.052762389183044434}]', 2808.34, false, NULL, '2026-11-04 03:10:42.916718+00', '2026-11-04 03:13:24.872015+00');
INSERT INTO public.image_jobs VALUES (13, '21ee240c252a4379a800b1acfb1a52f4.bin', 'failed', 'artifacts/beans_resnet18', NULL, NULL, NULL, NULL, NULL, 'FileNotFoundError: [Errno 2] No such file or directory: ''/home/user1/kh-subject9-eval-beans/media/jobs/21ee240c252a4379a800b1acfb1a52f4.bin''', '2026-11-04 03:10:42.930755+00', '2026-11-04 03:13:24.882771+00');
INSERT INTO public.image_jobs VALUES (14, 'c7fcfda54b1b416881f6e65856a831ac.bin', 'failed', 'artifacts/beans_resnet18', NULL, NULL, NULL, NULL, NULL, '작업 큐 등록 실패: Redis 연결을 확인하세요.', '2026-11-04 03:13:43.478647+00', '2026-11-04 03:13:44.085234+00');
INSERT INTO public.image_jobs VALUES (15, 'f0f6b42c4bef49a5a38abacd266554f5.bin', 'done', 'artifacts/beans_resnet18', 'bean_rust', 0.42560604214668274, '[{"label": "bean_rust", "score": 0.42560604214668274}, {"label": "healthy", "score": 0.36120185256004333}, {"label": "angular_leaf_spot", "score": 0.2131921350955963}]', 20.36, false, NULL, '2026-11-04 03:13:52.558095+00', '2026-11-04 03:13:52.596847+00');
INSERT INTO public.image_jobs VALUES (16, '7c31ef9696034b588b86ed84efd5e891.bin', 'done', 'artifacts/beans_resnet18', 'angular_leaf_spot', 0.5672573447227478, '[{"label": "angular_leaf_spot", "score": 0.5672573447227478}, {"label": "healthy", "score": 0.2516064941883087}, {"label": "bean_rust", "score": 0.1811361461877823}]', 21.05, false, NULL, '2026-11-04 03:14:13.605422+00', '2026-11-04 03:14:13.642357+00');


--
-- Name: image_jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vision_user
--

SELECT pg_catalog.setval('public.image_jobs_id_seq', 16, true);


--
-- PostgreSQL database dump complete
--

\unrestrict 2SeWvZCa9dca0sAn1ykmDlDbEF5ChzcjQwJzwzHEDgqniwhq1tljK3FM44Pu21d

