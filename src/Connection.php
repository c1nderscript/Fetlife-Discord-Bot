<?php
declare(strict_types=1);

namespace FetLife;

use RuntimeException;

class Connection implements ConnectionInterface
{
    private const BASE_URL = 'https://fetlife.com';

    private ?string $csrfToken = null;
    private string $cookieFile;

    public function __construct(?string $cookieFile = null)
    {
        $this->cookieFile = $cookieFile ?? tempnam(sys_get_temp_dir(), 'fl');
        register_shutdown_function(static function (string $file): void {
            if (file_exists($file)) {
                @unlink($file);
            }
        }, $this->cookieFile);
    }

    public function __destruct()
    {
        if (file_exists($this->cookieFile)) {
            @unlink($this->cookieFile);
        }
    }

    public function getCookieFile(): string
    {
        return $this->cookieFile;
    }

    public function logIn(string $nickname, string $password): string
    {
        $ch = curl_init(self::BASE_URL . '/users/sign_in');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_COOKIEFILE, $this->cookieFile);
        curl_setopt($ch, CURLOPT_COOKIEJAR, $this->cookieFile);
        $body = curl_exec($ch);
        if ($body === false) {
            throw new RuntimeException('Failed to load login page');
        }
        $this->csrfToken = $this->findCsrfToken($body);
        curl_close($ch);

        $postData = http_build_query([
            'user[login]' => $nickname,
            'user[password]' => $password,
            'user[otp_attempt]' => 'step_1',
            'authenticity_token' => $this->csrfToken,
            'utf8' => '✓',
        ]);

        return $this->post('/users/sign_in', $postData);
    }

    public function get(string $path): string
    {
        return $this->request($path, 'GET');
    }

    private function post(string $path, string $data): string
    {
        return $this->request($path, 'POST', $data);
    }

    private function request(string $path, string $method, string $data = ''): string
    {
        $ch = curl_init(self::BASE_URL . $path);
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        }
        curl_setopt($ch, CURLOPT_COOKIEFILE, $this->cookieFile);
        curl_setopt($ch, CURLOPT_COOKIEJAR, $this->cookieFile);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $body = curl_exec($ch);
        if ($body === false) {
            throw new RuntimeException('HTTP request failed');
        }
        $token = $this->findCsrfToken($body);
        if ($token !== null) {
            $this->csrfToken = $token;
        }
        curl_close($ch);
        return $body;
    }

    public function findUserId(string $html): ?int
    {
        if (preg_match('/FetLife\\.currentUser\\.id\\s*=\\s*(\\d+);/', $html, $m)) {
            return (int)$m[1];
        }
        if (preg_match('/var currentUserId\\s*=\\s*(\\d+)/', $html, $m)) {
            return (int)$m[1];
        }
        return null;
    }

    public function findUserNickname(string $html): ?string
    {
        if (preg_match('/<title>([-_A-Za-z0-9]+) - Kinksters - FetLife<\\/title>/', $html, $m)) {
            return $m[1];
        }
        return null;
    }

    private function findCsrfToken(string $html): ?string
    {
        if (preg_match('/<meta name=\"csrf-token\" content=\"([^\"]+)\"/', $html, $m)) {
            return html_entity_decode($m[1], ENT_COMPAT, 'UTF-8');
        }
        return null;
    }
}
