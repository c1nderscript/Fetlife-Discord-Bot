<?php
require __DIR__ . '/../vendor/autoload.php';

use Dotenv\Dotenv;
use Slim\Factory\AppFactory;

session_start();

$dotenv = Dotenv::createImmutable(__DIR__ . '/..');
$dotenv->safeLoad();

$app = AppFactory::create();

function getUser()
{
    return isset($_SESSION['fetlife_user']) ? unserialize($_SESSION['fetlife_user']) : null;
}

$app->post('/login', function ($request, $response) {
    $params = (array) $request->getParsedBody();
    $username = $params['username'] ?? ($_ENV['FETLIFE_USERNAME'] ?? null);
    $password = $params['password'] ?? ($_ENV['FETLIFE_PASSWORD'] ?? null);
    if (!$username || !$password) {
        $response->getBody()->write(json_encode(['error' => 'missing credentials']));
        return $response->withStatus(400)->withHeader('Content-Type', 'application/json');
    }
    $user = new FetLifeUser($username, $password);
    if (!empty($_ENV['FETLIFE_PROXY'])) {
        $type = $_ENV['FETLIFE_PROXY_TYPE'] ?? CURLPROXY_HTTP;
        if (is_string($type) && defined($type)) {
            $type = constant($type);
        }
        $user->connection->setProxy($_ENV['FETLIFE_PROXY'], $type);
    }
    if ($user->logIn()) {
        $_SESSION['fetlife_user'] = serialize($user);
        $response->getBody()->write(json_encode(['status' => 'ok']));
        return $response->withHeader('Content-Type', 'application/json');
    }
    $response->getBody()->write(json_encode(['error' => 'login failed']));
    return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
});

$app->get('/events', function ($request, $response) {
    $user = getUser();
    if (!$user) {
        $response->getBody()->write(json_encode(['error' => 'not authenticated']));
        return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
    }
    $params = $request->getQueryParams();
    $location = $params['location'] ?? null;
    if (!$location) {
        $response->getBody()->write(json_encode(['error' => 'missing location']));
        return $response->withStatus(400)->withHeader('Content-Type', 'application/json');
    }
    $events = $user->getUpcomingEventsInLocation($location, 1);
    $data = [];
    foreach ($events as $node) {
        $linkEl = $node->getElementsByTagName('a')->item(0);
        $link = $linkEl ? $linkEl->getAttribute('href') : '';
        $data[] = [
            'id' => $user->parseIdFromUrl($link),
            'title' => trim($node->getElementsByTagName('h2')->item(0)->textContent ?? ''),
            'link' => FetLife::base_url . $link,
            'time' => ($node->getElementsByTagName('time')->item(0)->getAttribute('datetime') ?? null)
        ];
    }
    $response->getBody()->write(json_encode($data));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->get('/events/{id}', function ($request, $response, $args) {
    $user = getUser();
    if (!$user) {
        $response->getBody()->write(json_encode(['error' => 'not authenticated']));
        return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
    }
    $event = $user->getEventById($args['id']);
    $data = [
        'id' => $event->id,
        'title' => $event->title,
        'link' => $event->getPermalink(),
        'start' => $event->dtstart,
        'end' => $event->dtend,
    ];
    $response->getBody()->write(json_encode($data));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->get('/users/{id}/writings', function ($request, $response, $args) {
    $user = getUser();
    if (!$user) {
        $response->getBody()->write(json_encode(['error' => 'not authenticated']));
        return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
    }
    $writings = $user->getWritingsOf($args['id']);
    $data = [];
    foreach ($writings as $w) {
        $data[] = [
            'id' => $w->id,
            'title' => $w->title,
            'link' => $w->getPermalink(),
            'published' => $w->dt_published,
        ];
    }
    $response->getBody()->write(json_encode($data));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->get('/groups/{id}/posts', function ($request, $response, $args) {
    $user = getUser();
    if (!$user) {
        $response->getBody()->write(json_encode(['error' => 'not authenticated']));
        return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
    }
    $id = $args['id'];
    $res = $user->connection->doHttpGet("/groups/$id/group_posts");
    $doc = new DOMDocument();
    @$doc->loadHTML($res['body']);
    $nodes = $user->doXPathQuery('//*[contains(@class, "group_post")]', $doc);
    $posts = [];
    foreach ($nodes as $node) {
        $a = $node->getElementsByTagName('a')->item(0);
        $link = $a ? $a->getAttribute('href') : '';
        $timeEl = $node->getElementsByTagName('time')->item(0);
        $posts[] = [
            'id' => $user->parseIdFromUrl($link),
            'title' => trim($a ? $a->textContent : ''),
            'link' => FetLife::base_url . $link,
            'published' => $timeEl ? $timeEl->getAttribute('datetime') : null,
        ];
    }
    $response->getBody()->write(json_encode($posts));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->run();
