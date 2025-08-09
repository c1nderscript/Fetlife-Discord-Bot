<?php
declare(strict_types=1);

namespace FetLife;

class Event
{
    public function __construct(
        public int $id,
        public string $title,
        public string $dtstart,
        public string $venue
    ) {
    }
}
