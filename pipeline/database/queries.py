"""
queries.py
----------
All raw SQL queries used by the AI pipeline database layer.

Design rules:
  - Every query is a module-level string constant — no query string
    construction anywhere else in the code (prevents SQL injection).
  - Parameterized with %s placeholders (psycopg2 style).
  - Grouped by domain: Missing Persons, Cameras, Detection Logs.
  - Queries are READ-ONLY from the pipeline's perspective; writes are
    performed only for detection_logs (the pipeline is a consumer of
    persons and cameras, not a writer).
"""


# =============================================================================
# Missing Persons
# =============================================================================

GET_ALL_MISSING_PERSONS = """
SELECT
    p.id,
    p.name,
    p.age,
    p.gender,
    p.status,
    p.last_seen_location,
    p.last_seen_date,
    p.description,
    p.contact_name,
    p.contact_phone,
    p.contact_email,
    p.created_at,
    p.updated_at,
    COALESCE(
        json_agg(
            json_build_object(
                'id',        pi.id,
                'image_url', pi.image_url,
                'is_primary', pi.is_primary
            ) ORDER BY pi.is_primary DESC, pi.id
        ) FILTER (WHERE pi.id IS NOT NULL),
        '[]'
    ) AS images
FROM missing_persons p
LEFT JOIN person_images pi ON pi.person_id = p.id
WHERE p.status != 'found'
GROUP BY p.id
ORDER BY p.created_at DESC;
"""

GET_MISSING_PERSON_BY_ID = """
SELECT
    p.id,
    p.name,
    p.age,
    p.gender,
    p.status,
    p.last_seen_location,
    p.last_seen_date,
    p.description,
    p.contact_name,
    p.contact_phone,
    p.contact_email,
    p.created_at,
    p.updated_at,
    COALESCE(
        json_agg(
            json_build_object(
                'id',        pi.id,
                'image_url', pi.image_url,
                'is_primary', pi.is_primary
            ) ORDER BY pi.is_primary DESC, pi.id
        ) FILTER (WHERE pi.id IS NOT NULL),
        '[]'
    ) AS images
FROM missing_persons p
LEFT JOIN person_images pi ON pi.person_id = p.id
WHERE p.id = %s
GROUP BY p.id;
"""

GET_PERSON_IMAGE_PATHS = """
SELECT
    pi.id,
    pi.image_url,
    pi.is_primary
FROM person_images pi
WHERE pi.person_id = %s
ORDER BY pi.is_primary DESC, pi.id;
"""

GET_MISSING_PERSONS_PAGINATED = """
SELECT
    p.id,
    p.name,
    p.age,
    p.gender,
    p.status,
    p.last_seen_location,
    p.last_seen_date,
    p.description,
    p.created_at
FROM missing_persons p
WHERE p.status != 'found'
ORDER BY p.created_at DESC
LIMIT %s OFFSET %s;
"""

COUNT_ACTIVE_MISSING_PERSONS = """
SELECT COUNT(*) AS total
FROM missing_persons
WHERE status != 'found';
"""


# =============================================================================
# Cameras
# =============================================================================

GET_ALL_CAMERAS = """
SELECT
    c.id,
    c.name,
    c.location,
    c.stream_url,
    c.is_active,
    c.latitude,
    c.longitude,
    c.created_at,
    c.updated_at
FROM cameras c
ORDER BY c.name;
"""

GET_CAMERA_BY_ID = """
SELECT
    c.id,
    c.name,
    c.location,
    c.stream_url,
    c.is_active,
    c.latitude,
    c.longitude,
    c.created_at,
    c.updated_at
FROM cameras c
WHERE c.id = %s;
"""

GET_ACTIVE_CAMERAS = """
SELECT
    c.id,
    c.name,
    c.location,
    c.stream_url,
    c.latitude,
    c.longitude
FROM cameras c
WHERE c.is_active = TRUE
ORDER BY c.name;
"""


# =============================================================================
# Detection Logs
# =============================================================================

INSERT_DETECTION_LOG = """
INSERT INTO detection_logs (
    person_id,
    camera_id,
    similarity_score,
    bounding_box,
    detected_at,
    frame_path,
    track_id
)
VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s)
RETURNING id;
"""

GET_DETECTION_LOGS_BY_PERSON = """
SELECT
    dl.id,
    dl.person_id,
    dl.camera_id,
    c.name          AS camera_name,
    c.location      AS camera_location,
    dl.similarity_score,
    dl.bounding_box,
    dl.detected_at,
    dl.frame_path,
    dl.track_id
FROM detection_logs dl
JOIN cameras c ON c.id = dl.camera_id
WHERE dl.person_id = %s
ORDER BY dl.detected_at DESC
LIMIT %s;
"""

GET_DETECTION_LOGS_BY_CAMERA = """
SELECT
    dl.id,
    dl.person_id,
    dl.camera_id,
    p.name          AS person_name,
    dl.similarity_score,
    dl.bounding_box,
    dl.detected_at,
    dl.frame_path,
    dl.track_id
FROM detection_logs dl
JOIN missing_persons p ON p.id = dl.person_id
WHERE dl.camera_id = %s
ORDER BY dl.detected_at DESC
LIMIT %s;
"""

GET_RECENT_DETECTIONS = """
SELECT
    dl.id,
    dl.person_id,
    p.name          AS person_name,
    dl.camera_id,
    c.name          AS camera_name,
    c.location      AS camera_location,
    dl.similarity_score,
    dl.bounding_box,
    dl.detected_at,
    dl.track_id
FROM detection_logs dl
JOIN missing_persons  p ON p.id = dl.person_id
JOIN cameras          c ON c.id = dl.camera_id
ORDER BY dl.detected_at DESC
LIMIT %s;
"""

GET_DETECTION_LOG_BY_ID = """
SELECT
    dl.id,
    dl.person_id,
    dl.camera_id,
    dl.similarity_score,
    dl.bounding_box,
    dl.detected_at,
    dl.frame_path,
    dl.track_id
FROM detection_logs dl
WHERE dl.id = %s;
"""

COUNT_DETECTIONS_FOR_PERSON_TODAY = """
SELECT COUNT(*) AS total
FROM detection_logs
WHERE person_id = %s
  AND detected_at >= CURRENT_DATE;
"""
