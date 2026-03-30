package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeClimb_223 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function LedgeClimb_223()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 9, this.frame10, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame4():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_jump01");
        }

        internal function frame10():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step02");
            };
            this.self.setXSpeed(7, false);
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

