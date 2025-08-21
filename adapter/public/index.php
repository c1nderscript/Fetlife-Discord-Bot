<?php
require __DIR__ . '/../vendor/autoload.php';

use Dotenv\Dotenv;
use Slim\Factory\AppFactory;
use Slim\Psr7\Response;
use FetLife\User as FetLifeUser;
use FetLife\Connection;

if (session_status() === PHP_SESSION_NONE) {
    @session_start();
}
if (!isset($_SESSION['accounts'])) {
    $_SESSION['accounts'] = [];
}

$dotenv = Dotenv::createImmutable(__DIR__ . '/..');
$dotenv->safeLoad();

$app = AppFactory::create();

$token = $_ENV['ADAPTER_AUTH_TOKEN'] ?? null;
if (!$token) {
    log_json('critical', 'missing ADAPTER_AUTH_TOKEN');
}

$app->add(function ($request, $handler) use ($token) {
    $path = $request->getUri()->getPath();
    if (in_array($path, ['/healthz', '/metrics', '/openapi.yaml'])) {
        return $handler->handle($request);
    }
    if (!$token) {
        $response = new Response();
        $response->getBody()->write(json_encode(['error' => 'server misconfigured']));
        return $response->withStatus(500)->withHeader('Content-Type', 'application/json');
    }
    $auth = $request->getHeaderLine('Authorization');
    if ($auth !== "Bearer $token") {
        $response = new Response();
        $response->getBody()->write(json_encode(['error' => 'unauthorized']));
        return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
    }
    return $handler->handle($request);
});

$metrics = ['fetlife_requests_total' => 0];

function metric_inc($name)
{
    global $metrics;
    $metrics[$name] = ($metrics[$name] ?? 0) + 1;
}

function metrics_text()
{
    global $metrics;
    $lines = [];
    foreach ($metrics as $k => $v) {
        $lines[] = "# TYPE $k counter";
        $lines[] = "$k $v";
    }
    return implode("\n", $lines) . "\n";
}

function log_json($level, $message, $context = [])
{
    $data = array_merge(['level' => $level, 'message' => $message], $context);
    error_log(json_encode($data));
}

function getAccountId($request)
{
    $hdr = $request->getHeaderLine('X-Account-ID');
    $params = $request->getQueryParams();
    return $hdr ?: ($params['account'] ?? 'default');
}

function getUser($accountId)
{
    if (!isset($_SESSION['accounts'][$accountId])) {
        return null;
    }
    $data = $_SESSION['accounts'][$accountId];
    $cookieFile = tempnam(sys_get_temp_dir(), 'fl');
    register_shutdown_function('unlink', $cookieFile);
    if (isset($data['cookie'])) {
        file_put_contents($cookieFile, $data['cookie']);
    }
    $user = new FetLifeUser($data['nickname'], '');
    $user->id = $data['id'];
    $user->connection = new Connection($cookieFile);
    return $user;
}

$app->post('/login', function ($request, $response) {
    log_json('info', 'login');
    $acct = getAccountId($request);
    $params = (array) $request->getParsedBody();
    $username = $params['username'] ?? ($_ENV['FETLIFE_USERNAME'] ?? null);
    $password = $params['password'] ?? ($_ENV['FETLIFE_PASSWORD'] ?? null);
    if (!$username || !$password) {
        $response->getBody()->write(json_encode(['error' => 'missing credentials']));
        return $response->withStatus(400)->withHeader('Content-Type', 'application/json');
    }
    $cookieFile = tempnam(sys_get_temp_dir(), 'fl');
    register_shutdown_function('unlink', $cookieFile);
    $user = new FetLifeUser($username, $password, new Connection($cookieFile));
    if (!empty($_ENV['FETLIFE_PROXY'])) {
        $type = $_ENV['FETLIFE_PROXY_TYPE'] ?? CURLPROXY_HTTP;
        if (is_string($type) && defined($type)) {
            $type = constant($type);
        }
        $user->connection->setProxy($_ENV['FETLIFE_PROXY'], $type);
    }
    metric_inc('fetlife_requests_total');
    if ($user->logIn()) {
        $_SESSION['accounts'][$acct] = [
            'id' => $user->id,
            'nickname' => $username,
            'cookie' => file_get_contents($cookieFile) ?: '',
        ];
        session_regenerate_id(true);
        $response->getBody()->write(json_encode(['status' => 'ok']));
        return $response->withHeader('Content-Type', 'application/json');
    }
    $response->getBody()->write(json_encode(['error' => 'login failed']));
    return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
});

