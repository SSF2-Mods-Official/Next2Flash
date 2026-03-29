package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class HangRoll_165 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function HangRoll_165()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 8, this.frame9, 18, this.frame19, 19, this.frame20, 24, this.frame25);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            this.self.playSound("falcon_jumpS1");
        }

        internal function frame9():*
        {
            this.self.playSound("cfalcon_run_start");
        }

        internal function frame19():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame20():*
        {
            if (this.self.getMetalStatus())
            {
                SSF2API.playSound("metal_step_m1");
            }
            else
            {
                SSF2API.playSound("falcon_footstep");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

