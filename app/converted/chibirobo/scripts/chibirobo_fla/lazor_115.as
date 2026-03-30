package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class lazor_115 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var self:*;
        public var localBlaster:Number;
        public var character:*;

        public function lazor_115()
        {
            super();
            addFrameScript(0, this.frame1, 15, this.frame16, 29, this.frame30, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.localBlaster = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.self.destroy);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.self.destroy);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.destroy);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.self.destroy);
                this.localBlaster = this.character.getGlobalVariable("blasterAngle");
                if (!this.self.isFacingRight())
                {
                    this.localBlaster = (180 - this.localBlaster);
                };
                this.self.angleControl(24, this.localBlaster);
            };
        }

        internal function frame16():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame30():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame31():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.self.destroy);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.self.destroy);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.destroy);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.self.destroy);
                this.self.stancePlayFrame("loop");
            };
        }


    }
}

