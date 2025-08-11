# syntax=docker/dockerfile:1
FROM php:8.2-cli@sha256:304cfb487bbe9b2ce5a933f6e5848e0248bff1fbb0d5ee36cec845f4a34f4fb1 AS builder

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git unzip \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

COPY composer.json composer.lock ./
RUN composer install --no-interaction --prefer-dist --no-dev

FROM php:8.2-cli@sha256:304cfb487bbe9b2ce5a933f6e5848e0248bff1fbb0d5ee36cec845f4a34f4fb1

WORKDIR /app

COPY --from=builder /app/vendor ./vendor
COPY src/ src/
COPY adapter/public/ public/

EXPOSE 8000
CMD ["php", "-S", "0.0.0.0:8000", "-t", "public"]
