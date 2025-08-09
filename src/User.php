<?php
declare(strict_types=1);

namespace FetLife;

use RuntimeException;

class User
{
    public string $nickname;
    public string $password;
    public ?int $id = null;
    public ConnectionInterface $connection;

    public function __construct(string $nickname, string $password, ?ConnectionInterface $connection = null)
    {
        $this->nickname = $nickname;
        $this->password = $password;
        $this->connection = $connection ?? new Connection();
    }

    public function logIn(): void
    {
        $html = $this->connection->logIn($this->nickname, $this->password);
        $id = $this->connection->findUserId($html);
        if ($id === null) {
            throw new RuntimeException('Unable to log in');
        }
        $this->id = $id;
    }

    public function getUserProfile(string|int|null $who = null): Profile
    {
        $id = $this->resolveWho($who);
        $html = $this->connection->get("/users/$id");
        $nickname = $this->connection->findUserNickname($html);
        if ($nickname === null) {
            throw new RuntimeException('Profile not found');
        }
        return new Profile($nickname, $id);
    }

    public function getUpcomingEventsInLocation(string $locStr, int $pages = 0): array
    {
        return $this->getEventsInListing("/$locStr/events", $pages);
    }

    private function getEventsInListing(string $urlBase, int $pages): array
    {
        $html = $this->connection->get($urlBase);
        $doc = new \DOMDocument();
        @$doc->loadHTML($html);
        $xpath = new \DOMXPath($doc);
        $entries = $xpath->query('//ul[contains(@class,"event_listings")]/li');
        $events = [];
        foreach ($entries as $entry) {
            $a = $entry->getElementsByTagName('a')->item(0);
            $url = $a->getAttribute('href');
            $id = (int) current(array_reverse(explode('/', $url)));
            $title = trim($a->textContent);
            $time = $entry->getElementsByTagName('div')->item(0)->textContent;
            $venue = $entry->getElementsByTagName('div')->item(1)->textContent;
            $events[] = new Event($id, $title, $time, $venue);
        }
        return $events;
    }

    private function resolveWho(string|int|null $who): int
    {
        if ($who === null) {
            if ($this->id === null) {
                throw new RuntimeException('User id not set');
            }
            return $this->id;
        }
        if (is_int($who)) {
            return $who;
        }
        if (ctype_digit($who)) {
            return (int) $who;
        }
        throw new RuntimeException('Resolving nicknames not implemented');
    }
}
