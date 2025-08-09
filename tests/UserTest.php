<?php
declare(strict_types=1);

namespace FetLife\Tests;

use FetLife\User;
use FetLife\Profile;
use FetLife\Event;
use FetLife\ConnectionInterface;
use PHPUnit\Framework\TestCase;

class FakeConnection implements ConnectionInterface
{
    public function logIn(string $nickname, string $password): string
    {
        return '<script>FetLife.currentUser.id = 99;</script>';
    }

    public function get(string $path): string
    {
        if ($path === '/users/99') {
            return '<title>tester - Kinksters - FetLife</title>';
        }
        if ($path === '/location/test/events') {
            return '<ul class="event_listings"><li><a href="/events/1">Test Event</a><div>2024-01-01 18:00</div><div>Club X</div></li></ul>';
        }
        return '';
    }

    public function findUserId(string $html): ?int
    {
        if (preg_match('/FetLife\\.currentUser\\.id = (\\d+)/', $html, $m)) {
            return (int) $m[1];
        }
        return null;
    }

    public function findUserNickname(string $html): ?string
    {
        if (preg_match('/<title>([^<]+) - Kinksters - FetLife<\\/title>/', $html, $m)) {
            return $m[1];
        }
        return null;
    }
}

final class UserTest extends TestCase
{
    public function testLoginSetsId(): void
    {
        $user = new User('tester', 'secret', new FakeConnection());
        $user->logIn();
        $this->assertSame(99, $user->id);
    }

    public function testGetUserProfile(): void
    {
        $user = new User('tester', 'secret', new FakeConnection());
        $user->logIn();
        $profile = $user->getUserProfile();
        $this->assertInstanceOf(Profile::class, $profile);
        $this->assertSame('tester', $profile->nickname);
    }

    public function testGetUpcomingEvents(): void
    {
        $user = new User('tester', 'secret', new FakeConnection());
        $user->logIn();
        $events = $user->getUpcomingEventsInLocation('location/test');
        $this->assertCount(1, $events);
        $this->assertInstanceOf(Event::class, $events[0]);
        $this->assertSame('Test Event', $events[0]->title);
    }
}
