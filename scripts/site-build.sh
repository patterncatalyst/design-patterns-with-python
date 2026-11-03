#!/usr/bin/env bash
# Usage: scripts/site-build.sh [build|serve]
# Build (default) or serve the Jekyll site in a ruby container (Docker Engine).
# The host needs no Ruby. Gems install under /tmp inside the container and
# Gemfile.lock must come out unchanged.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

mode="${1:-build}"
image="ruby:4.0.9"

common=(
    --rm
    -u "$(id -u):$(id -g)"
    -e HOME=/tmp
    -e BUNDLE_PATH=/tmp/bundle
    -e BUNDLE_FROZEN=true
    -e JEKYLL_ENV=production
    -v "$PWD":/srv/site:Z
    -w /srv/site
)

case "$mode" in
    build)
        docker run "${common[@]}" "$image" \
            bash -c 'bundle install --quiet && bundle exec jekyll build'
        ;;
    serve)
        docker run "${common[@]}" -p 4000:4000 "$image" \
            bash -c 'bundle install --quiet && bundle exec jekyll serve --host 0.0.0.0 --port 4000'
        ;;
    *)
        echo "usage: $0 [build|serve]" >&2
        exit 2
        ;;
esac

git diff --quiet Gemfile.lock || {
    echo "site-build: Gemfile.lock changed during the build" >&2
    exit 1
}
echo "site-build: ok (Gemfile.lock unchanged)"