$app->get('/events', function ($request, $response) {
    $acct = getAccountId($request);
    $user = getUser($acct);
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
    log_json('info', 'events', ['location' => $location]);
    metric_inc('fetlife_requests_total');
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
    $acct = getAccountId($request);
    $user = getUser($acct);
    if (!$user) {
        $response->getBody()->write(json_encode(['error' => 'not authenticated']));
        return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
    }
    log_json('info', 'event_detail', ['id' => $args['id']]);
    metric_inc('fetlife_requests_total');
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

$app->get('/events/{id}/attendees', function ($request, $response, $args) {
    $acct = getAccountId($request);
    $user = getUser($acct);
    if (!$user) {
        $response->getBody()->write(json_encode(['error' => 'not authenticated']));
        return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
    }
    $params = $request->getQueryParams();
    $pages = $params['pages'] ?? 1;
    log_json('info', 'event_attendees', ['id' => $args['id'], 'pages' => $pages]);
    metric_inc('fetlife_requests_total');
    $event = $user->getEventById($args['id']);
    $event->populate($pages);
    $list = [];
    $sets = ['going' => 'going', 'maybegoing' => 'maybe', 'notgoing' => 'not_going'];
    foreach ($sets as $prop => $status) {
        if (!empty($event->$prop) && is_array($event->$prop)) {
            foreach ($event->$prop as $profile) {
                $list[] = [
                    'id' => $profile->id,
                    'nickname' => $profile->nickname,
                    'status' => $status,
                    'comment' => $profile->rsvp_comment ?? null,
                ];
            }
        }
    }
    $response->getBody()->write(json_encode($list));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->get('/users/{id}/writings', function ($request, $response, $args) {
    $acct = getAccountId($request);
    $user = getUser($acct);
    if (!$user) {
        $response->getBody()->write(json_encode(['error' => 'not authenticated']));
        return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
    }
    log_json('info', 'writings', ['id' => $args['id']]);
    metric_inc('fetlife_requests_total');
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
    $acct = getAccountId($request);
    $user = getUser($acct);
    if (!$user) {
        $response->getBody()->write(json_encode(['error' => 'not authenticated']));
        return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
    }
    $id = $args['id'];
    log_json('info', 'group_posts', ['id' => $id]);
    metric_inc('fetlife_requests_total');
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

$app->get('/messages', function ($request, $response) {
    $acct = getAccountId($request);
    $user = getUser($acct);
    if (!$user) {
        $response->getBody()->write(json_encode(['error' => 'not authenticated']));
        return $response->withStatus(401)->withHeader('Content-Type', 'application/json');
    }
    log_json('info', 'messages');
    metric_inc('fetlife_requests_total');
    $res = $user->connection->doHttpGet('/conversations');
    $doc = new DOMDocument();
    @$doc->loadHTML($res['body']);
    $nodes = $user->doXPathQuery('//*[contains(@class, "conversation__message")]', $doc);
    $messages = [];
    foreach ($nodes as $node) {
        $a = $node->getElementsByTagName('a')->item(0);
        $link = $a ? $a->getAttribute('href') : '';
        $id = $user->parseIdFromUrl($link);
        $senderEl = $node->getElementsByTagName('span')->item(0);
        $sender = trim($senderEl ? $senderEl->textContent : '');
        $timeEl = $node->getElementsByTagName('time')->item(0);
        $messages[] = [
            'id' => $id,
            'sender' => $sender,
            'text' => trim($node->textContent),
            'sent' => $timeEl ? $timeEl->getAttribute('datetime') : null,
        ];
    }
    $response->getBody()->write(json_encode($messages));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->get('/healthz', function ($request, $response) {
    $response->getBody()->write(json_encode(['status' => 'ok']));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->get('/metrics', function ($request, $response) {
    $response->getBody()->write(metrics_text());
    return $response->withHeader('Content-Type', 'text/plain; version=0.0.4');
});

$app->get('/openapi.yaml', function ($request, $response) {
    $spec = file_get_contents(__DIR__ . '/../openapi.yaml');
    $response->getBody()->write($spec);
    return $response->withHeader('Content-Type', 'application/yaml');
});

$app->run();
