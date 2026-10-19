
#!/bin/sh
# Purpose: Summarise a saved Campus Notice Board monitor log.
# Usage: ./scripts/summarise.sh evidence/t4-at-rest.log

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <monitor-log-file>" >&2
    exit 1
fi

LOG_FILE="$1"

if [ ! -f "$LOG_FILE" ]; then
    echo "Error: File not found: $LOG_FILE" >&2
    exit 1
fi

awk '
$2 == "OK" || $2 == "FAIL" {
    total++

    if (total == 1)
        first = $1

    last = $1

    if ($2 == "FAIL")
        failed++

    if ($2 == "OK") {
        if (match($0, /"version"[[:space:]]*:[[:space:]]*"[^"]+"/)) {
            field = substr($0, RSTART, RLENGTH)
            split(field, parts, "\"")
            versions[parts[4]]++
        } else {
            unknown++
        }
    }
}
END {
    print "===== Availability Summary ====="
    printf "Total requests: %d\n", total
    printf "Failed requests: %d\n", failed
    print "First timestamp: " (total ? first : "N/A")
    print "Last timestamp: " (total ? last : "N/A")

    print "Responses by version:"
    for (version in versions) {
        printf "  %s: %d\n", version, versions[version]
    }

    if (unknown > 0)
        printf "  Unknown version: %d\n", unknown

    print "================================"
}
' "$LOG_FILE"
