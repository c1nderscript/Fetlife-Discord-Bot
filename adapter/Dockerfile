FROM php:8.2-cli

WORKDIR /app

# Install composer
RUN apt-get update \
    && apt-get install -y --no-install-recommends git unzip \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Install PHP dependencies
COPY composer.json composer.lock ./
RUN composer install --no-interaction --prefer-dist

# Copy source and public files
COPY src/ src/
COPY adapter/public/ public/

EXPOSE 8000
CMD ["php", "-S", "0.0.0.0:8000", "-t", "public"]
