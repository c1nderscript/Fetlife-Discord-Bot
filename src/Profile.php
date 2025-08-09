<?php
declare(strict_types=1);

namespace FetLife;

class Profile
{
    public function __construct(
        public string $nickname,
        public int $id
    ) {
    }
}
