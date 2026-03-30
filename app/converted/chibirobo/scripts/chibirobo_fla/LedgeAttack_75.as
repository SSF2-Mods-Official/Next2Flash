package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeAttack_75 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function LedgeAttack_75()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 9, this.frame10, 10, this.frame11, 11, this.frame12, 12, this.frame13, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame4():*
        {
            this.self.playSound("chibi_LedgeClimb");
        }

        internal function frame10():*
        {
            this.self.setXSpeed(10, false);
        }

        internal function frame11():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame12():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame13():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

