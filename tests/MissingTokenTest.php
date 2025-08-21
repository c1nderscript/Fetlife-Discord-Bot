<?php
declare(strict_types=1);

namespace FetLife\Tests;

use PHPUnit\Framework\TestCase;

final class MissingTokenTest extends TestCase
{
    public function testMissingTokenReturns500(): void
    {
        unset($_ENV['ADAPTER_AUTH_TOKEN']);
        $_SERVER['REQUEST_METHOD'] = 'GET';
        $_SERVER['REQUEST_URI'] = '/login';
        ob_start();
        include __DIR__ . '/../adapter/public/index.php';
        $output = ob_get_clean();
        $this->assertStringContainsString('server misconfigured', $output);
    }
}
