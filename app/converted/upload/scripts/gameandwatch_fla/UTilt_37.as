package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class UTilt_37 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function UTilt_37()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 13, this.frame14, 18, this.frame19, 26, this.frame27);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady() && !this.self.isFacingRight())
            {
                this.self.stancePlayFrame("left");
            };
        }

        internal function frame6():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playSound("gw_ftilt02");
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }

        internal function frame19():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playSound("gw_ftilt02");
        }

        internal function frame27():*
        {
            this.self.endAttack();
        }


    }
}

