#!/usr/bin/env bash
# 실행 캡처용 명령 출력 수집 → reports/evidence/screens/src/*.txt (서비스·Docker 실행 중일 때)

O=reports/evidence/screens/src; mkdir -p $O
cd ~/kh-subject9-eval-beans || exit 1
source .venv/bin/activate
P='user1@wsl:~/kh-subject9-eval-beans$'
run() { # $1 = 파일명, 나머지 = 명령 (bash -c)
  f=$O/$1.txt; shift
  { echo "$P $*"; bash -c "$*" 2>&1; } >> $f
}
# 01 데이터·학습
run cap01_dataset 'for s in train val test; do for c in angular_leaf_spot bean_rust healthy; do printf "%-6s %-18s %4s장\n" $s $c $(ls dataset/$s/$c | wc -l); done; done'
run cap01_dataset 'cat reports/data/dataset_check.json | head -30'
run cap02_model_dirs 'ls -la artifacts/beans_resnet18 artifacts/beans_resnet18_full'
run cap02_model_dirs 'grep MODEL_PATH .env'
run cap03_train_e0 'cat reports/evidence/train_log_head_only.txt | grep -v "slow image" | tail -25'
run cap04_train_e2 'cat reports/evidence/train_log_e2_full.txt | grep -v "slow image" | tail -25'
run cap05_test_eval 'cat reports/data/model_selection.md | sed -n 9,15p'
run cap05_test_eval 'cat reports/data/test_runs.log'
# 02 실행 구조
run cap06_runtime 'docker compose ps --format "table {{.Name}}\t{{.Image}}\t{{.Status}}"'
run cap06_runtime "ps -eo pid,args | grep -E '[u]vicorn main:app|[c]elery -A ai.celery_app' | grep -v tee | cut -c1-150"
run cap06_runtime 'docker compose exec -T redis redis-cli ping; curl -s http://127.0.0.1:8000/health; echo'
# 04 DB
run cap07_db_schema 'docker compose exec -T postgres psql -U vision_user -d vision_db -c "\d image_jobs"'
run cap08_db_rows 'docker compose exec -T postgres psql -U vision_user -d vision_db -c "SELECT id, status, model_id, top1_label, round(top1_score::numeric,4) AS score, inference_ms, cache_hit, left(coalesce(error_message,\x27\x27),40) AS error FROM image_jobs ORDER BY id;"'
run cap08_db_rows 'docker compose exec -T postgres psql -U vision_user -d vision_db -c "SELECT status, cache_hit, count(*) FROM image_jobs GROUP BY 1,2 ORDER BY 1,2;"'
# Redis 캐시
run cap09_redis_cache 'docker compose exec -T redis redis-cli -n 1 dbsize'
run cap09_redis_cache 'docker compose exec -T redis redis-cli -n 1 --scan --pattern "vision:classify:*" | head -5'
run cap09_redis_cache 'K=$(docker compose exec -T redis redis-cli -n 1 --scan --pattern "vision:classify:*" | head -1); docker compose exec -T redis redis-cli -n 1 ttl "$K"; docker compose exec -T redis redis-cli -n 1 get "$K" | cut -c1-200'
# 06 성능 원본
run cap10_timings 'cat reports/data/timings.csv'
# 07 테스트
run cap11_pytest 'cat reports/evidence/pytest_mock.txt'
run cap12_t10_worker_stopped 'cat reports/evidence/t10_t16_worker_stopped.txt | cut -c1-170'
run cap13_t15_redis_stopped 'cat reports/evidence/t15_redis_stopped.txt | cut -c1-170'
run cap14_worker_log 'grep -E "succeeded|raised|ready|Connected" reports/evidence/celery_worker_log.txt | head -22 | cut -c1-170'
run cap15_errors 'python -c "import json;d=json.load(open(\"reports/evidence/api_responses.json\"));[print(e[\"id\"],e[\"status\"],json.dumps(e[\"body\"],ensure_ascii=False)[:110]) for e in d[\"error_cases\"]]"'
# 개선 실험
run cap16_review_rule 'python scripts/review_rule.py apply --model artifacts/beans_resnet18_full --split test'

f=reports/evidence/screens/src/cap09_redis_cache.txt; rm -f $f
cd ~/kh-subject9-eval-beans || exit 1
P='user1@wsl:~/kh-subject9-eval-beans$'
IMG=dataset/val/healthy/$(ls dataset/val/healthy | sed -n 20p)
run() { { echo "$P $*"; bash -c "$*" 2>&1; echo; } >> $f; }
run 'docker compose exec -T redis redis-cli -n 1 dbsize'
run "curl -s -F image=@$IMG http://127.0.0.1:8000/api/sync/classify/ | python3 -c 'import sys,json;d=json.load(sys.stdin);print(\"1회차:\",d[\"top1\"],\"inference_ms=\",d[\"inference_ms\"],\"cache_hit=\",d[\"cache_hit\"])'"
run "curl -s -F image=@$IMG http://127.0.0.1:8000/api/sync/classify/ | python3 -c 'import sys,json;d=json.load(sys.stdin);print(\"2회차:\",d[\"top1\"],\"inference_ms=\",d[\"inference_ms\"],\"cache_hit=\",d[\"cache_hit\"])'"
run 'docker compose exec -T redis redis-cli -n 1 --scan --pattern "vision:classify:*"'
run "sha256sum $IMG"
run 'K=$(docker compose exec -T redis redis-cli -n 1 --scan --pattern "vision:classify:*" | head -1); echo "TTL(초):"; docker compose exec -T redis redis-cli -n 1 ttl "$K"'
run 'docker compose exec -T redis redis-cli -n 2 llen celery'

f=reports/evidence/screens/src/cap08_db_rows.txt; rm -f $f
cd ~/kh-subject9-eval-beans || exit 1
P='user1@wsl:~/kh-subject9-eval-beans$'
Q1="SELECT id, status, top1_label, round(top1_score::numeric,4) AS score, inference_ms, cache_hit, left(coalesce(error_message,''),38) AS error, to_char(created_at,'MM-DD HH24:MI:SS') AS created FROM image_jobs ORDER BY id;"
Q2="SELECT status, cache_hit, count(*) FROM image_jobs GROUP BY 1,2 ORDER BY 1,2;"
for q in "$Q1" "$Q2"; do
  { echo "$P docker compose exec postgres psql -U vision_user -d vision_db -c \"$q\""
    docker compose exec -T postgres psql -U vision_user -d vision_db -c "$q"; } >> $f 2>&1
done
