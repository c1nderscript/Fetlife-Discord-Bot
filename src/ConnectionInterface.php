<?php
declare(strict_types=1);

namespace FetLife;

interface ConnectionInterface
{
    /**
     * Perform login and return response body.
     */
    public function logIn(string $nickname, string $password): string;

    /**
     * Execute a GET request and return response body.
     */
    public function get(string $path): string;

    /**
     * Extract user id from HTML.
     */
    public function findUserId(string $html): ?int;

    /**
     * Extract nickname from profile HTML.
     */
    public function findUserNickname(string $html): ?string;
}
