<?php
declare(strict_types=1);

namespace FetLife\Tests;

use FetLife\Connection;
use FetLife\User;
use PHPUnit\Framework\TestCase;

final class CookieCleanupTest extends TestCase
{
    public function testCookieFileRemovedAfterLoginAndUnset(): void
    {
        $conn = new class extends Connection {
            public function logIn(string $nickname, string $password): string
            {
                return '<script>FetLife.currentUser.id = 1;</script>';
            }
            public function get(string $path): string
            {
                return '';
            }
            public function findUserId(string $html): ?int
            {
                return 1;
            }
            public function findUserNickname(string $html): ?string
            {
                return 'tester';
            }
        };
        $path = $conn->getCookieFile();
        $user = new User('tester', 'secret', $conn);
        $user->logIn();
        unset($user, $conn);
        $this->assertFileDoesNotExist($path);
    }
}
