package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class DTilt_86 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function DTilt_86()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 6, this.frame7, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady())
            {
            };
        }

        internal function frame4():*
        {
            this.self.playSound("gw_dtilt");
            this.self.attachEffect("global_dust_light");
        }

        internal function frame7():*
        {
            this.self.playSound("gw_ftilt01");
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

