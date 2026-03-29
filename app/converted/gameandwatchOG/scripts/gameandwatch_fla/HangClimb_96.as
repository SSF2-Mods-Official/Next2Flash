package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class HangClimb_96 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function HangClimb_96()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 8, this.frame9, 12, this.frame13, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            this.self.playSound("gw_jump1");
        }

        internal function frame9():*
        {
            this.self.setXSpeed(6, false);
        }

        internal function frame13():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("snd_se_GW_Landing02");
            };
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

