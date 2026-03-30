package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class waterSpoutProj_147 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var newXSpeed:*;
        public var newYSpeed:*;
        public var character:*;

        public function waterSpoutProj_147()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 10, this.frame11, 12, this.frame13, 13, this.frame14, 19, this.frame20, 23, this.frame24);
        }

        public function toContinue(_arg_1:*):*
        {
            this.self.stancePlayFrame("continue");
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.toContinue);
        }

        public function toChibtinue(_arg_1:*):*
        {
            this.self.stancePlayFrame("chibtinue");
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toChibtinue);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toChibtinue);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toChibtinue);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.toChibtinue);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.newXSpeed = 0;
            this.newYSpeed = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.self.getMC().scaleX = 1.25;
                this.self.getMC().scaleY = 1.25;
                this.character = this.self.getOwner();
                this.newXSpeed = (0.55 * this.character.getXSpeed());
                this.newYSpeed = ((0.55 * this.character.getYSpeed()) + this.self.getProjectileStat("yspeed"));
                this.self.setXSpeed(this.newXSpeed, true);
                this.self.setYSpeed(this.newYSpeed);
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.toContinue);
            };
        }

        internal function frame7():*
        {
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
        }

        internal function frame11():*
        {
            this.self.destroy();
        }

        internal function frame13():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame14():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toChibtinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toChibtinue);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toChibtinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.toChibtinue);
            };
        }

        internal function frame20():*
        {
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
        }

        internal function frame24():*
        {
            this.self.destroy();
        }


    }
}

