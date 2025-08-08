<?php
class FetLifeUserTest extends PHPUnit_Framework_TestCase {

    protected static $FL;

    public static function setUpBeforeClass () {
        $username = getenv('FETLIFE_USERNAME');
        $password = getenv('FETLIFE_PASSWORD');
        $proxyurl = getenv('FETLIFE_PROXYURL');
        if (!$username || !$password) {
            return;
        }
        self::$FL = new FetLifeUser($username, $password);
        if ('auto' === $proxyurl) {
            self::$FL->connection->setProxy('auto');
        } else if ($proxyurl) {
            $p = parse_url($proxyurl);
            self::$FL->connection->setProxy(
                "{$p['host']}:{$p['port']}",
                ('socks' === $p['scheme']) ? CURLPROXY_SOCKS5 : CURLPROXY_HTTP
            );
        }
    }

    protected function setUp(): void {
        if (!self::$FL) {
            $this->markTestSkipped('FetLife credentials not provided');
        }
    }

    public function testFoundUserId () {
        self::$FL->logIn();
        $this->assertNotEmpty(self::$FL->id);
    }

}
