package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class HangClimb_164 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function HangClimb_164()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 8, this.frame9, 10, this.frame11, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            this.self.playSound("falcon_jumpS1");
        }

        internal function frame9():*
        {
            this.self.setXSpeed(7, false);
        }

        internal function frame11():*
        {
            this.self.playSound("falcon_footstep");
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}

