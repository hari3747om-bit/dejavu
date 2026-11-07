"""Fake company history for the demo (Acme Shop, an online store)."""

INCIDENTS = [
    {
        "id": "INC-0101", "date": "2026-01-14T02:10:00Z", "service": "payments-service",
        "symptom": "p99 latency rose from 300ms to 4s; errors: 'redis.exceptions.ConnectionError: Too many connections'",
        "root_cause": "Redis connection pool exhausted right after deploy v2.31 (pool size left at 20)",
        "fix_worked": "Raised Redis pool size from 20 to 200 and redeployed config",
        "fix_failed": ["Rolled back to v2.30 (did NOT help, pool config is shared)", "Restarted pods (relief for 5 minutes only)"],
        "engineer": "Priya",
    },
    {
        "id": "INC-0118", "date": "2026-02-03T14:40:00Z", "service": "auth-gateway",
        "symptom": "Users cannot log in; 'x509: certificate has expired' in gateway logs",
        "root_cause": "Internal TLS certificate expired (90-day rotation missed)",
        "fix_worked": "Renewed certificate with cert-manager and restarted auth-gateway",
        "fix_failed": ["Clearing the session cache (unrelated)"],
        "engineer": "Rahul",
    },
    {
        "id": "INC-0127", "date": "2026-02-19T02:05:00Z", "service": "order-api",
        "symptom": "Orders time out at exactly 2 AM; DB error 'FATAL: remaining connection slots are reserved'",
        "root_cause": "Nightly analytics batch job starves DB connections",
        "fix_worked": "Moved batch job to the read replica and capped it at 10 connections",
        "fix_failed": ["Scaling order-api pods up (made it worse, more connections)"],
        "engineer": "Meera",
    },
    {
        "id": "INC-0140", "date": "2026-03-12T16:20:00Z", "service": "payments-service",
        "symptom": "Checkout slow, p99 3.5s, 'Too many connections' in Redis client logs after v2.34 rollout",
        "root_cause": "Redis pool exhaustion again after deploy; new release reset pool size to default",
        "fix_worked": "Set REDIS_POOL_SIZE=200 in the deploy template permanently",
        "fix_failed": ["Rollback did not help", "Increasing pod CPU (irrelevant)"],
        "engineer": "Priya",
    },
    {
        "id": "INC-0155", "date": "2026-04-02T09:30:00Z", "service": "inventory-sync",
        "symptom": "Stock counts out of date by hours; queue depth growing in 'inventory-events'",
        "root_cause": "Consumer crashed on a malformed supplier message (poison message) and kept retrying",
        "fix_worked": "Moved the poison message to the dead-letter queue and restarted the consumer",
        "fix_failed": ["Restart alone (consumer hit the same message again)"],
        "engineer": "Arjun",
    },
    {
        "id": "INC-0171", "date": "2026-05-08T03:50:00Z", "service": "notification-worker",
        "symptom": "Emails delayed 30+ minutes; SMTP provider returns 429 rate limit",
        "root_cause": "Marketing campaign sent 200k emails and exceeded the provider rate limit",
        "fix_worked": "Throttled the campaign queue to 50 emails/sec; transactional emails use a separate queue now",
        "fix_failed": ["Switching SMTP provider mid-incident (broke SPF records)"],
        "engineer": "Meera",
    },
    {
        "id": "INC-0188", "date": "2026-06-21T02:12:00Z", "service": "order-api",
        "symptom": "Order timeouts again around 2 AM; 'remaining connection slots are reserved'",
        "root_cause": "Nightly batch job again; the cap from INC-0127 was removed during a refactor",
        "fix_worked": "Restored the 10 connection cap on the batch job",
        "fix_failed": ["Restarting the DB (caused 4 minutes extra downtime)"],
        "engineer": "Arjun",
    },
    {
        "id": "INC-0203", "date": "2026-08-30T11:15:00Z", "service": "auth-gateway",
        "symptom": "Login failures for 20% of users; 'x509: certificate has expired' on one region only",
        "root_cause": "Certificate renewed in two regions but missed in ap-south",
        "fix_worked": "Renewed the ap-south certificate manually",
        "fix_failed": ["Restarting the gateway in all regions"],
        "engineer": "Rahul",
    },
]

TRIBAL_KNOWLEDGE = [
    ("Priya", "payments-service latency spikes are almost always the Redis connection pool after a deploy. Check REDIS_POOL_SIZE before anything else."),
    ("Meera", "Anything weird in order-api between 1 AM and 3 AM is the nightly analytics batch job. Look at DB connection counts first."),
    ("Rahul", "Our internal TLS certs expire every 90 days. If logins fail with x509 errors, check certificate expiry in every region."),
    ("Arjun", "inventory-sync restarts do not fix stuck queues. Look for a poison message and move it to the dead-letter queue."),
]

# Held back for the live demo (NOT seeded into memory)
DEMO_ALERTS = [
    {
        "id": "INC-0301", "service": "payments-service",
        "error": "p99 latency 4.2s after deploy v2.41. Logs: 'redis.exceptions.ConnectionError: Too many connections'",
    },
    {
        "id": "INC-0302", "service": "order-api",
        "error": "Order requests timing out at 02:03 AM. DB: 'remaining connection slots are reserved for non-replication superuser connections'",
    },
]


def incident_to_text(i):
    failed = "; ".join(i["fix_failed"]) if i["fix_failed"] else "none recorded"
    return (
        f"Incident {i['id']} on {i['date'][:10]} in {i['service']}. "
        f"Symptom: {i['symptom']}. Root cause: {i['root_cause']}. "
        f"Fix that WORKED: {i['fix_worked']}. "
        f"Fixes that did NOT work: {failed}. Resolved by {i['engineer']}."
    )
